import json
import time
import xlrd
import requests
import lxml.html
from io import BytesIO
from zipfile import ZipFile
from django.utils import timezone
from catalog.models import *
from project.models import Log


class Runner:


	def __init__(self):

		self.name  = 'Axsoft'
		self.alias = 'axoft'
		self.count = {
			'product' : 0,
			'party'   : 0}

		# Фиксируем время старта
		self.start_time = timezone.now()

		# Поставщик
		self.distributor = Distributor.objects.take(
			alias = self.alias,
			name  = self.name)

		# Загрузчик
		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = self.distributor)

		# На заказ
		self.on_order = Stock.objects.take(
			alias             = self.alias + '-on-order',
			name              = self.name + ': на заказ',
			delivery_time_min = 10,
			delivery_time_max = 40,
			distributor       = self.distributor)

		# Единица измерения
		self.default_unit = Unit.objects.take(alias = 'pcs', name = 'шт.')

		# Тип цен
		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')
		self.rp = PriceType.objects.take(alias = 'RP', name = 'Розничная цена')

		# Валюты
		self.rub = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  = 1)
		self.usd = Currency.objects.take(
			alias     = 'USD',
			name      = '$',
			full_name = 'US Dollar',
			rate      = 60,
			quantity  = 1)
		self.eur = Currency.objects.take(
			alias     = 'EUR',
			name      = 'EUR',
			full_name = 'Euro',
			rate      = 80,
			quantity  = 1)

		# Используемые ссылки
		self.urls = {
			'start'         : 'http://axoft.ru/',
			'login'         : 'http://axoft.ru/',
			'vendors'       : 'http://axoft.ru/vendors/',
			'search_vendor' : '/vendors/',
			'search_price'  : '/pricelists/download.php?',
			'prefix'        : 'http://axoft.ru',
		}

		# Сессия
		self.s = requests.Session()
		self.cookie = None


	def run(self):

		# Авторизуемся
		if not self.login():
			return False

		# Получаем список производителей и ссылок на их прайс-листы
		prices = self.getPrices()

		# Проходим по каждому прайс-листу
		for n, price in enumerate(prices):

			print("Прайс-лист {} из {}: {}".format(
				n + 1,
				len(prices),
				price['name']))

			# Синоним производителя
			vendor_synonym = VendorSynonym.objects.take(
				name        = price['name'],
				updater     = self.updater,
				distributor = self.distributor)

			if vendor_synonym.vendor:
				data = self.getData(price['url'], price['name'])
				if data:
					self.parsePrice(data, vendor_synonym.vendor)
			else:
				print('Производитель не привязан.')

		# Чистим устаревшие партии
		Party.objects.clear(stock = self.on_order, time = self.start_time)

		Log.objects.add(
			subject     = "catalog.updater.{}".format(self.updater.alias),
			channel     = "info",
			title       = "Updated",
			description = "Обработано продуктов: {} шт.\n Обработано партий: {} шт.".format(self.count['product'], self.count['party']))

		return True


	def login(self):

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			Log.objects.add(
				subject     = "catalog.updater.{}".format(self.updater.alias),
				channel     = "error",
				title       = "login error",
				description = "Проверьте параметры авторизации. Кажется их нет.")
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False

		# Получаем куки
		try:
			r = self.s.get(self.urls['start'], timeout = 30.0)
			self.cookies = r.cookies
		except requests.exceptions.Timeout:
			Log.objects.add(
				subject     = "catalog.updater.{}".format(self.updater.alias),
				channel     = "error",
				title       = "requests.exceptions.Timeout",
				description = "Превышение интервала ожидания загрузки.")
			return False

		# Авторизуемся
		try:
			payload = {
				'backurl'       : '/',
				'AUTH_FORM'     : 'Y',
				'TYPE'          : 'AUTH',
				'IS_POPUP'      : '1',
				'USER_LOGIN'    : self.updater.login,
				'USER_PASSWORD' : self.updater.password,
				'Login'         : 'Вход для партнеров'}
			r = self.s.post(
				self.urls['login'],
				cookies         = self.cookies,
				data            = payload,
				allow_redirects = True,
				timeout         = 30.0)
			self.cookies = r.cookies
		except requests.exceptions.Timeout:
			Log.objects.add(
				subject     = "catalog.updater.{}".format(self.updater.alias),
				channel     = "error",
				title       = "requests.exceptions.Timeout",
				description = "Превышение интервала ожидания авторизации.")
			return False

		return True


	def getPrices(self):

		vendors = []
		prices  = []

		# Загружаем список производителей
		try:
			r = self.s.get(
				self.urls['vendors'],
				cookies         = self.cookies,
				allow_redirects = True,
				timeout         = 30.0)
			self.cookies = r.cookies
		except requests.exceptions.Timeout:
			Log.objects.add(
				subject     = "catalog.updater.{}".format(self.updater.alias),
				channel     = "error",
				title       = "requests.exceptions.Timeout",
				description = "Превышение интервала ожидания загрузки списка производителей.")
			return False

		# Проходим по всем ссылкам
		tree = lxml.html.fromstring(r.text)
		links = tree.xpath('//a')

		# Выбираем ссылкки на страницы производителей
		for link in links:

			vendor = {}
			vendor['name'] = link.text
			vendor['url']  = '{}{}'.format(self.urls['prefix'], link.get('href'))

			if (self.urls['search_vendor'] in vendor['url']):
				vendors.append(vendor)

		print("Обнаружил страниц производителей: {} шт.".format(len(vendors)))

		# Проходим по всем страницам производителям
		for n, vendor in enumerate(vendors):

			try:
				r = self.s.get(
					vendor['url'],
					cookies         = self.cookies,
					allow_redirects = True,
					timeout         = 30.0)
				self.cookies = r.cookies
			except requests.exceptions.Timeout:
				Log.objects.add(
					subject     = "catalog.updater.{}".format(self.updater.alias),
					channel     = "error",
					title       = "requests.exceptions.Timeout",
					description = "Превышение интервала ожидания загрузки страницы производителя {}.".format(vendor['name']))
				continue

			# Проходим по всем ссылкам
			tree = lxml.html.fromstring(r.text)
			urls = tree.xpath('//a/@href')

			# Добавляем в список ссылок на прайс-листы соответсвующие
			for url in urls:

				price = {}

				if self.urls['search_price'] in url:

					if not self.urls['prefix'] in url:
						url  = '{}{}'.format(self.urls['prefix'], url)

					price['url']  = url
					price['name'] = vendor['name']

					if price['url'] and price['name']:
						prices.append(price)
						print('Прайс-лист {} из {}: {} [{}].'.format(n + 1, len(vendors), price['url'], price['name']))

		return prices


	def getData(self, url, name = None):

		print('Загружаю: {}.'.format(url))

		# Загружаем прайс-лист
		try:
			r = self.s.get(
				url,
				cookies         = self.cookies,
				allow_redirects = True,
				timeout         = 30.0)
			self.cookies = r.cookies
		except requests.exceptions.Timeout:
			Log.objects.add(
				subject     = "catalog.updater.{}".format(self.updater.alias),
				channel     = "error",
				title       = "requests.exceptions.Timeout",
				description = "Превышение интервала ожидания загрузки каталога.")
			return False

		try:
			zip_data = ZipFile(BytesIO(r.content))
		except:
			Log.objects.add(
				subject     = "catalog.updater.{}".format(self.updater.alias),
				channel     = "error",
				title       = "requests.exceptions.Timeout",
				description = 'Битый архив: <a href="{url}">{name}</a>.'.format(url = url, name = name))
			return False

		data = zip_data.open(zip_data.namelist()[0])

		return data


	def parsePrice(self, data, vendor):

		# Номера строк и столбцов
		num = {
			'header_line' : 3,
			'first_line'  : 5}

		# Распознаваемые слова
		word = {
			'party_article'   : 'AxoftSKU',
			'product_article' : 'VendorSKU',
			'product_name'    : 'ProductDescription',
			'product_version' : 'Version',
			'price_in'        : 'Partner',
			'price_out'       : 'Retail',
			'product_vat'     : 'NDS'}

		# Сопоставление валют
		currencies = {
			'General'           : None,
			'#,##0.00[$р.-419]' : self.rub,
			'[$$-409]#,##0.00'  : self.usd,
			'[$€-2]\\ #,##0.00' : self.eur}

		# Имя категории поставщика
		category_synonym_name = None

		# Парсим
		try:
			book = xlrd.open_workbook(
				file_contents   = data.read(),
				formatting_info = True)
		except NotImplementedError:
			print("Ошибка: непонятная ошибка при открытии файла.")
			return False
		sheet = book.sheet_by_index(0)

		# Получаем словарь форматов (потребуется при получении валюты)
		formats = book.format_map

		# Проходим по всем строкам
		for row_num in range(sheet.nrows):
			row = sheet.row_values(row_num)

			# Заголовок
			if row_num == num['header_line']:

				# Разбираем заголовок
				for cel_num, cel in enumerate(row):
					if   str(cel).strip() == word['party_article']:
						num['party_article'] = cel_num
					elif str(cel).strip() == word['product_article']:
						num['product_article'] = cel_num
					elif str(cel).strip() == word['product_name']:
						num['product_name'] = cel_num
					elif str(cel).strip() == word['product_version']:
						num['product_version'] = cel_num
					elif str(cel).strip() == word['price_in']:
						num['price_in'] = cel_num
					elif str(cel).strip() == word['price_out']:
						num['price_out'] = cel_num
					elif str(cel).strip() == word['product_vat']:
						num['product_vat'] = cel_num

				# Проверяем, все ли столбцы распознались
				if len(num) < 9:
					print(len(num))
					for n in num:
						print(n)
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else: print("Структура данных без изменений.")

			# Строка с данными
			elif row_num >= num['first_line']:

				# Определяем значение переменных
				if row[num['product_article']]:
					product_article = row[num['product_article']]
				else:
					product_article = row[num['party_article']]
				party_article       = row[num['party_article']]
				product_name        = row[num['product_name']]
				product_version     = row[num['product_version']]
				price_in            = self.fixPrice(row[num['price_in']])
				price_out           = self.fixPrice(row[num['price_out']])
				product_vat         = row[num['product_vat']]

				# Валюта входной цены
				xfx = sheet.cell_xf_index(row_num, num['price_in'])
				xf = book.xf_list[xfx]
				format_str = formats[xf.format_key].format_str
				price_currency_in = currencies[format_str]

				# Валюта выходной цены
				xfx = sheet.cell_xf_index(row_num, num['price_out'])
				xf = book.xf_list[xfx]
				format_str = formats[xf.format_key].format_str
				price_currency_out = currencies[format_str]

				# Имя синонима категории
				if product_name and not product_article:
					category_synonym_name = "{}: {}".format(
						vendor.name,
						row[num['product_name']])

				# Продукт
				elif product_article and product_name:

					# Получаем объект категории
					if category_synonym_name:
						category_synonym = CategorySynonym.objects.take(
							name        = category_synonym_name,
							updater     = self.updater,
							distributor = self.distributor)
						category = category_synonym.category
					else:
						category = None

					# Получаем объект товара
					product = Product.objects.take(
						article  = product_article,
						vendor   = vendor,
						name     = product_name,
						category = category,
						unit     = self.default_unit)
					self.count['product'] += 1

					# Добавляем партии
					party = Party.objects.make(
						product        = product,
						stock          = self.on_order,
						price          = price_in,
						price_type     = self.dp,
						currency       = price_currency_in,
						price_out      = price_out,
						price_type_out = self.rp,
						currency_out   = price_currency_out,
						quantity       = -1,
						unit           = self.default_unit,
						time           = self.start_time)
					self.count['party'] += 1

		return True


	def fixPrice(self, price):
		if price:
			try: price = float(price)
			except ValueError: price = None
		else: price = None
		return price
