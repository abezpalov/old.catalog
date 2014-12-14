from datetime import date
from datetime import datetime
from catalog.models import Updater
from catalog.models import Currency
from catalog.models import Unit
from catalog.models import Product
from catalog.models import Party
from catalog.models import PriceType
from catalog.models import Price


class Runner:

	def __init__(self):

		# Инициируем переменные
		self.name = 'Обновление цен'
		self.alias = 'price-update'
		self.message = ''

		# Получаем необходимые объекты
		self.updater = Updater.objects.take(alias=self.alias, name=self.name)
		self.rp = PriceType.objects.take(alias='RP', name='Розничная цена')
		self.rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)

	def run(self):

		self.message = 'Тест запуска'

		Price.objects.recalculate()

