import time
import requests
import lxml.html
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
		self.name = 'Landata'
		self.alias = 'landata'

		# Получаем необходимые объекты
		self.distributor = Distributor.objects.take(alias = self.alias, name = self.name)
		self.updater = Updater.objects.take(alias = self.alias, name = self.name, distributor = self.distributor)

		# Склады
		# C1- склад №1 по адресу 2-ой пер. Петра Алексеева д.2 стр.1
		self.s1 = Stock.objects.take(
			alias = self.alias + '-stock-1',
			name = self.name + ': склад № 1',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor = self.distributor)
		Party.objects.clear(stock = self.s1)

		# C2- склад №2 по адресу Дмитровское шоссе
		self.s2 = Stock.objects.take(
			alias = self.alias + '-stock-2',
			name = self.name + ': склад № 2',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor = self.distributor)
		Party.objects.clear(stock = self.s2)

		# БТ- Ближний транзит - свободный товар, поступающий на склады Landata в течение 1-21 дней
		self.bt = Stock.objects.take(
			alias = self.alias + '-b-transit',
			name = self.name + ': ближний транзит',
			delivery_time_min = 10,
			delivery_time_max = 30,
			distributor = self.distributor)
		Party.objects.clear(stock = self.bt)

		# ДТ- Дальний транзит - свободный товар, поступающий на склады Landata в период между 22 - 60 днями
		self.dt = Stock.objects.take(
			alias = self.alias + '-d-transit',
			name = self.name + ': дальний транзит',
			delivery_time_min = 25,
			delivery_time_max = 80,
			distributor = self.distributor)
		Party.objects.clear(stock = self.dt)

		# Типы цен, валюты и единицы
		self.default_unit = Unit.objects.take(alias = 'pcs', name = 'шт.')
		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')
		self.rub = Currency.objects.take(alias = 'RUB', name = 'р.', full_name = 'Российский рубль', rate = 1, quantity = 1)
		self.usd = Currency.objects.take(alias = 'USD', name = '$', full_name = 'US Dollar', rate = 60, quantity = 1)
		self.eur = Currency.objects.take(alias = 'EUR', name = 'EUR', full_name = 'Euro', rate = 80, quantity = 1)

		# Используемые ссылки
		self.url = {
			'start': 'http://www.landata.ru/forpartners/',
			'login': 'http://www.landata.ru/forpartners/',
			'price': 'http://www.landata.ru/forpartners/sklad/sklad_tranzit_online/',
			'backurl': '/index.php',
			'filter': '?vendor_code='}

	def run(self):

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		try:
			r = s.get(self.url['start'], timeout = 100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print('Ошибка: превышен интервал ожидания загрузки Cookies.')
			return False

		# Авторизуемся
		try:
			payload = {
				'AUTH_FORM': 'Y',
				'TYPE': 'AUTH',
				'backurl': self.url['backurl'],
				'USER_LOGIN': self.updater.login,
				'USER_PASSWORD': self.updater.password,
				'Login': '%C2%EE%E9%F2%E8'}
			r = s.post(
				self.url['login'],
				cookies = cookies,
				data = payload,
				allow_redirects = True,
				verify = False,
				timeout = 100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print('Ошибка: превышен интервал ожидания подтверждения авторизации.')
			return False

		# Загружаем начальную страницу каталога
		try:
			r = s.get(
				self.url['price'],
				cookies = cookies,
				allow_redirects = True,
				verify = False,
				timeout = 100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print('Ошибка: превышен интервал ожидания загрузки каталога.')
			return False

		# Получаем все ссылки
		tree = lxml.html.fromstring(r.text)
		urls = tree.xpath('//a/@href')
		del(tree)

		# Проходим по всем ссылкам
		done = []
		for url in urls:
			if self.url['filter'] in url:

				# Проверяем ссылку
				url = self.url['price'] + url
				if url in done:
					print('Страница {} уже обработана.'.format(url))
					continue

				# Загружаем страницу
				try:
					r = s.get(url, cookies = cookies, timeout = 30.0)
					tree = lxml.html.fromstring(r.text)
					print("\nЗагружена страница: " + url)
				except requests.exceptions.Timeout:
					print("Ошибка: превышен интервал ожидания загрузки страницы каталога.")
					continue

				# Парсим таблицу с товарами
				table = tree.xpath('//table[@class="table  table-striped tablevendor"]//tr')
				print("Загружено строк таблицы: {}.".format(len(table)))
				if self.parseProducts(table, url.split(self.url['filter'])[1]):
					done.append(url) # Добавляем ссылку в обработанные страницы

				# Чистим за собой
				del(r)
				del(tree)
				del(table)

				# Ждем, чтобы не получить отбой сервера
				time.sleep(1)

		return True

	def parseProducts(self, table, vendor_synonym_name):

		# Номера строк и столбцов
		num = {'headers': 10}

		# Распознаваемые слова
		word = {
			'party_article': 'Н/н',
			'product_article': 'Код',
			'product_name': 'Наименование',
			's1': 'С1',
			's2': 'C2',
			'bt': 'БТ',
			'dt': 'ДТ',
			'price': 'Цена Dealer',
			'currency_alias': 'Валюта'}

		# Валюты
		currencies = {
			'RUB': self.rub,
			'USD': self.usd,
			'EUR': self.eur}

		# Обрабатываем синоним производителя
		if vendor_synonym_name:
			vendor_synonym = VendorSynonym.objects.take(
				name = vendor_synonym_name,
				updater = self.updater,
				distributor = self.distributor)
		else: return False

		# Получаем объект производителя
		vendor = vendor_synonym.vendor
		if not vendor:
			return False

		# Проходим по строкам таблицы
		for trn, tr in enumerate(table):

			# Заголовок таблицы
			if not trn:
				for thn, th in enumerate(tr):
					if   th.text == word['party_article']:   num['party_article']   = thn
					elif th.text == word['product_article']: num['product_article'] = thn
					elif th.text == word['product_name']:    num['product_name']    = thn
					elif th.text == word['s1']:              num['s1']              = thn
					elif th.text == word['s2']:              num['s2']              = thn
					elif th.text == word['bt']:              num['bt']              = thn
					elif th.text == word['dt']:              num['dt']              = thn
					elif th.text == word['price']:           num['price']           = thn
					elif th.text == word['currency_alias']:  num['currency_alias']  = thn

				# Проверяем, все ли столбцы распознались
				if len(num) < num['headers']:
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else: print("Структура данных без изменений.")

			# Строка товара
			else:

				# Обрабатываем информацию о товаре
				product_article = tr[num['product_article']].text.strip().split('//')[0]
				product_name    = tr[num['product_name']].text.strip()
				if product_article and product_name:
					product = Product.objects.take(
						article = product_article,
						vendor = vendor,
						name = product_name,
						category = None,
						unit = self.default_unit)
				else: continue

				# Обрабатываем информацию о партиях
				party_article = tr[num['party_article']].text.strip()

				price = self.fixPrice(tr[num['price']].text)

				currency_alias = tr[num['currency_alias']].text.strip()
				if currency_alias: currency = currencies[currency_alias]
				else: currency =  None

				s1 = self.fixQuantity(tr[num['s1']].text)
				s2 = self.fixQuantity(tr[num['s2']].text)
				bt = self.fixQuantity(tr[num['bt']].text)
				dt = self.fixQuantity(tr[num['dt']].text)

				# Записываем партии
				if s1:
					party = Party.objects.make(
						product = product,
						stock=self.s1,
						price = price,
						price_type = self.dp,
						currency = currency,
						quantity = s1,
						unit = self.default_unit)
					print("{} {} = {} {}".format(product.vendor, product.article, party.price, party.currency))

				if s2:
					party = Party.objects.make(
						product = product,
						stock=self.s1,
						price = price,
						price_type = self.dp,
						currency = currency,
						quantity = s2,
						unit = self.default_unit)
					print("{} {} = {} {}".format(product.vendor, product.article, party.price, party.currency))

				if bt:
					party = Party.objects.make(
						product = product,
						stock=self.s1,
						price = price,
						price_type = self.dp,
						currency = currency,
						quantity = bt,
						unit = self.default_unit)
					print("{} {} = {} {}".format(product.vendor, product.article, party.price, party.currency))

				if dt:
					party = Party.objects.make(
						product = product,
						stock=self.s1,
						price = price,
						price_type = self.dp,
						currency = currency,
						quantity = dt,
						unit = self.default_unit)
					print("{} {} = {} {}".format(product.vendor, product.article, party.price, party.currency))

		return True


	def fixPrice(self, price):

		# Чистим
		if price:
			price = str(price).strip()
			price = price.replace(',', '.')
			price = price.replace(' ', '')

		# Преобразуем формат
		if price:
			try: price = float(price)
			except ValueError: price = None
		else:
			price = None
		return price


	def fixQuantity(self, quantity):
		if quantity:
			quantity = str(quantity).strip()
			if quantity == 'Есть': quantity = 1
			else: quantity = int(quantity)
		else: quantity = None
		return quantity
