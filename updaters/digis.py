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
		self.name = 'Treolan'
		self.alias = 'treolan'
		self.message = ''

		# Получаем необходимые объекты
		self.distributor  = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater      = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.stock        = Stock.objects.take(alias=self.alias+'-stock', name=self.name+': склад', delivery_time_min = 3, delivery_time_max = 10, distributor=self.distributor)
		self.transit      = Stock.objects.take(alias=self.alias+'-transit', name=self.name+': транзит', delivery_time_min = 10, delivery_time_max = 40, distributor=self.distributor)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.rp           = PriceType.objects.take(alias='RP', name='Розничная цена')
		self.dp           = PriceType.objects.take(alias='DP', name='Диллерская цена')
		self.rub          = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)
		self.usd          = Currency.objects.take(alias='USD', name='$', full_name='US Dollar', rate=60, quantity=1)
		self.eur          = Currency.objects.take(alias='EUR', name='EUR', full_name='Евро', rate=80, quantity=1)

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.stock)
		Party.objects.clear(stock=self.transit)

		# Используемые ссылки
		self.url_login = ''
		self.url_price = ''
