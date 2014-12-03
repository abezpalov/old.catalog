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

		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.factory = Stock.objects.take(alias=self.alias+'-factory', name=self.name+': завод', delivery_time_min = 10, delivery_time_max = 20, distributor=self.distributor)
		self.vendor = Vendor.objects.take(alias=self.alias, name=self.name)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.price_type_dp = PriceType.objects.take(alias='RRP', name='Рекомендованная розничная цена')
		self.currency_rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)

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










