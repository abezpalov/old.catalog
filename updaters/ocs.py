""" Updater.OCS
	API поставщика работает только с разрешёнными IP-адресами.
"""

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

	name = 'OCS'
	alias = 'ocs'

	url = 'https://b2bservice.ocs.ru/b2bJSON.asmx/'

	def __init__(self):

		super().__init__()

		self.stocks = {}
		self.stocks['Самара']          = self.take_stock('stock-samara', 'склад в Самаре', 1, 3)
		self.stocks['Саратов']         = self.take_stock('stock-saratov', 'склад в Саратове', 3, 10)
		self.stocks['Оренбург']        = self.take_stock('stock-orenburg', 'склад в Оренбурге', 3, 10)
		self.stocks['Казань']          = self.take_stock('stock-kazan', 'склад в Казани', 3, 10)
		self.stocks['Уфа']             = self.take_stock('stock-ufa', 'склад в Уфе', 3, 10)
		self.stocks['Нижний Новгород'] = self.take_stock('stock-nizhniy-novgorod', 'склад в Нижнем Новгороде', 3, 10)
		self.stocks['В пути']          = self.take_stock('transit', 'в пути', 10, 60)
		self.stocks['Транзит из ЦО']   = self.take_stock('transit-from-moskow', 'транзит со склада в Москве', 5, 20)
		self.stocks['ЦО (Москва)']     = self.take_stock('stock-moskow', 'склад в Москве', 3, 10)
		self.stocks['ЦО (СПб)']        = self.take_stock('stock-spb', 'склад в Санкт-Петербурге', 3, 10)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		import requests
		import json
		from django.utils import timezone

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
			category_synonym = self.take_categorysynonym(category_synonym_name)

			# Синоним производителя
			vendor_synonym = self.take_vendorsynonym(p['Producer'])

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
				self.count['product'] += 1

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
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1

		# Чистим партии
		Party.objects.clear(stock = self.stocks['Самара'],          time = self.start_time)
		Party.objects.clear(stock = self.stocks['Саратов'],         time = self.start_time)
		Party.objects.clear(stock = self.stocks['Оренбург'],        time = self.start_time)
		Party.objects.clear(stock = self.stocks['Казань'],          time = self.start_time)
		Party.objects.clear(stock = self.stocks['Уфа'],             time = self.start_time)
		Party.objects.clear(stock = self.stocks['Нижний Новгород'], time = self.start_time)
		Party.objects.clear(stock = self.stocks['В пути'],          time = self.start_time)
		Party.objects.clear(stock = self.stocks['Транзит из ЦО'],   time = self.start_time)
		Party.objects.clear(stock = self.stocks['ЦО (Москва)'],     time = self.start_time)
		Party.objects.clear(stock = self.stocks['ЦО (СПб)'],        time = self.start_time)

		self.log()
