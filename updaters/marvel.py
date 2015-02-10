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
		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)

		# Объект загрузчика
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)

		# Склад
		self.stock = Stock.objects.take(
			alias = self.alias+'-stock',
			name = self.name + ': склад',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor = self.distributor)
		Party.objects.clear(stock=self.stock)

		# Ближний транзит
		self.transit_b = Stock.objects.take(
			alias = self.alias+'-b-transit',
			name = self.name + ': ближний транзит',
			delivery_time_min = 10,
			delivery_time_max = 20,
			distributor = self.distributor)
		Party.objects.clear(stock=self.transit_b)

		# Дальний транзит
		self.transit_d = Stock.objects.take(
			alias = self.alias+'-d-transit',
			name = self.name + ': дальний транзит',
			delivery_time_min = 20,
			delivery_time_max = 60,
			distributor = self.distributor)
		Party.objects.clear(stock=self.transit_d)

		# Единица измерения
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')

		# Тип цены
		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')

		# Валюты
		self.rub = Currency.objects.take(alias = 'RUB', name = 'р.', full_name = 'Российский рубль', rate = 1, quantity = 1)
		self.usd = Currency.objects.take(alias = 'USD', name = '$', full_name = 'US Dollar', rate = 60, quantity = 1)
		self.eur = Currency.objects.take(alias = 'EUR', name = 'EUR', full_name = 'Euro', rate = 80, quantity = 1)

		# Используемая ссылки
		self.url = 'https://b2b.marvel.ru/Api/'
		self.key = ''
		self.task = {
			'categories': 'GetCatalogCategories'}
		self.request_format = {'xml': '0', 'json': '1'}
		self.cookies = None

	def run(self):

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False

		categories = self.getInfo('categories', 'json')



		# TODO Next

		return False

	# Функция запроса к API дистрибьютора
	def getInfo(self, task, request_format, number_of_attempts = 10):

		# Создаем сессию
		import requests
		s = requests.Session()

		# Получаем каталог
		url = '{url}{task}?user={login}&password={password}&secretKey={key}&responseFormat={request_format}'.format(
			url            = self.url,
			task           = self.task[task],
			login          = self.updater.login,
			password       = self.updater.password,
			key            = self.key,
			request_format = self.request_format[request_format])

		# TODO TEST
		print(url)

		r = s.post(url, cookies = self.cookies, allow_redirects = True, verify = False, timeout = 60)

		# TODO TEST
		print(r.text[0:5000])



		# TODO Next
		return False


