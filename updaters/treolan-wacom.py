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
		self.parent_name = 'Treolan'
		self.parent_alias = 'treolan'
		self.name = 'Treolan: Wacom на заказ'
		self.alias = 'treolan-wacom'
		self.message = ''

		# Получаем необходимые объекты
		self.distributor = Distributor.objects.take(alias=self.parent_alias, name=self.parent_name)
		self.parent_updater = Updater.objects.take(alias=self.parent_alias, name=self.parent_name, distributor=self.distributor)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.factory = Stock.objects.take(alias=self.alias+'-wacom-factory', name=self.name+': Wacom на заказ', delivery_time_min = 30, delivery_time_max = 60, distributor=self.distributor)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.price_type_dp = PriceType.objects.take(alias='DP', name='Диллерская цена')
		self.rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)
		self.usd = Currency.objects.take(alias='USD', name='$', full_name='US Dollar', rate=60, quantity=1)

		# Забираем параметры доступа у родительского загрузчика
		if not self.updater.login and self.parent_updater.login:
			self.updater.login = self.parent_updater.login
			self.updater.save()
		if not self.updater.password and self.parent_updater.password:
			self.updater.password = self.parent_updater.password
			self.updater.save()

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.factory)

		# Используемые ссылки
		self.url_login = 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F'
		self.url_price = 'https://b2b.treolan.ru/FullPriceListFiles'


	def run(self):






		return False
