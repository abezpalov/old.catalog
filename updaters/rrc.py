import re
import lxml.html
import requests
import time
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

	def __init__(self):

		# Инициируем переменные
		self.name = 'RRC'
		self.alias = 'rrc'
		self.message = ''

		# Получаем необходимые объекты
		self.distributor  = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater      = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.stock        = Stock.objects.take(alias=self.alias+'-stock', name=self.name+': склад', delivery_time_min = 3, delivery_time_max = 10, distributor=self.distributor)
		self.on_order     = Stock.objects.take(alias=self.alias+'-on-order', name=self.name+': на заказ', delivery_time_min = 10, delivery_time_max = 40, distributor=self.distributor)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.dp           = PriceType.objects.take(alias='DP', name='Диллерская цена')
		self.rub          = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)
		self.usd          = Currency.objects.take(alias='USD', name='$', full_name='US Dollar', rate=60, quantity=1)
		self.eur          = Currency.objects.take(alias='EUR', name='EUR', full_name='Евро', rate=80, quantity=1)

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.stock)
		Party.objects.clear(stock=self.on_order)

		# Используемые ссылки
		self.url = 'http://rrc.ru/catalog/?login=yes'
		self.url_prefix = 'http://rrc.ru'
		self.url_filter = '/catalog/'

		# Шаблон, соответсвующий ссылке на категорию с продуктами
		self.p = re.compile('^\/catalog\/[0-9]{4}_[0-9]_[0-9]{4}\/(\?PAGEN_[0-9]+=[0-9]+)?$')

	def run(self):

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		try:
			r = s.get(self.url, timeout=100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания загрузки Cookies.'
			return False

		# Авторизуемся
		try:
			payload = {'AUTH_FORM': 'Y', 'TYPE': 'AUTH', 'backurl': '/catalog/', 'USER_LOGIN': self.updater.login, 'USER_PASSWORD': self.updater.password, 'Login': '1'}
			r = s.post(self.url, cookies=cookies, data=payload, allow_redirects=True, timeout=30.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания подтверждения авторизации.'
			return False

		# Загружаем начальную страницу каталога
		try:
			r = s.get(self.url, cookies=cookies, allow_redirects=True, timeout=30.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания загрузки каталога.'
			return False

		# Проходим по всем ссылкам
		tree = lxml.html.fromstring(r.text)
		urls = tree.xpath('//a/@href')
		i = 0
		while i < len(urls):

			# Сслыка на категорию
			if re.match(self.p, urls[i]):

				#TODO test out
				self.message += self.url_prefix + urls[i] + '\n'
				hack = self.url_prefix + urls[i]

				# Переходим по ссылке
				try:
					r = s.get(self.url_prefix + urls[i], cookies = cookies, timeout=30.0)
					cookies = r.cookies
				except requests.exceptions.Timeout:
					self.message = 'Превышение интервала ожидания загрузки .'
					continue

				# Получаем все ссылки. Ссылки, которых нет - добавляем в список.
				tree = lxml.html.fromstring(r.text)
				new_urls = tree.xpath('//a/@href')
				for url in new_urls:
					if not url in urls: urls.append(url)

				#TODO Парсим таблицу с товарами
				self.parseProducts(tree)

			i += 1

		return True

	def parseProducts(self, tree):

		# Номера строк и столбцов
		num = {'headers': 6}

		# Распознаваемые слова
		word = {
			'article': 'Partnumber',
			'vendor': 'Вендор',
			'name': 'Товар',
			'quantity': 'Доступно',
			'price': 'Цена'}

		# Заголовок таблицы
		ths = tree.xpath('//table[@class="catalog-item-list"]/thead/tr/th')
		for thn, th in enumerate(ths):
			if   th.text == word['article']:
				num['article'] = thn
				self.message += str(thn) + "\n" 
			elif th.text == word['vendor']:
				num['vendor'] = thn
				self.message += str(thn) + "\n" 
			elif th.text == word['name']:
				num['name'] = thn
				self.message += str(thn) + "\n" 
			elif th.text == word['quantity']:
				num['quantity'] = thn
				self.message += str(thn) + "\n" 
			elif th.text == word['price']:
				num['price'] = thn
				self.message += str(thn) + "\n" 
			self.message += str(th.text) + "\n" 

		# Проверяем, все ли столбцы распознались
		if len(num) < num['headers']:
			self.message += "Ошибка структуры данных: не все столбцы опознаны.\n"
			return False
		else: self.message += "Структура данных без изменений.\n"

		# Товар
		tbs = tree.xpath('//table[@class="catalog-item-list"]/tbody[@class="b-products-item__table x-products-item"]')
		for tr in tbs:


			for tdn, td in enumerate(tr[0]):
				if tdn == num['article']:
					article = str(td.text).strip()
				if tdn == num['vendor']:
					try: vendor_synonym_name = str(td[0].text).strip()
					except IndexError: vendor_synonym_name = str(td.text).strip()
				elif tdn == num['name']: name = str(td[0].text).strip()
				elif tdn == num['quantity']: quantity = self.fixQuantity(td.text)
				elif tdn == num['price']:
					try:
						price = td[0].text
						if price and '$' == price[0]:
							price = self.fixPrice(price)
							currency = self.usd
						elif price and '€' == price[0]:
							price = self.fixPrice(price)
							currency = self.eur
						elif not price:
							price = None
							currency = None
						else:
							price = self.fixPrice(price)
							currency = self.rub
					except IndexError:
						price = None
						currency = None

#			self.message += article + ' ' + vendor_synonym_name + ' ' + str(price) + '\n'

			# Обрабатываем синоним производителя
			if vendor_synonym_name:
				vendor_synonym = VendorSynonym.objects.take(name=vendor_synonym_name, updater=self.updater, distributor=self.distributor)
			else: continue

			# Получаем объект товара
			if article and name and vendor_synonym.vendor:
				product = Product.objects.take(article=article, vendor=vendor_synonym.vendor, name=name, unit = self.default_unit)
			else: continue

			# Партии
			if quantity:
				party = Party.objects.make(product=product, stock=self.stock, price = price, price_type = self.dp, currency = currency, quantity = quantity, unit = self.default_unit)
			else:
				party = Party.objects.make(product=product, stock=self.on_order, price = price, price_type = self.dp, currency = currency, quantity = 0, unit = self.default_unit)

		return True

	def fixPrice(self, price):
		price = str(price).strip()
		price = price.replace(',', '')
		price = price.replace('$', '')
		price = price.replace('€', '')
		price = price.replace(' ', '')
		if price: price = float(price)
		else: price = 0
		return price

	def fixQuantity(self, quantity):
		quantity = str(quantity).strip()
		if quantity in ('', '0'): quantity = 0
		else: quantity = int(quantity)
		return quantity
