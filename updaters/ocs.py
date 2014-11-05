from catalog.models import Updater
from catalog.models import Currency
from catalog.models import CategorySynonym
from datetime import date
from datetime import datetime
import lxml.html
import requests


class Update:


	def __init__(self):

		# Инициируем переменные
		self.name = 'OCS'
		self.alias = 'ocs'
		self.message = ''

		try: # self.updater
			self.updater = Updater.objects.get(alias=self.alias)
		except Updater.DoesNotExist:
			self.updater = Updater(alias=self.alias, name=self.name, created=datetime.now(), modified=datetime.now(), updated=datetime.now())
			self.updater.save()

		try: # self.currency_rub
			self.currency_rub = Currency.objects.get(alias='RUB')
		except Currency.DoesNotExist:
			self.currency_rub = Currency(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1, created=datetime.now(), modified=datetime.now())
			self.currency_rub.save()

		try: # self.currency_usd
			self.currency_usd = Currency.objects.get(alias='USD')
		except Currency.DoesNotExist:
			self.currency_usd = Currency(alias='USD', name='$', full_name='US Dollar', rate=38, quantity=1, created=datetime.now(), modified=datetime.now())
			self.currency_usd.save()

		if self.updater.state: self.run()

	def run(self):


