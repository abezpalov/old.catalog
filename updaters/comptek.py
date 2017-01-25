from project.models import Log

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

	name = 'Comptek'
	alias = 'comptek'
	url = {
		'start'    : 'http://comptek.ru/',
		'login'    : 'http://comptek.ru/personal/auth.xhtml',
		'price'    : 'http://comptek.ru/',
		'filter'   : 'catalog/',
		'unfilter' : 'item/',
		'base'     : 'http://comptek.ru'}

	def __init__(self):

		super().__init__()

		self.stock    = self.take_stock('stock', 'склад', 3, 10)
		self.transit  = self.take_stock('transit', 'транзит', 10, 60)
		self.on_order = self.take_stock('on-order', 'на заказ', 40, 80)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		import time

		payload = {
			'login'    : self.updater.login,
			'password' : self.updater.password}
		if not self.login(payload):
			return False

		# Заходим на начальную страницу каталога
		tree = self.load_html(self.url['price'])

		# Проходим по всем ссылкам
		urls = []
		for u in tree.xpath('//a/@href'):
			if not u in urls:
				urls.append(u)

		i = 0
		while i < len(urls):

			# Сслыка на категорию
			if self.url['filter'] in urls[i] and self.url['unfilter'] not in urls[i]:
				url = self.url['base'] + urls[i]

				vendor = Vendor.objects.get_by_key(updater = self.updater, ext_key = url.split('/')[4])
				print('Vendor: {}.'.format(vendor))

				if vendor:
					tree = self.load_html(url)
					print("Загружена: {}.".format(url))

					for u in tree.xpath('//a/@href'):
						if not u in urls:
							urls.append(u)

					# Парсим таблицу с товарами
					self.parse(tree, vendor)

					# Ждем, чтобы не получить отбой сервера
					time.sleep(1)

				else:
					print("Пропущена: {}.".format(url))

			else:
				url = self.url['base'] + urls[i]
				print("Пропущена: {}.".format(url))

			i += 1

		# Чистим партии
		Party.objects.clear(stock = self.stock, time = self.start_time)
		Party.objects.clear(stock = self.transit, time = self.start_time)
		Party.objects.clear(stock = self.on_order, time = self.start_time)

		self.log()


	def parse(self, tree, vendor):


		# Номера строк и столбцов
		num = {
			'product_article': 0,
			'product_name':    1,
			'stock':           3,
			'transit':         4,
			'price':           5}

		# Валюты
		currencies = {
			'RUB' : self.rub,
			'USD' : self.usd,
			'EUR' : self.eur}

		# Обрабатываем синоним производителя
#		if vendor_synonym_name:
#			vendor_synonym = self.take_vendorsynonym(vendor_synonym_name)
#			vendor = vendor_synonym.vendor
#		else:
#			vendor = None

		# Получаем объект производителя
#		if vendor is None:
#			return False

		table = tree.xpath('//table[@class="list-table"]//tr')

		# Проходим по строкам таблицы
		for trn, tr in enumerate(table):

			if trn:

				product_article  = self.get_text(tr, './td[@class="art"]')
				product_name     = self.get_text(tr, './td[@class="prod-name"]/a')
				product_url      = self.get_href(tr, './td[@class="prod-name"]/a/@href')
				party_on_stock   = self.get_int(tr, './td', index = 2)
				party_on_transit = self.get_int(tr, './td', index = 4)
				party_price      = self.get_float(tr, './td', index = 5)
				party_currency   = self.get_currency(tr, './td', index = 5)

				if product_article and product_name:
					product = Product.objects.take(
						article = product_article,
						vendor = vendor,
						name = product_name,
						category = None,
						unit = self.default_unit)
					self.count['product'] += 1
				else: continue

				if party_on_stock:
					party = Party.objects.make(
						product    = product,
						stock      = self.stock,
						price      = party_price,
						price_type = self.dp,
						currency   = party_currency,
						quantity   = party_on_stock,
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1

				if party_on_transit:
					party = Party.objects.make(
						product    = product,
						stock      = self.transit,
						price      = party_price,
						price_type = self.dp,
						currency   = party_currency,
						quantity   = party_on_transit,
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1

				if not party_on_stock and not party_on_transit and party_price and party_currency:
					party = Party.objects.make(
						product    = product,
						stock      = self.on_order,
						price      = party_price,
						price_type = self.dp,
						currency   = party_currency,
						quantity   = None,
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1





	def get_text(self, element, query, index = 0):


		try:
			result = element.xpath(query)[index].text.strip()
		except Exception:
			result = ''

		return result


	def get_href(self, element, query, index = 0):

		try:
			result = element.xpath(query)[index].strip()

			if self.url['base'] not in result:
				result = self.url['base'] + result

		except Exception:
			result = ''

		return result



	def get_int(self, element, query, index = 0):

		try:
			result = int(element.xpath(query)[index].text.strip())

		except Exception:
			result = None

		return result



	def get_float(self, element, query, index = 0):

		try:
			text = element.xpath(query)[index].text.strip()
			text = text.replace('₽', '')
			text = text.replace('$', '')
			text = text.replace(' ', '')
			text = text.replace('&nbsp;', '')
			text = text.replace(' ', '') # Хитрый пробел
			print(text)
			result = float(text)

		except Exception:
			result = None

		return result


	def get_currency(self, element, query, index = 0):

		try:
			text = element.xpath(query)[index].text.strip()
		except Exception:
			text = ''

		if not text:
			result = None
		elif '₽' in text:
			result = self.rub
		elif '$' in text:
			result = self.usd
		else:
			print(text)
			exit()

		return result
