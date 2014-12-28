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
		self.name = 'ЦМО'
		self.alias = 'cmo'
		self.message = ''

		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.factory = Stock.objects.take(alias=self.alias+'-factory', name=self.name+': завод', delivery_time_min = 10, delivery_time_max = 20, distributor=self.distributor)
		self.vendor = Vendor.objects.take(alias=self.alias, name=self.name)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.rp = PriceType.objects.take(alias='RP', name='Розничная цена')
		self.rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.factory)

		# Используемые ссылки
		self.url = 'http://www.cmo.ru/catalog/price/'

	def run(self):

		import lxml.html
		import requests

		# Номера строк и столбцов
		num = {'header': 0}

		# Распознаваемые слова
		word = {
			'article': 'Артикул',
			'code': 'Код (ID)',
			'name': 'Наименование продукции',
			'price': '"Цена, RUB"'}

		# Создаем сессию
		s = requests.Session()

		# Загружаем данные
		try:
			r = s.get(self.url, timeout=100.0)
			tree = lxml.html.fromstring(r.text)
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания загрузки.'
			return False

		# Парсим
		try:
			table = tree.xpath("//table")[0]
		except IndexError:
			self.message += "Не получилось загрузить прайс-лист.\n"
			self.message += "Проверьте параметры доступа.\n"
			return False

		for trn, tr in enumerate(table):

			# Заголовок таблицы
			if trn == num['header']:
				for tdn, td in enumerate(tr):
					if   td.text == word['article']: num['article'] = tdn
					elif td.text == word['code']:    num['code'] = tdn
					elif td.text == word['name']:    num['name'] = tdn
					elif td.text == word['price']:   num['price'] = tdn

				# Проверяем, все ли столбцы распознались
				if not num['article'] == 0 or not num['code'] or not num['name'] or not num['price']:
					self.message += "Ошибка структуры данных: не все столбцы опознаны.\n"
					return False
				else: self.message += "Структура данных без изменений.\n"

			# Категория
			elif len(tr) == 1:
				category_synonym = CategorySynonym.objects.take(name=tr[0][0][0].text.strip(), updater=self.updater, distributor=self.distributor)

			# Товар
			elif len(tr) == 4:

				article = str(tr[num['article']].text).strip()
				code    = str(tr[num['code']].text).strip()
				name    = str(tr[num['name']][0].text).strip()
				link    = str(tr[num['name']][0].get('href')).strip()
				price   = self.fixPrice(tr[num['price']].text)

				# Если артикул не указан - используем код товара
				if not article and code: article = code

				# Получаем объект товара
				if article and name:
					product = Product.objects.take(article=article, vendor=self.vendor, name=name, category = category_synonym.category, unit = self.default_unit)
				else: continue

				# Добавляем партии
				party = Party.objects.make(product=product, stock=self.factory, price=price, price_type = self.rp, currency = self.rub, quantity = -1, unit = self.default_unit)
				self.message += product.article + ' = ' + str(party.price) + ' ' + party.currency.alias + ' ' + party.price_type.alias + '\n'

		return True


	def fixPrice(self, price):

		price = str(price).strip()
		if price in ('Цена не найдена'): price = None
		else:
			price = price.replace('RUB', '')
			price = price.replace(' ', '')
			price = float(price)
		return price
