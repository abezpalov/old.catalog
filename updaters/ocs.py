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
		self.name = 'OCS'
		self.alias = 'ocs'
		self.message = ''

		# Получаем необходимые объекты
		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.stock_s = Stock.objects.take(alias=self.alias+'-stock-s', name=self.name+': склад в Самаре', delivery_time_min = 1, delivery_time_max = 3, distributor=self.distributor)
		self.stock_m = Stock.objects.take(alias=self.alias+'-stock-m', name=self.name+': склад в Москве', delivery_time_min = 3, delivery_time_max = 10, distributor=self.distributor)
		self.transit_b =Stock.objects.take(alias=self.alias+'-transit-b', name=self.name+': ближний транзит', delivery_time_min = 10, delivery_time_max = 20, distributor=self.distributor)
		self.transit_d =Stock.objects.take(alias=self.alias+'-transit-d', name=self.name+': дальний транзит', delivery_time_min = 20, delivery_time_max = 40, distributor=self.distributor)
		self.transit_u =Stock.objects.take(alias=self.alias+'-transit-u', name=self.name+': транзит с неопределенным сроком', delivery_time_min = 20, delivery_time_max = 80, distributor=self.distributor)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.price_type_dp = PriceType.objects.take(alias='DP', name='Диллерская цена')
		self.rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)
		self.usd = Currency.objects.take(alias='USD', name='$', full_name='US Dollar', rate=60, quantity=1)
		self.eur = Currency.objects.take(alias='EUR', name='EUR', full_name='Euro', rate=80, quantity=1)


		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.stock_s)
		Party.objects.clear(stock=self.stock_m)
		Party.objects.clear(stock=self.transit_b)
		Party.objects.clear(stock=self.transit_d)
		Party.objects.clear(stock=self.transit_u)

		# Используемые ссылки
		self.url = 'https://b2bservice.ocs.ru/b2b.asmx/'


	def run(self):

		import requests









		# Создаем сессию
		s = requests.Session()

		# Получаем каталоги
#		payload = {'Login': self.updater.login, 'Token': self.updater.password}

# Content-Type: application/json; charset=utf-8

		headers = {'Content-Type': 'application/json; charset=utf-8'}
		payload = '{"Login":"' + self.updater.login + '","Token":"' + self.updater.password + '"}"'
		try:
			r = s.get(self.url+'GetCatalog', data=payload, headers=headers, allow_redirects=True, verify=False, timeout=100.0)
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания загрузки Cookies.'
			return False

		self.message = r.text






		return False
