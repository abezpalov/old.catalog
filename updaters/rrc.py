import re
import time

from project.models import Log

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):


	name  = 'RRC'
	alias = 'rrc'

	url = {
		'start' : 'http://rrc.ru/catalog/?login=yes',
		'login' : 'http://rrc.ru/catalog/?login=yes',
		'links' : 'http://rrc.ru/catalog/?login=yes',
		'base'  : 'http://rrc.ru'}

	p = re.compile('^\/catalog\/[0-9]{4}_[0-9]_[0-9]{4}\/(\?PAGEN_[0-9]+=[0-9]+)?$')


	def __init__(self):

		super().__init__()

		self.stock    = self.take_stock('stock',    'склад',     3, 10)
		self.on_order = self.take_stock('on-order', 'на заказ', 20, 60)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		payload = {
			'AUTH_FORM'     : 'Y',
			'TYPE'          : 'AUTH',
			'backurl'       : '/catalog/',
			'USER_LOGIN'    : self.updater.login,
			'USER_PASSWORD' : self.updater.password,
			'Login'         : '1'}
		self.login(payload)

		tree = self.load_html(self.url['links'])

		# Проходим по всем ссылкам
		urls = tree.xpath('//a/@href')
		i = 0
		while i < len(urls):

			# Сслыка на категорию
			if re.match(self.p, urls[i]):
				url = self.url['base'] + urls[i]
				tree = self.load_html(url)
				print("Загружена страница: {}.".format(url))

				for u in tree.xpath('//a/@href'):
					if not u in urls:
						urls.append(u)

				# Парсим таблицу с товарами
				self.parse(tree)

				# Ждем, чтобы не получить отбой сервера
				time.sleep(1)

			i += 1

		# Чистим партии
		Party.objects.clear(stock = self.on_order, time = self.start_time)
		Party.objects.clear(stock = self.stock,    time = self.start_time)

		self.log()


	def parse(self, tree):

		# Номера строк и столбцов
		num = {'headers': 6}

		# Распознаваемые слова
		word = {
			'article'  : 'Partnumber/',
			'vendor'   : 'Вендор',
			'name'     : 'Товар',
			'quantity' : 'Доступно',
			'price'    : 'Цена'}

		# Заголовок таблицы
		ths = tree.xpath('//table[@class="catalog-item-list"]/thead/tr/th')
		for thn, th in enumerate(ths):

			if th.text == word['article']:
				num['article'] = thn
			elif th.text == word['vendor']:
				num['vendor'] = thn
			elif th.text == word['name']:
				num['name'] = thn
			elif th.text == word['quantity']:
				num['quantity'] = thn
			elif th.text == word['price']:
				num['price'] = thn

		# Проверяем, все ли столбцы распознались
		if not len(num) == num['headers']:
			return False

		# Товар
		tbs = tree.xpath('//table[@class="catalog-item-list"]/tbody[@class="b-products-item__table x-products-item"]')
		for tr in tbs:

			# Обнуляем значения
			article             = None
			vendor_synonym_name = None
			name                = None
			quantity            = None
			price               = None
			currency            = None

			# Получаем информацию о товаре
			for tdn, td in enumerate(tr[0]):
				if tdn == num['article']:
					article = str(td.text).strip()
				if tdn == num['vendor']:
					try: vendor_synonym_name = str(td[0].text).strip()
					except IndexError: vendor_synonym_name = str(td.text).strip()
				elif tdn == num['name']: name = str(td[0].text).strip()
				elif tdn == num['quantity']: quantity = self.fix_quantity(td.text)
				elif tdn == num['price']:
					try:
						price = td[0].text
						if price and '$' == price[0]:
							price = self.fix_price(price)
							currency = self.usd
						elif price and '€' == price[0]:
							price = self.fix_price(price)
							currency = self.eur
						elif not price:
							price = None
							currency = self.usd
						else:
							price = self.fix_price(price)
							currency = self.rub
					except IndexError:
						price = None
						currency = self.usd

			# Обрабатываем синоним производителя
			if vendor_synonym_name:
				vendor_synonym = VendorSynonym.objects.take(
					name        = vendor_synonym_name,
					updater     = self.updater,
					distributor = self.distributor)
			else: continue

			# Получаем объект товара
			if article and name and vendor_synonym.vendor:
				product = Product.objects.take(
					article = article,
					vendor  = vendor_synonym.vendor,
					name    = name,
					unit    = self.default_unit)
				self.count['product'] += 1
			else: continue

			# Партии
			if quantity:
				party = Party.objects.make(
					product    = product,
					stock      = self.stock,
					price      = price,
					price_type = self.dp,
					currency   = currency,
					quantity   = quantity,
					unit       = self.default_unit,
					time       = self.start_time)
				self.count['party'] += 1
			else:
				party = Party.objects.make(
					product    = product,
					stock      = self.on_order,
					price      = price,
					price_type = self.dp,
					currency   = currency,
					quantity   = 0,
					unit       = self.default_unit,
					time       = self.start_time)
				self.count['party'] += 1

		return True


	def fix_price(self, price):

		price = price.replace(',', '')

		price = super().fix_price(price)

		return price
