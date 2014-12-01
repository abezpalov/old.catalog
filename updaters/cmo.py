import lxml.html
import requests
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


class Update:


	def __init__(self):

		# Инициируем переменные
		self.name = 'ЦМО'
		self.alias = 'cmo'
		self.message = ''

		try: # self.updater
			self.updater = Updater.objects.get(alias=self.alias)
		except Updater.DoesNotExist:
			self.updater = Updater(alias=self.alias, name=self.name, created=datetime.now(), modified=datetime.now(), updated=datetime.now())
			self.updater.save()

		try: # self.distributor
			self.distributor = Distributor.objects.get(alias=self.alias)
		except Distributor.DoesNotExist:
			self.distributor = Distributor(alias=self.alias, name=self.name, created=datetime.now(), modified=datetime.now())
			self.distributor.save()

		try: # self.factory
			self.stock = Stock.objects.get(alias=self.alias+'-factory')
		except Stock.DoesNotExist:
			self.stock = Stock(alias=self.alias+'-factory', name=self.name+': завод', delivery_time_min = 10, delivery_time_max = 20, created=datetime.now(), modified=datetime.now())
			self.stock.save()

		try: # self.price_type_dp
			self.price_type_dp = PriceType.objects.get(alias='RRP')
		except PriceType.DoesNotExist:
			self.price_type_dp = PriceType(alias='RRP', name='Рекомендованная розничная цена', created=datetime.now(), modified=datetime.now())
			self.price_type_dp.save()

		try: # self.currency_rub
			self.currency_rub = Currency.objects.get(alias='RUB')
		except Currency.DoesNotExist:
			self.currency_rub = Currency(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1, created=datetime.now(), modified=datetime.now())
			self.currency_rub.save()

		try: # self.default_unit
			self.default_unit = Unit.objects.get(alias='pcs')
		except Unit.DoesNotExist:
			self.default_unit = Unit(alias='pcs', name='шт.', created=datetime.now(), modified=datetime.now())
			self.default_unit.save()

		try:
			self.vendor = Vendor.objects.get(alias='cmo')
		except Vendor.DoesNotExist:
			vendor = Vendor(name=self.name, alias=self.alias, created=datetime.now(), modified=datetime.now())
			vendor.save()

		if self.updater.state: self.run()


	def run(self):

		# Создаем сессию
		s = requests.Session()

		# Загружаем общий прайс
		r = s.get('http://www.cmo.ru/catalog/price/')
		tree = lxml.html.fromstring(r.text)

		# Парсим
		table = tree.xpath("//table")[0]
		head = True

		# TODO
		for trn, tr in enumerate(table):

			# Заголовок таблицы
			if trn == 0:
				for tdn, td in enumerate(tr):
					if td.text == 'Артикул': nArticle = tdn
					elif td.text == 'Код (ID)': nCode = tdn
					elif td.text == 'Наименование продукции': nName = tdn
					elif td.text == '"Цена, RUB"': nPrice = tdn

				# Проверяем, все ли столбцы распознались
				if not nArticle == 0 or not nCode or not nName or not nPrice:
					self.message += "Ошибка структуры данных: не все столбцы опознаны.\n"
					return False

			# Категория
			elif len(tr) == 1:
				categorySynonymName = tr[0][0][0].text.strip()
				try:
					categorySynonym = CategorySynonym.objects.get(name=categorySynonymName)
				except CategorySynonym.DoesNotExist:
					categorySynonym = CategorySynonym(name=categorySynonymName, updater=self.updater, distributor=self.distributor, created=datetime.now(), modified=datetime.now())
					categorySynonym.save()

			# Товар
			elif len(tr) == 4:
				for tdn, td in enumerate(tr):
					if tdn == nArticle: article = str(td.text).strip()
					elif tdn == nCode: code = str(td.text).strip()
					elif tdn == nName:
						name = str(td[0].text).strip()
						name = name.replace('&shy;', '')
						link = td[0].get('href').strip()
					elif tdn == nPrice:
						price = str(td.text).strip()
						if price in ('Цена не найдена'): price = None
						else:
							price = price.replace('RUB', '')
							price = price.replace(' ', '')
							self.message += str(float(price)) + "\n"

				# Если нет товара, добавляем его
				if article and article != '':
					try:
						product = Product.objects.get(article=article, vendor=self.vendor)
					except Product.DoesNotExist:
						if article and name and categorySynonym.category and article != '':
							product = Product(name=name[:500], full_name=name, article=article, vendor=self.vendor, category=categorySynonym.category, unit=self.default_unit, description = '', created=datetime.now(), modified=datetime.now())
							product.save()
						else: continue
				else: continue










