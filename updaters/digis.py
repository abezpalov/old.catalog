import requests
import lxml.html
from datetime import date
from datetime import datetime
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


	name = 'Digis'
	alias = 'digis'


	def __init__(self):

		# Поставщик
		self.distributor = Distributor.objects.take(
			alias = self.alias,
			name  = self.name)

		# Загрузчик
		self.updater = Updater.objects.take(
			alias = self.alias,
			name  = self.name,
			distributor = self.distributor)

		# На заказ
		self.factory = Stock.objects.take(
			alias             = self.alias + '-factory',
			name              = self.name + ': на заказ',
			delivery_time_min = 20,
			delivery_time_max = 60,
			distributor       = self.distributor)
		Party.objects.clear(stock=self.factory)

		# Склад
		self.stock = Stock.objects.take(
			alias             = self.alias + '-stock',
			name              = self.name+': склад',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stock)

		# Транзит
		self.transit = Stock.objects.take(
			alias             = self.alias + '-transit',
			name              = self.name + ': транзит',
			delivery_time_min = 10,
			delivery_time_max = 40,
			distributor       = self.distributor)
		Party.objects.clear(stock=self.transit)

		# Единица измерения
		self.default_unit = Unit.objects.take(alias = 'pcs', name = 'шт.')

		# Типы цен
		self.rp = PriceType.objects.take(alias = 'RP', name = 'Розничная цена')
		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')

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
			full_name = 'Евро',
			rate      = 80,
			quantity  = 1)

		# Дополнительные переменные
		self.url = {
			'start': 'http://digis.ru/distribution/',
			'login': 'http://digis.ru/distribution/?login=yes',
			'files': 'http://digis.ru/personal/profile/price/',
			'base':  'http://digis.ru',
			'price': '/bitrix/redirect.php?event1=news_out&event2=/personal/profile/price/p14u/daily_price_cs_pdl.xlsx'}

		self.currencies = {
			'RUB':  self.rub,
			'RUR':  self.rub,
			'руб':  self.rub,
			'руб.': self.rub,
			'USD':  self.usd,
			'EUR':  self.eur,
			'':     None}

		self.stocks = {
			'factory': self.factory,
			'stock':   self.stock,
			'transit': self.transit}


	def run(self):

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		try:
			r = s.get(self.url['start'], allow_redirects = True, timeout = 30.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания загрузки Cookies.")
			return False

		# Авторизуемся
		try:
			payload = {
				'AUTH_FORM': 'Y',
				'TYPE': 'AUTH',
				'backurl': '/distribution/',
				'href': 'http://digis.ru/distribution/',
				'USER_LOGIN': self.updater.login,
				'USER_PASSWORD': self.updater.password,
				'USER_REMEMBER': 'Y',
				'Login': 'Войти'}
			r = s.post(self.url['login'], cookies = cookies, data = payload, allow_redirects = True)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания подтверждения авторизации.")
			return False

		# Заходим на страницу загрузки
		try:
			r = s.get(self.url['files'], cookies = cookies, timeout = 30.0)
		except requests.exceptions.Timeout:
			print("Превышение интервала загрузки ссылок.")
			return False

		# Получаем ссылки со страницы
		tree = lxml.html.fromstring(r.text)
		urls = tree.xpath('//a/@href')
		for url in urls:
			if self.url['price'] in url:

				# Дописываем префикс url при необходимости
				if not self.url['base'] in url:
					url = self.url['base'] + url

				# Скачиваем прайс-лист
				print("Прайс-лист найден: {}".format(url))
				r = s.get(url, cookies = cookies)

				# TODO Парсим прайс-лист
				if self.parsePrice(r): return True
				else: return False

		print("Ошибка: прайс-лист не найден.")
		return False

	def parsePrice(self, r):

		import xlrd
		from io import BytesIO

		xlsx_data = BytesIO(r.content)

		# Номера строк и столбцов
		num = {'header': 10}

		# Распознаваемые слова
		word = {
			'category':           'Категория',
			'category_sub':       'Подкатегория',
			'product_vendor':     'Бренд',
			'party_article':      'Код',
			'product_article':    'Артикул',
			'product_name':       'Наименование',
			'quantity_factory':   'На складе',
			'quantity_stock':     'Доступно к заказу',
			'quantity_transit':   'Транзит',
			'party_price_in':     'Цена (партн)',
			'party_currency_in':  None,
			'party_price_out':    'Цена (розн)',
			'party_currency_out': None,
			'product_warranty':   'Гарантия'}

		book = xlrd.open_workbook(file_contents = xlsx_data.read())
		sheet = book.sheet_by_index(1)

		for row_num in range(sheet.nrows):
			row = sheet.row_values(row_num)

			# Пустые строки
			if row_num < num['header']:
				continue

			# Заголовок таблицы
			elif row_num == num['header']:
				for cel_num, cel in enumerate(row):
					if   str(cel).strip() == word['category']:
						num['category'] = cel_num
					elif str(cel).strip() == word['category_sub']:
						num['category_sub']       = cel_num
					elif str(cel).strip() == word['product_vendor']:
						num['product_vendor']     = cel_num
					elif str(cel).strip() == word['party_article']:
						num['party_article']      = cel_num
					elif str(cel).strip() == word['product_article']:
						num['product_article']    = cel_num
					elif str(cel).strip() == word['product_name']:
						num['product_name']       = cel_num
					elif str(cel).strip() == word['quantity_factory']:
						num['quantity_factory']   = cel_num
					elif str(cel).strip() == word['quantity_stock']:
						num['quantity_stock']     = cel_num
					elif str(cel).strip() == word['quantity_transit']:
						num['quantity_transit']   = cel_num
					elif str(cel).strip() == word['party_price_in']:
						num['party_price']        = cel_num
						num['party_currency']     = cel_num + 1
					elif str(cel).strip() == word['party_price_out']:
						num['party_price_out']     = cel_num
						num['party_currency_out']  = cel_num + 1
					elif str(cel).strip() == word['product_warranty']:
						num['product_warranty']   = cel_num

				# Проверяем, все ли столбцы распознались
				if not len(num) == 15:
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else: print("Структура данных без изменений.")

			# Товар
			elif row[num['product_article']] and row[num['product_vendor']]:

				# Синоним категории
				category_synonym = CategorySynonym.objects.take(
					name        = "{} | {}".format(row[num['category']], row[num['category_sub']]),
					updater     = self.updater,
					distributor = self.distributor)

				# Синоним производителя
				vendor_synonym = VendorSynonym.objects.take(
					name        = row[num['product_vendor']],
					updater     = self.updater,
					distributor = self.distributor)

				# Продукт
				product_article    = row[num['product_article']]
				product_name       = row[num['product_name']]

				if product_article and product_name and vendor_synonym.vendor:

					product = Product.objects.take(
						article  = product_article,
						vendor   = vendor_synonym.vendor,
						name     = product_name,
						category = category_synonym.category,
						unit     = self.default_unit)
					print("{} {}".format(product.vendor.name, product.article))

					# Партии
					party_article      = row[num['party_article']]

					quantity            = {}
					quantity['factory'] = self.fixQuantityFactory(row[num['quantity_factory']])
					quantity['stock']   = self.fixQuantityStock(row[num['quantity_stock']])
					quantity['transit'] = self.fixQuantityTransit(row[num['quantity_transit']])

					party_price         = self.fixPrice(row[num['party_price']])
					party_currency      = self.currencies[row[num['party_currency']]]

					party_price_out     = self.fixPrice(row[num['party_price_out']])
					party_currency_out  = self.currencies[row[num['party_currency_out']]]

					# Партии на заказ
					stock_name = 'factory'
					if quantity[stock_name]:
						party = Party.objects.make(
							product        = product,
							stock          = self.stocks[stock_name],
							article        = party_article,
							price          = party_price,
							price_type     = self.dp,
							currency       = party_currency,
							price_out      = party_price,
							price_type_out = self.rp,
							currency_out   = party_currency,
							quantity       = quantity[stock_name],
							unit           = self.default_unit)
						print("{} {} = {} {}".format(
							product.vendor.name,
							product.article,
							party.price,
							party.currency))

					# Партии на складе
					stock_name = 'stock'
					if quantity[stock_name]:
						party = Party.objects.make(
							product        = product,
							stock          = self.stocks[stock_name],
							article        = party_article,
							price          = party_price,
							price_type     = self.dp,
							currency       = party_currency,
							price_out      = party_price,
							price_type_out = self.rp,
							currency_out   = party_currency,
							quantity       = quantity[stock_name],
							unit           = self.default_unit)
						print("{} {} = {} {}".format(
							product.vendor.name,
							product.article,
							party.price,
							party.currency))

					# Партии в транзите
					stock_name = 'transit'
					if quantity[stock_name]:
						party = Party.objects.make(
							product        = product,
							stock          = self.stocks[stock_name],
							article        = party_article,
							price          = party_price,
							price_type     = self.dp,
							currency       = party_currency,
							price_out      = party_price,
							price_type_out = self.rp,
							currency_out   = party_currency,
							quantity       = quantity[stock_name],
							unit           = self.default_unit)
						print("{} {} = {} {}".format(
							product.vendor.name,
							product.article,
							party.price,
							party.currency))

		return True


	def fixPrice(self, price):
		price = str(price).strip()
		if price == 'звоните': return None
		elif price: return float(price)
		else: return None


	def fixQuantityFactory(self, quantity):
		quantity = str(quantity).strip()
		if quantity in ('под заказ'): return -1
		else: return None


	def fixQuantityStock(self, quantity):
		quantity = str(quantity).strip()

		quantity = quantity.replace('более ', '')

		return int(float(quantity))


	def fixQuantityTransit(self, quantity):
		quantity = str(quantity).strip()
		if quantity: return 5
		else: return None
