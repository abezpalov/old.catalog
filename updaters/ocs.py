import requests
import json
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


	name = 'OCS'
	alias = 'ocs'


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

		self.stocks = {}

		self.stocks['Самара'] = Stock.objects.take(
			alias             = self.alias + '-stock-samara',
			name              = self.name + ': склад в Самаре',
			delivery_time_min = 1,
			delivery_time_max = 3,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stocks['Самара'])

		self.stocks['Саратов'] = Stock.objects.take(
			alias             = self.alias + '-stock-saratov',
			name              = self.name + ': склад в Саратове',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stocks['Саратов'])

		self.stocks['Оренбург'] = Stock.objects.take(
			alias             = self.alias + '-stock-orenburg',
			name              = self.name + ': склад в Оренбурге',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stocks['Оренбург'])

		self.stocks['Казань'] = Stock.objects.take(
			alias             = self.alias + '-stock-kazan',
			name              = self.name + ': склад в Казани',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stocks['Казань'])

		self.stocks['Нижний Новгород'] = Stock.objects.take(
			alias             = self.alias + '-stock-nizhniy-novgorod',
			name              = self.name + ': склад в Нижнем Новгороде',
			delivery_time_min = 5,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stocks['Нижний Новгород'])

		self.stocks['В пути'] = Stock.objects.take(
			alias             = self.alias + '-transit',
			name              = self.name + ': в пути',
			delivery_time_min = 10,
			delivery_time_max = 60,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stocks['В пути'])

		self.stocks['Транзит из ЦО'] = Stock.objects.take(
			alias             = self.alias + '-transit-from-moskow',
			name              = self.name + ': транзит со склада в Москве',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stocks['Транзит из ЦО'])

		self.stocks['ЦО'] = Stock.objects.take(
			alias             = self.alias + '-stock-moskow',
			name              = self.name + ': склад в Москве',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stocks['ЦО'])

		# Единица измерения
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')

		# Тип цены
		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')

		# Валюты
		self.rub = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  =1)
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
		self.url = 'https://b2bservice.ocs.ru/b2bJSON.asmx/'


	def run(self):

		category_synonyms = {}
		locations = []

		currencies = {
			"RUR": self.rub,
			"RUB": self.rub,
			"EUR": self.eur,
			"USD": self.usd}

		# Получаем категории
		print('Получаем категории.')
		headers = {'Content-Type': 'application/json; charset=utf-8'}
		payload = json.dumps({
			'Login': self.updater.login,
			'Token': self.updater.password})
		try:
			r = requests.post(
				self.url + 'GetCatalog',
				data = payload,
				headers = headers,
				verify = False,
				timeout = 100.0)
		except requests.exceptions.Timeout:
			print("Ошибка: превышен интервал ожидания загрузки категорий.")
			return False

		for c in json.loads(r.text)['d']['Categories']:
			if c['ParentCategoryID']:
				category_synonyms[c['CategoryID']] = "{} | {}".format(
					category_synonyms[c['ParentCategoryID']],
					c['CategoryName'])
			else:
				category_synonyms[c['CategoryID']] = c['CategoryName']
			print(category_synonyms[c['CategoryID']])

		# Получаем локации
		print('Получаем локации.')
		payload = json.dumps({
			'Login':        self.updater.login,
			'Token':        self.updater.password,
			'Availability': 1,
			'ShipmentCity': 'Самара'})

		try:
			r = requests.post(
				self.url + 'GetLocations',
				data    = payload,
				headers = headers,
				verify  = False,
				timeout = 100.0)
		except requests.exceptions.Timeout:
			print("Ошибка: превышен интервал ожидания загрузки локаций.")
			return False

		for l in json.loads(r.text)['d']['LocationList']:
			locations.append(l['Location'])
			print(l['Location'])

		# Получаем продукты
		print('Получаем продукты.')
		payload = json.dumps({
			'Login': self.updater.login,
			'Token': self.updater.password,
			'Availability': 0,
			'ShipmentCity': 'Самара',
			'CategoryIDList': None,
			'ItemIDList': None,
			'LocationList': locations,
			'DisplayMissing': 1})

		try:
			r = requests.post(
				self.url + 'GetProductAvailability',
				data    = payload,
				headers = headers,
				verify  = False,
				timeout = 100.0)
		except requests.exceptions.Timeout:
			print("Ошибка: превышен интервал ожидания загрузки товаров.")
			return False

		# Проходим по элементам списка продуктов
		for p in json.loads(r.text)['d']['Products']:

			# Синоним категории
			try:
				category_synonym_name = category_synonyms[p['CategoryID']]
			except KeyError:
				category_synonym_name = p['CategoryID']
			category_synonym = CategorySynonym.objects.take(
				name        = category_synonym_name,
				updater     = self.updater,
				distributor = self.distributor)

			# Синоним производителя
			vendor_synonym = VendorSynonym.objects.take(
				name        = p['Producer'],
				updater     = self.updater,
				distributor = self.distributor)

			# Продукт
			product_article = p['PartNumber']
			product_name = p['ItemName']
			if product_article and product_name and vendor_synonym.vendor:
				product = Product.objects.take(
					article  = product_article,
					vendor   = vendor_synonym.vendor,
					name     = product_name,
					category = category_synonym.category,
					unit     = self.default_unit)
				print("{} {}".format(product.vendor.name, product.article))

				# Цена
				price = p['Price']

				# Валюта
				try:
					currency = currencies[p['Currency']]
				except KeyError:
					currency = currencies['EUR']

				# Партии
				for l in p['Locations']:

					stock = self.stocks[l['Location']]				
					quantity = l['Quantity']

					party = Party.objects.make(
						product    = product,
						stock      = stock,
						price      = price,
						price_type = self.dp,
						currency   = currency,
						quantity   = quantity,
						unit       = self.default_unit)
					print("{} {} = {} {}".format(
						product.vendor.name,
						product.article,
						party.price,
						party.currency.alias))

		return True
