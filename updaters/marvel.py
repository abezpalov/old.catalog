import time
import requests
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

	name = 'Marvel'
	alias = 'marvel'

	def __init__(self):

		# Объект дистрибьютора
		self.distributor = Distributor.objects.take(
			alias = self.alias,
			name  = self.name)

		# Объект загрузчика
		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = self.distributor)

		# Склад в Москве
		self.stock_msk = Stock.objects.take(
			alias             = self.alias + '-stock-msk',
			name              = self.name + ': склад в Москве',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stock_msk)

		# Склад в Санкт-Петербурге
		self.stock_spb = Stock.objects.take(
			alias             = self.alias + '-stock-spb',
			name              = self.name + ': склад в Санкт-Петербурге',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stock_spb)

		# Единица измерения
		self.default_unit = Unit.objects.take(alias = 'pcs', name = 'шт.')

		# Тип цены
		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')

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

		# Дополнительные переменные
		self.url = 'https://b2b.marvel.ru/Api/'
		self.key = ''
		self.task = {
			'categories': 'GetCatalogCategories',
			'catalog':    'GetFullStock'}
		self.request_format = {'xml': '0', 'json': '1'}
		self.cookies = None
		self.category_synonyms = {}
		self.currencies = {
			'RUB': self.rub,
			'USD': self.usd,
			'EUR': self.eur}
		self.stocks = {
			'msk': self.stock_msk,
			'spb': self.stock_spb}


	def run(self):

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False

		# Получаем категории для обработки
		data = self.getData('categories', 'json')

		# Обрабатываем категории
		if data: self.parseCategories(data)
		else: return False

		print('Ждем 15 минут.')
		time.sleep(901)

		# Получаем каталог для обработки
		data = self.getData('catalog', 'json', 1)

		# Обрабатываем каталог
		if data: self.parseCatalog(data)
		else: return False

		return True

	def getData(self, task, request_format, pack_status = None):

		# Создаем сессию
		s = requests.Session()

		# Собираем URL
		if not pack_status is None:
			url = '{url}{task}?user={login}&password={password}&secretKey={key}&packStatus={pack_status}&responseFormat={request_format}'.format(
			url            = self.url,
			task           = self.task[task],
			login          = self.updater.login,
			password       = self.updater.password,
			key            = None,
			pack_status    = pack_status,
			request_format = self.request_format[request_format])
		else:
			url = '{url}{task}?user={login}&password={password}&secretKey={key}&responseFormat={request_format}'.format(
			url            = self.url,
			task           = self.task[task],
			login          = self.updater.login,
			password       = self.updater.password,
			key            = None,
			request_format = self.request_format[request_format])

		# Выполняем запрос
		r = s.post(
			url,
			cookies = self.cookies,
			verify = False,
			timeout = 300)

		# Обрабатываем ответ
		if 'json' == request_format:
			import json
			data = json.loads(r.text)
			if data['Header']['Key']: self.key = data['Header']['Key']
			if data['Header']['Code'] != 0:
				print('Ошибка: невнятный ответ сервера.')
				if data['Header']['Message']: print(data['Header']['Message'])
				return False
			else:
				return data['Body']
		else:
			print('Ошибка: используется неподдерживаемый формат.')
			return False


	def parseCategories(self, data):

		# Категории
		for category in data['Categories']:
			self.parseCategory(category)


	def parseCategory(self, category):

		# ID
		category_id = category['CategoryID']
		parent_id = category['ParentCategoryId']

		# Имя
		category_name = category['CategoryName']
		if parent_id:
			category_name = "{} | {}".format(
				self.category_synonyms[parent_id],
				category_name)

		# Добавляем в словарь
		self.category_synonyms[category_id] = category_name
		print(category_name)

		# Проходим рекурсивно по подкатегориям
		for sub_category in category['SubCategories']:
			self.parseCategory(sub_category)


	def parseCatalog(self, data):

		# Проходим по категориям
		for item in data['CategoryItem']:

			# Определяем значение переменных
			product_article       = item['WareArticle']
			product_name          = item['WareFullName']
			category_synonym_id   = item['CategoryId']
			category_synonym_name = self.category_synonyms[category_synonym_id]
			vendor_synonym_name   = item['WareVendor']

			party_price    = self.fixPrice(item['WarePrice'])
			party_currency = self.currencies[item['WareVendor']]
			party_quantity = {
				'msk': self.fixQuantity(item['AvailableForShippingInMSKCount']),
				'spb': self.fixQuantity(item['AvailableForShippingInSPBCount'])}

			# Синоним категории
			category_synonym = CategorySynonym.objects.take(
				name        = category_synonym_name,
				updater     = self.updater,
				distributor = self.distributor)

			# Синоним производителя
			vendor_synonym = VendorSynonym.objects.take(
				name        = vendor_synonym_name,
				updater     = self.updater,
				distributor = self.distributor)

			# Продукт
			if product_article and product_name and vendor_synonym.vendor:
				product = Product.objects.take(
					article  = product_article,
					vendor   = vendor_synonym.vendor,
					name     = product_name,
					category = category_synonym.category,
					unit     = self.default_unit)
				print("{} {}".format(product.vendor.name, product.article))

			# Партии
			stock_name = 'msk'
			if party_quantity[stock_name]:
				party = Party.objects.make(
					product    = product,
					stock      = self.stocks[stock_name],
					price      = party_price,
					price_type = self.dp,
					currency   = party_currency,
					quantity   = party_quantity[stock_name],
					unit       = self.default_unit)
				print("{} {} = {} {}".format(
					product.vendor.name,
					product.article,
					party.price,
					party.currency.alias))
			stock_name = 'spb'
			if party_quantity[stock_name]:
				party = Party.objects.make(
					product    = product,
					stock      = self.stocks[stock_name],
					price      = party_price,
					price_type = self.dp,
					currency   = party_currency,
					quantity   = party_quantity[stock_name],
					unit       = self.default_unit)
				print("{} {} = {} {}".format(
					product.vendor.name,
					product.article,
					party.price,
					party.currency.alias))


	def fixPrice(self, price):
		price = str(price)
		price = price.replace(',', '.')
		if price: price = float(price)
		else: price = None
		return price


	def fixQuantity(self, quantity):
		price = price.replace('+', '')
		quantity = int(quantity)
		return quantity
