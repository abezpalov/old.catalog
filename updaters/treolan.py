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
		self.name = 'Treolan'
		self.alias = 'treolan'
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

		try: # self.stock
			self.stock = Stock.objects.get(alias=self.alias+'-stock')
		except Stock.DoesNotExist:
			self.stock = Stock(alias=self.alias+'-stock', name=self.name+': склад', delivery_time_min = 3, delivery_time_max = 10, created=datetime.now(), modified=datetime.now())
			self.stock.save()

		try: # self.transit
			self.transit = Stock.objects.get(alias=self.alias+'-transit')
		except Stock.DoesNotExist:
			self.transit = Stock(alias=self.alias+'-transit', name=self.name+': транзит', delivery_time_min = 10, delivery_time_max = 40, created=datetime.now(), modified=datetime.now())
			self.transit.save()

		try: # self.price_type_dp
			self.price_type_dp = PriceType.objects.get(alias='DP')
		except PriceType.DoesNotExist:
			self.price_type_dp = PriceType(alias='DP', name='Диллерская цена', created=datetime.now(), modified=datetime.now())
			self.price_type_dp.save()

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

		try: # self.default_unit
			self.default_unit = Unit.objects.get(alias='pcs')
		except Unit.DoesNotExist:
			self.default_unit = Unit(alias='pcs', name='шт.', created=datetime.now(), modified=datetime.now())
			self.default_unit.save()

		if self.updater.state: self.run()


	def run(self):

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		url = 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2f'
		r = s.get(url)
		cookies = r.cookies

		# Авторизуемся
		url = 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F'
		payload = {'UserName': 'GST_zhd', 'Password': 'uatokhjt', 'RememberMe': 'false'}
		r = s.post(url, cookies=cookies, data=payload, allow_redirects=True, verify=False)
		cookies = r.cookies

		# Загружаем общий прайс
		url = 'https://b2b.treolan.ru/Catalog/SearchToExcel?&comodity=true&withMarketingProgramsOnly=false&availableAtStockOnly=false&rusDescription=true&condition=0&catalogProductsOnly=true&order=0&getExcel=true&searchBylink=false&take=50&skip=0'
		r = s.get(url, cookies=cookies, allow_redirects=False, verify=False)
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

			# Категория
			elif len(tr) == 1:
				# Обрабатываем синоним категории
				categorySynonymName = tr[0][0].text.strip()
				try:
					categorySynonym = CategorySynonym.objects.get(name=categorySynonymName)
				except CategorySynonym.DoesNotExist:
					categorySynonym = CategorySynonym(name=categorySynonymName, updater=self.updater, distributor=self.distributor, created=datetime.now(), modified=datetime.now())
					categorySynonym.save()

			# Товар
			elif len(tr) == 9:
				for tdn, td in enumerate(tr):
					if tdn == nArticle: article = str(td.text).strip()
					elif tdn == nName: name = str(td.text).strip()
					elif tdn == nVendor: vendorSynonymName = str(td.text).strip()
					elif tdn == nStock: stock = str(td.text).strip()
					elif tdn == nTransit: transit = str(td.text).strip()
					elif tdn == nTransitDate: transitDate = str(td.text).strip()
					elif tdn == nPriceUSD: priceUSD = str(td.text).strip()
					elif tdn == nPriceRUB: priceRUB = str(td.text).strip()
					elif tdn == nDop: dop = str(td.text).strip()

				# Обрабатываем синоним производителя
				if vendorSynonymName != "":
					try:
						vendorSynonym = VendorSynonym.objects.get(name=vendorSynonymName)
					except VendorSynonym.DoesNotExist:
						vendorSynonym = VendorSynonym(name=vendorSynonymName, updater=self.updater, created=datetime.now(), modified=datetime.now())
						vendorSynonym.save()

				# Проверяем наличие товара в базе
				if article and vendorSynonym.vendor and article != '':
					try:
						product = Product.objects.get(article=article, vendor=vendorSynonym.vendor)
					except Product.DoesNotExist:

						# Проверяем необходимые даннные для добавления товара в базу
						if article and name and categorySynonym.category and vendorSynonym.vendor and article != '':
							product = Product(name=name[:500], full_name=name, article=article, vendor=vendorSynonym.vendor, category=categorySynonym.category, unit=self.default_unit, description = '', created=datetime.now(), modified=datetime.now())
							product.save()
						else: continue
				else: continue

				# TODO Обрабатываем партии

				# Склад
				if stock in ('', '0*'): stock = 0
				elif stock == 'мало': stock = 5
				elif stock == 'много': stock = 10
				else: stock = int(stock)

				# Транзит
				if transit in ('', '0*'): transit = 0
				elif transit == 'мало': transit = 5 - stock
				elif transit == 'много': transit = 10 - stock
				else: transit = int(transit) - stock

				# Цена в долларах
				self.message += 'priceUSD = ' + priceUSD + "\n"
				priceUSD = priceUSD.replace(',', '.')
				priceUSD = priceUSD.replace(' ', '')
				if priceUSD != '':
					float(priceUSD)
					try:

						# Склад
						party = Party.objects.get(product=product, stock=self.stock)
						party.price = priceUSD
						party.price_type = self.price_type_dp
						party.currency = self.currency_usd
						party.quantity = stock
						party.unit = self.default_unit
						party.comment = ''
						party.state = True
						party.modified = datetime.now()
						party.save()

						# Транзит
						party = Party.objects.get(product=product, stock=self.transit)
						party.price = priceUSD
						party.price_type = self.price_type_dp
						party.currency = self.currency_usd
						party.quantity = transit
						party.unit = self.default_unit
						party.comment = ''
						party.state = True
						party.modified = datetime.now()
						party.save()

					except Party.DoesNotExist:

						# Склад
						party = Party(
							product=product,
							stock=self.stock,
							price = priceUSD,
							price_type = self.price_type_dp,
							currency = self.currency_usd,
							quantity = stock,
							unit = self.default_unit,
							comment = '',
							created=datetime.now(),
							modified=datetime.now())
						party.save()

						# Транзит
						party = Party(
							product=product,
							stock=self.transit,
							price = priceUSD,
							price_type = self.price_type_dp,
							currency = self.currency_usd,
							quantity = transit,
							unit = self.default_unit,
							comment = '',
							created=datetime.now(),
							modified=datetime.now())
						party.save()

				# Цена в рублях
				self.message += 'priceRUB = ' + priceRUB + "\n"
				priceRUB = priceRUB.replace(',', '.')
				priceRUB = priceRUB.replace(' ', '')
				if priceRUB != '':
					float(priceRUB)
					try:

						# Склад
						party = Party.objects.get(product=product, stock=self.stock)
						party.price = priceRUB
						party.price_type = self.price_type_dp
						party.currency = self.currency_rub
						party.quantity = stock
						party.unit = self.default_unit
						party.comment = ''
						party.state = True
						party.modified = datetime.now()
						party.save()

						# Транзит
						party = Party.objects.get(product=product, stock=self.transit)
						party.price = priceRUB
						party.price_type = self.price_type_dp
						party.currency = self.currency_rub
						party.quantity = transit
						party.unit = self.default_unit
						party.comment = ''
						party.state = True
						party.modified = datetime.now()
						party.save()

					except Party.DoesNotExist:

						# Склад
						party = Party(
							product=product,
							stock=self.stock,
							price = priceRUB,
							price_type = self.price_type_dp,
							currency = self.currency_rub,
							quantity = stock,
							unit = self.default_unit,
							comment = '',
							created=datetime.now(),
							modified=datetime.now())
						party.save()

						# Транзит
						party = Party(
							product=product,
							stock=self.transit,
							price = priceRUB,
							price_type = self.price_type_dp,
							currency = self.currency_rub,
							quantity = transit,
							unit = self.default_unit,
							comment = '',
							created=datetime.now(),
							modified=datetime.now())
						party.save()

		# Обрабатываем цены

		# Отмечаемся и уходим
		self.updater.updated = datetime.now()
		self.updater.save()
		return True
