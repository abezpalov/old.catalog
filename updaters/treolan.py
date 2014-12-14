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
		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.stock = Stock.objects.take(alias=self.alias+'-stock', name=self.name+': склад', delivery_time_min = 3, delivery_time_max = 10, distributor=self.distributor)
		self.transit =Stock.objects.take(alias=self.alias+'-transit', name=self.name+': транзит', delivery_time_min = 10, delivery_time_max = 40, distributor=self.distributor)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.price_type_dp = PriceType.objects.take(alias='DP', name='Диллерская цена')
		self.rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)
		self.usd = Currency.objects.take(alias='USD', name='$', full_name='US Dollar', rate=60, quantity=1)

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.stock)
		Party.objects.clear(stock=self.transit)

		# Используемые ссылки
		self.url_login = 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F'
		self.url_price = 'https://b2b.treolan.ru/Catalog/SearchToExcel?&comodity=true&withMarketingProgramsOnly=false&availableAtStockOnly=false&rusDescription=true&condition=0&catalogProductsOnly=true&order=0&getExcel=true&searchBylink=false&take=50&skip=0'

	def run(self):

		import lxml.html
		import requests

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		r = s.get(self.url_login)
		cookies = r.cookies

		# Авторизуемся
		payload = {'UserName': self.updater.login, 'Password': self.updater.password, 'RememberMe': 'false'}
		r = s.post(self.url_login, cookies=cookies, data=payload, allow_redirects=True, verify=False)
		cookies = r.cookies

		# Загружаем общий прайс
		r = s.get(self.url_price, cookies=cookies, allow_redirects=False, verify=False)
		tree = lxml.html.fromstring(r.text)

		# Парсим
		table = tree.xpath("//table")[0]
		head = True
		for trn, tr in enumerate(table):

			# Заголовок таблицы
			if trn == 0:
				for tdn, td in enumerate(tr):
					if td[0].text == 'Артикул': nArticle = tdn
					elif td[0].text == 'Наименование': nName = tdn
					elif td[0].text == 'Производитель': nVendor = tdn
					elif td[0].text == 'Св.': nStock = tdn
					elif td[0].text == 'Св.+Тр.': nTransit = tdn
					elif td[0].text == 'Б. Тр.': nTransitDate = tdn
					elif td[0].text == 'Цена*': nPriceUSD = tdn
					elif td[0].text == 'Цена руб.**': nPriceRUB = tdn
					elif td[0].text == 'Доп.': nDop = tdn

				# Проверяем, все ли столбцы распознались
				if not nArticle == 0 or not nName or not nVendor or not nStock or not nTransit or not nPriceUSD or not nPriceUSD or not nPriceRUB:
					self.message += "Ошибка структуры данных: не все столбцы опознаны.\n"
					return False
				else: self.message += "Структура данных без изменений.\n"

			# Категория
			elif len(tr) == 1:
				categorySynonym = CategorySynonym.objects.take(name=tr[0][0].text.strip(), updater=self.updater, distributor=self.distributor)

			# Товар
			elif len(tr) == 9:
				for tdn, td in enumerate(tr):
					if tdn == nArticle: article = str(td.text).strip()
					elif tdn == nName: name = str(td.text).strip()
					elif tdn == nVendor: vendorSynonymName = str(td.text).strip()
					elif tdn == nStock: stock = self.fixQuantity(str(td.text).strip())
					elif tdn == nTransit: transit = self.fixQuantity(str(td.text).strip()) - stock
					elif tdn == nTransitDate: transitDate = str(td.text).strip()
					elif tdn == nPriceUSD: priceUSD = self.fixPrice(str(td.text).strip())
					elif tdn == nPriceRUB: priceRUB = self.fixPrice(str(td.text).strip())
					elif tdn == nDop: dop = str(td.text).strip()

				# Обрабатываем синоним производителя
				if vendorSynonymName != '':
					vendorSynonym = VendorSynonym.objects.take(name=vendorSynonymName, updater=self.updater, distributor=self.distributor)
				else: continue

				# Если нет товара, добавляем его
				if article and vendorSynonym.vendor and article != '':
					try:
						product = Product.objects.get(article=article, vendor=vendorSynonym.vendor)
						if not product.category and categorySynonym.category:
							product.category = categorySynonym.category
							product.save()
					except Product.DoesNotExist:
						# Проверяем необходимые даннные для добавления товара в базу
						if article and name and vendorSynonym.vendor and article != '':
							product = Product()
							product.setName(name)
							product.setArticle(article)
							product.vendor = vendorSynonym.vendor
							product.category = categorySynonym.category
							product.unit = self.default_unit
							product.created = datetime.now()
							product.modified = datetime.now()
							product.save()
							self.message += "Добавлен продукт: " + product.name[:100] + ".\n"
						else: continue
				else: continue

				# Цена в долларах
				if priceUSD != '':
					party = Party.objects.make(product=product, stock=self.stock, price = priceUSD, price_type = self.price_type_dp, currency = self.usd, quantity = stock, unit = self.default_unit)
					party = Party.objects.make(product=product, stock=self.stock, price = priceUSD, price_type = self.price_type_dp, currency = self.usd, quantity = transit, unit = self.default_unit)

				# Цена в рублях
				if priceRUB != '':
					party = Party.objects.make(product=product, stock=self.stock, price = priceRUB, price_type = self.price_type_dp, currency = self.rub, quantity = stock, unit = self.default_unit)
					party = Party.objects.make(product=product, stock=self.stock, price = priceRUB, price_type = self.price_type_dp, currency = self.rub, quantity = transit, unit = self.default_unit)

		return True

	def fixPrice(self, price):
		price = price.replace(',', '.')
		price = price.replace(' ', '')
		return price

	def fixQuantity(self, quantity):
		if quantity in ('', '0*'): quantity = 0
		elif quantity == 'мало': quantity = 5
		elif quantity == 'много': quantity = 10
		elif quantity == 'Поставка\n 7 дней': quantity = -1
		else: quantity = int(quantity)
		return quantity
