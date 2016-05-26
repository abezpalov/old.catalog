""" Updater.Marvel
	API поставщика имеет странные ограничения на время между запросами.
"""

from project.models import Log

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

	name  = 'Marvel'
	alias = 'marvel'

	url = 'https://b2b.marvel.ru/Api/'


	def __init__(self):

		super().__init__()

		self.stock_msk = self.take_stock('stock-msk', 'склад в Москве', 3, 10)
		self.stock_spb = self.take_stock('stock-spb', 'склад в Санкт-Петербурге', 3, 10)

		self.count = {
			'product' : 0,
			'party'   : 0}

		# Дополнительные переменные
		# TODO ??
		self.key = ''
		self.task = {
			'categories' : 'GetCatalogCategories',
			'catalog'    : 'GetFullStock',
			'parameters' : 'GetItems',
			'photos'     : 'GetItemPhotos'}
		self.request_format = {
			'xml'  : '0',
			'json' : '1'}
		self.cookies = None
		self.category_synonyms = {}
		self.currencies = {
			'RUB' : self.rub,
			'RUR' : self.rub,
			'USD' : self.usd,
			'EUR' : self.eur,
			''    :    None}
		self.stocks = {
			'msk' : self.stock_msk,
			'spb' : self.stock_spb}


	def run(self):

		import time

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False

		# Загружаем и парсим категирии
		data = self.get_data('categories', 'json')
		self.parse_categories(data)

		print('Ждем 15 минут.')
		m = 905
		for i in range(m):
			print("Осталось {} секунд.".format(m-i))
			time.sleep(1)

		# Загружаем и парсим каталог
		data = self.get_data('catalog', 'json', 1)
		self.parse_catalog(data)

		# Чистим партии
		Party.objects.clear(stock = self.stock_msk, time = self.start_time)
		Party.objects.clear(stock = self.stock_spb, time = self.start_time)

		self.log()


	def update_products_description(self):

		# Количество продуктов за один запрос
		l = 50

		# Получаем задачи с базы
		tasks = UpdaterTask.objects.filter(
			complite = False,
			name     = 'update.product.description',
			updater  = self.updater)

		# Вычисляем количество запросов
		if len(tasks) % l:
			q = len(tasks) // l + 1
		else:
			q = len(tasks) // l

		# Формируем группы товаров для запросов
		for n in range(q):

			party = tasks[n * l : (n + 1) * l]

			articles = []
			products = {}

			for p in party:

				product = Product.objects.get(id = p.subject)
				articles.append(product.article)
				products[product.article] = product

			print('Tasks[{}:{}] - {} products.'.format(n*l, (n+1)*l, len(party)))

			# Выполняем запрос
			data = self.get_data('parameters', 'json', 1, articles)

			# Парсим параметры продуктов
			if data:
				self.parse_parameters(data, products)
			else:
				print('Error!')
				continue


			# Выполняем запрос перечней фотографий продуктов
			data = self.get_data('photos', 'json', 1, articles)

			# Парсим перечни фотографий продуктов
			if data:
				self.parse_photos(data, products)
			else:
				print('Error!')
				continue


	def get_data(self, task, request_format, pack_status = None, articles = None):

		import requests

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

		if articles:

			# Готовим начало
			url = '{url}{mid}'.format(
				url = url,
				mid = '&getExtendedItemInfo=1&items={"WareItem": [')

			# Добавляем артикулы
			for article in articles:
				url = '{url}{mid}{article}{end}'.format(
					url     = url,
					mid     = '{"ItemId": "',
					article = article,
					end     = '"},')

			# Удаляем лишнюю запятую
			url = url[0 : len(url) - 1]

			# Добавляем конец
			url = '{url}{end}'.format(
				url = url,
				end = ']}')

		# Выполняем запрос
		try:
			r = s.post(url, cookies = self.cookies, verify = False, timeout = 300)
		except Exception:
			print('Нет соединения')
			return False
		else:

			# Обрабатываем ответ
			if 'json' == request_format:

				import json

				try:
					data = json.loads(r.text)
				except Exception:
					return False

				if data['Header']['Key']: self.key = data['Header']['Key']
				if data['Header']['Code'] != 0:
					if data['Header']['Message']:
						Log.objects.add(
						subject     = "catalog.updater.{}".format(self.updater.alias),
						channel     = "error",
						title       = "?",
						description = data['Header']['Message'])
					else:
						Log.objects.add(
						subject     = "catalog.updater.{}".format(self.updater.alias),
						channel     = "error",
						title       = "?",
						description = "Невнятный ответ сервера")
					return False
				else:
					return data['Body']
			else:
				print('Ошибка: используется неподдерживаемый формат.')
				return False


	def parse_categories(self, data):

		for category in data['Categories']:
			self.parse_category(category)


	# Используется рекурсия
	def parse_category(self, category):

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
			self.parse_category(sub_category)


	def parse_catalog(self, data):

		# Проходим по категориям
		for item in data['CategoryItem']:

			# Определяем значение переменных
			product_article       = item['WareArticle']
			product_name          = item['WareFullName']
			category_synonym_id   = item['CategoryId']
			try:
				category_synonym_name = self.category_synonyms[category_synonym_id]
			except KeyError:
				category_synonym_name = 'Новые'
			vendor_synonym_name   = item['WareVendor']

			party_price    = self.fix_price(item['WarePrice'])
			party_currency = self.currencies[item['WarePriceCurrency']]
			party_quantity = {
				'msk': self.fix_quantity(item['AvailableForShippingInMSKCount']),
				'spb': self.fix_quantity(item['AvailableForShippingInSPBCount'])}

			# Синоним категории
			category_synonym = self.take_categorysynonym(category_synonym_name)

			# Синоним производителя
			vendor_synonym = self.take_vendorsynonym(vendor_synonym_name)

			# Продукт
			if product_article and product_name and vendor_synonym.vendor:
				product = Product.objects.take(
					article  = product_article,
					vendor   = vendor_synonym.vendor,
					name     = product_name,
					category = category_synonym.category,
					unit     = self.default_unit)
				self.count['product'] += 1
				UpdaterTask.objects.take(
					name    = 'update.product.description',
					subject = product.id,
					updater = self.updater)

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
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1
				stock_name = 'spb'
				if party_quantity[stock_name]:
					party = Party.objects.make(
						product    = product,
						stock      = self.stocks[stock_name],
						price      = party_price,
						price_type = self.dp,
						currency   = party_currency,
						quantity   = party_quantity[stock_name],
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1


	def parse_parameters(self, data, products):

		print('parseParameters')

		for pr in data['CategoryItem']:
			print(pr['WareArticle'])

			try:
				product = products[pr['WareArticle']]
				ps = data['CategoryItem'][0]['ExtendedInfo']['Parameter']

			except Exception:
				print('Error?')
				continue

			else:

				for p in ps:

					name  = p['ParameterName']
					value = p['ParameterValue']
#					print('\t{} = {}'.format(name, value))

					parameter_synonym = self.take_parametersynonym(name)

					parameter = parameter_synonym.parameter

					if parameter:
#						print('Распознан параметр: {} = {}.'.format(parameter.name, value))
						parameter_to_product = ParameterToProduct.objects.take(
							parameter = parameter,
							product   = product)
						parameter_to_product.set_value(
							value = value,
							updater = self.updater)

		return True


	def parse_photos(self, data, products):

		print('parsePhotos')

		for pr in data['Photo']:

			product = products[pr['BigImage']['WareArticle']]
			source  = pr['BigImage']['URL']

			photo = ProductPhoto.objects.load(product = product, source = source)
