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

		# Получаем перечень всех продуктов
		products = Product.objects.all()

		for product in products:
			self.message += product.name + '\n'

			parties = Party.objects.filter(product=product)

			# Получаем цену
			try:
				price = Price.objects.get(product=product)
			except Price.DoesNotExist:
				price = Price()
				price.product = product
				price.created = datetime.now()
			finally:
				price.price = 0

			# Вычисляем новую цену
			if 0 == len(parties):
				price.price = 0
			else:
				s = 0 # Сумма цен
				n = 0 # Количество значащих цен
				for party in parties:
					p = party.price * party.currency.rate / party.currency.quantity * party.price_type.multiplier
					s += p
					if p != 0: n += 1
				if 0 == n :
					price.price = 0
				else:
					price.price = s / n

				price.price_type = self.rp
				price.currency = self.rub
				price.modified = datetime.now()
				price.save()

