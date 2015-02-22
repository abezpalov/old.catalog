import re
import json
import time
import xlrd
import requests
import lxml.html
from io import BytesIO
from zipfile import ZipFile
from catalog.models import Updater
from catalog.models import Distributor
from catalog.models import Stock
from catalog.models import Currency
from catalog.models import Unit
from catalog.models import CategorySynonym
from catalog.models import VendorSynonym
from catalog.models import Category
from catalog.models import Vendor
from catalog.models import Product
from catalog.models import Party
from catalog.models import PriceType
from catalog.models import Price

class Runner:


	name = 'Axsoft'
	alias = 'axoft'


	def __init__(self):

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
		Party.objects.clear(stock = self.on_order)

		# Единица измерения
		self.default_unit = Unit.objects.take(alias = 'pcs', name = 'шт.')

		# Тип цен
		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')
		self.rp = PriceType.objects.take(alias = 'RP', name = 'Розничная цена')

		# Валюты
		self.rub = Currency.objects.take(
			alias = 'RUB',
			name = 'р.',
			full_name = 'Российский рубль',
			rate = 1,
			quantity = 1)
		self.usd = Currency.objects.take(
			alias = 'USD',
			name = '$',
			full_name = 'US Dollar',
			rate = 60,
			quantity = 1)
		self.eur = Currency.objects.take(
			alias = 'EUR',
			name = 'EUR',
			full_name = 'Euro',
			rate = 80,
			quantity = 1)

		# Используемые ссылки
		self.url = {
			'start':   'http://axoft.ru/',
			'login':   'http://axoft.ru/',
			'prices':  'http://axoft.ru/software/pricelists/',
			'prefix':  'http://axoft.ru'}

		# Сессия
		self.s = requests.Session()
		self.cookie = None

		# Регулярные выражения
		self.reg = re.compile('var oFilterArray = (\[[^\[]*\])')


	def run(self):

		# Авторизуемся
		if not self.login():
			return False

		# Получаем список производителей и ссылок на их прайс-листы
		prices = self.getPrices()
		if not prices:
			print('Ошибка: не получен список прайс-листов.')
			return False

		# Проходим по каждому прайс-листу
		for n, price in enumerate(prices):

			if price['sName'] and price['sDownloadUrl']:

				print("Прайс-лист {} из {}: {}".format(
					n + 1,
					len(prices),
					price['sName']))

				# Синоним производителя
				vendor_synonym = VendorSynonym.objects.take(
					name = price['sName'],
					updater = self.updater,
					distributor = self.distributor)

				if vendor_synonym.vendor:
					url = self.url['prefix'] + price['sDownloadUrl']
					data = self.getData(url)
					if data:
						self.parsePrice(data, vendor_synonym.vendor)
				else:
					print('Производитель не привязан.')

		return True


	def login(self):

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False

		# Получаем куки
		try:
			r = self.s.get(self.url['start'], timeout = 30.0)
			self.cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания загрузки Cookies.")
			return False

		# Авторизуемся
		try:
			payload = {
				'backurl': '/',
				'AUTH_FORM': 'Y',
				'TYPE': 'AUTH',
				'IS_POPUP': '1',
				'USER_LOGIN': self.updater.login,
				'USER_PASSWORD': self.updater.password,
				'Login': 'Вход для партнеров'}
			r = self.s.post(
				self.url['login'],
				cookies = self.cookies,
				data = payload,
				allow_redirects = True,
				timeout = 30.0)
			self.cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания подтверждения авторизации.")
			return False

		return True


	def getPrices(self):

		# Загружаем начальную страницу каталога
		try:
			r = self.s.get(
				self.url['prices'],
				cookies = self.cookies,
				allow_redirects = True,
				timeout = 30.0)
			self.cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания загрузки каталога.")
			return False

		# Находим и парсим список в тексте страницы
		prices = re.search(self.reg, r.text)
		prices = json.loads(prices.group(1))

		return prices


	def getData(self, url):

		print('Загружаю: {}.'.format(url))

		# Загружаем прайс-лист
		try:
			r = self.s.get(
				url,
				cookies = self.cookies,
				allow_redirects = True,
				timeout = 30.0)
			self.cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания загрузки каталога.")
			return False

		zip_data = ZipFile(BytesIO(r.content))
		data = zip_data.open(zip_data.namelist()[0])

		print('Получен прайс: {}'.format(zip_data.namelist()[0]))

		time.sleep(1)

		return data


	def parsePrice(self, data, vendor):

		# Номера строк и столбцов
		num = {
			'header_line': 3,
			'first_line':  5}

		# Распознаваемые слова
		word = {
			'party_article':   'AxoftSKU',
			'product_article': 'VendorSKU',
			'product_name':    'ProductDescription',
			'product_version': 'Version',
			'price_in':        'Retail',
			'price_out':       'Partner',
			'product_vat':     'NDS'}

		# Сопоставление валют
		currencies = {
			'General':           None,
			'#,##0.00[$р.-419]': self.rub,
			'[$$-409]#,##0.00':  self.usd,
			'[$€-2]\\ #,##0.00': self.eur}

		# Имя категории поставщика
		category_synonym_name = None

		# Парсим
		book = xlrd.open_workbook(
			file_contents   = data.read(),
			formatting_info = True)
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
						unit           = self.default_unit)
					print("{} {} = {} {}".format(
						party.product.vendor,
						party.product.article,
						party.price,
						party.currency))

		return True


	def fixPrice(self, price):
		if price:
			try: price = float(price)
			except ValueError: price = None
		else: price = None
		return price
