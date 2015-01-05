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
		self.name = 'Landata'
		self.alias = 'landata'
		self.message = ''

		# Получаем необходимые объекты
		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.stock = Stock.objects.take(alias=self.alias+'-stock', name=self.name+': склад', delivery_time_min = 3, delivery_time_max = 10, distributor=self.distributor)
		self.b_transit =Stock.objects.take(alias=self.alias+'-b-transit', name=self.name+': ближний транзит', delivery_time_min = 10, delivery_time_max = 20, distributor=self.distributor)
		self.d_transit =Stock.objects.take(alias=self.alias+'-d-transit', name=self.name+': дальний транзит', delivery_time_min = 20, delivery_time_max = 60, distributor=self.distributor)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.dp = PriceType.objects.take(alias='DP', name='Диллерская цена')
		self.rrp = PriceType.objects.take(alias='RRP', name='Рекомендованная розничная цена')
		self.rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)
		self.usd = Currency.objects.take(alias='USD', name='$', full_name='US Dollar', rate=60, quantity=1)
		self.eur = Currency.objects.take(alias='EUR', name='EUR', full_name='Euro', rate=80, quantity=1)

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.stock)
		Party.objects.clear(stock=self.b_transit)
		Party.objects.clear(stock=self.d_transit)

		# Используемые ссылки
		self.url_start = 'http://www.landata.ru/forpartners/price/'
		self.url_login = 'http://www.landata.ru/forpartners/price/index.php?login=yes'
		self.url_price = 'http://www.landata.ru/tranzit/download/index.php'

	def run(self):

		import lxml.html
		import requests

		# Номера строк и столбцов
		num = {'header': 0}

		# Распознаваемые слова
		word = {
			'article': 'Артикул',
			'name': 'Наименование',
			'vendor': 'Производитель',
			'stock': 'Св.',
			'transit': 'Св.+Тр.',
			'transit_date': 'Б. Тр.',
			'price_usd': 'Цена*',
			'price_rub': 'Цена руб.**',
			'dop': 'Доп.'}

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		try:
			r = s.get(self.url_login, timeout=100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания загрузки Cookies.'
			return False

		# Авторизуемся
		try:
			payload = {
				'AUTH_FORM': 'Y',
				'TYPE': 'AUTH',
				'backurl': '/forpartners/sklad/sklad_tranzit/index.php',
				'USER_LOGIN': self.updater.login,
				'USER_PASSWORD': self.updater.password,
				'Login': '%C2%EE%E9%F2%E8'}
			r = s.post(self.url_login, cookies=cookies, data=payload, allow_redirects=True, verify=False, timeout=100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания подтверждения авторизации.'
			return False

		# Загружаем общий прайс
		try:
			r = s.get(self.url_price, cookies=cookies, allow_redirects=False, verify=False, timeout=100.0)
			tree = lxml.html.fromstring(r.text)
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания загрузки прайс-листа.'
			return False

		# TODO Спарсить!!



		self.message += 'ok\n'
		return False
