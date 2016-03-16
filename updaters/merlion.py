import requests
from lxml import etree
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


	name = 'Merlion'
	alias = 'merlion'


	def __init__(self):

		# Поставщик
		self.distributor = Distributor.objects.take(
			alias = self.alias,
			name  = self.name)

		# Загрузчик
		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = self.distributor)

		# Склад в Самаре
		self.stock_samara = Stock.objects.take(
			alias             = self.alias + '-samara-stock',
			name              = self.name+': Склад в Самаре',
			delivery_time_min = 1,
			delivery_time_max = 3,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stock_samara)

		# Склад в Москве
		self.stock_moscow = Stock.objects.take(
			alias             = self.alias + '-moscow-stock',
			name              = self.name+': склад в Москве',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stock_moscow)

		# Склад в Москве (Чехов)
		self.stock_chehov = Stock.objects.take(
			alias             = self.alias + '-chehov-stock',
			name              = self.name + ': склад в Москве (Чехов)',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stock_chehov)

		# Склад в Москве (Быково)
		self.stock_bykovo = Stock.objects.take(
			alias             = self.alias + '-bykovo-stock',
			name              = self.name + ': склад в Москве (Быково)',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stock_bykovo)

		# Склад в Москве (склад доставки)
		self.stock_dostavka = Stock.objects.take(
			alias             = self.alias + '-dostavka-stock',
			name              = self.name+': склад в Москве (склад доставки)',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stock_dostavka)

		# Ближний транзит
		self.transit_b = Stock.objects.take(
			alias             = self.alias + '-b-transit',
			name              = self.name + ': ближний транзит',
			delivery_time_min = 10,
			delivery_time_max = 20,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.transit_b)

		# Дальний транзит
		self.transit_d = Stock.objects.take(
			alias             = self.alias + '-d-transit',
			name              = self.name + ': дальний транзит',
			delivery_time_min = 20,
			delivery_time_max = 60,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.transit_d)

		# Единица измерения
		self.default_unit = Unit.objects.take(alias = 'pcs', name = 'шт.')

		# Тип цены
		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')

		# Валюты
		self.rub = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  = 1)
		self.usd = Currency.objects.take(
			alias     = 'USD',
			name      = '$',
			full_name = 'US Dollar',
			rate      = 60,
			quantity  = 1)

		# Используемые ссылки
		self.url_login = 'https://b2b.merlion.com/'
		self.url_price = (
			'https://b2b.merlion.com/?action=Y3F86565&action1=YD56AF97&lol=84bbfe81dd1cd7966229740eac26ddae&type=xml',
			'https://b2b.merlion.com/?action=Y3F86565&action1=YD56AF97&lol=95a71288d806dfa41c09d2bfacbb5dd6&type=xml',)


	def run(self):

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		try:
			r = s.get(self.url_login, timeout=100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания загрузки Cookies.")
			return False

		# Авторизуемся
		try:
			payload = {
				'client': self.updater.login.split('|')[0],
				'login': self.updater.login.split('|')[1],
				'password': self.updater.password,
				'Ok': '%C2%EE%E9%F2%E8'}
			r = s.post(self.url_login, cookies=cookies, data=payload, allow_redirects=True, verify=False, timeout=100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания подтверждения авторизации.")
			return False

		# Получаем актуальные ссылки на прайс-листы
		# TODO


		# Получаем архив с прайс-листом
		for url in self.url_price:
#			try:
			r = s.get(url, cookies = cookies)
			data = self.getData(r)
			tree = etree.parse(data)
			if self.parsePrice(tree):
				del(tree)
			else:
				print("Ошибка: парсинг невозможен.")
				return False
#			except:
#				print("Неизвестная ошибка: требуется отладка.")
#				return False

		return True


	def getData(self, r):

		from io import BytesIO
		from catalog.lib.zipfile import ZipFile

		try:
			zip_data = ZipFile(BytesIO(r.content))
			xml_data = zip_data.open(zip_data.namelist()[0])
		except:
			return False

		print("Получен прайс-лист: " + zip_data.namelist()[0])

		del zip_data
		return xml_data


	def parsePrice(self, tree):

		# Словарь для составления имени синонима категории
		g = {0: '', 1: '', 2: ''}

		# Распознаваемые слова
		word = {
			'party_article': 'No',
			'product_name': 'Name',
			'vendor_synonym_name': 'Brand',
			'product_article': 'PartNo',
			'price_usd': 'Price',
			'price_rub': 'PriceR',
			'stock_chehov': 'Avail_SV_CHEHOV',
			'stock_bykovo': 'Avail_SV_BYKOVO',
			'stock_dostavka': 'Avail_DOSTAVKA',
			'stock_samara': 'Avail_RSMR',
			'stock_moscow': 'Avail_MSK',
			'transit_b': 'Avail_Expect',
			'transit_d': 'Avail_ExpectNext',
			'transit_date': 'Date_ExpectNext',
			'pack_minimal': 'Min_Pack',
			'pack': 'Pack',
			'volume': 'Vol',
			'weight': 'WT',
			'warranty': 'Warranty',
			'status': 'Status',
			'maction': 'MAction',
			'rrp': 'RRP',
			'rrp_date': 'RRP_Date'}

		for g1 in tree.xpath('.//G1'):
			for g2_n, g2 in enumerate(g1):
				if not g2_n:
					g[0] = g2.text.strip()
				else:
					for g3_n, g3 in enumerate(g2):
						if not g3_n:
							g[1] = g3.text.strip()
						else:

							for item_n, item in enumerate(g3):
								if not item_n:
									# Получаем объект синонима категории
									g[2] = item.text.strip()
									category_synonym_name = "{} | {} | {}".format(g[0], g[1], g[2])
									category_synonym = CategorySynonym.objects.take(
										name = category_synonym_name,
										updater = self.updater,
										distributor = self.distributor)
								else:

									# Обнуляем значения
									party_article        = None
									product_name         = None
									vendor_synonym_name  = None
									product_article      = None
									price_usd            = None
									price_rub            = None

									stock_chehov   = None
									stock_bykovo   = None
									stock_dostavka = None
									stock_samara   = None
									stock_moscow   = None
									transit_b      = None
									transit_d      = None
									transit_date   = None

									pack_minimal = None
									pack         = None
									volume       = None
									weight       = None
									warranty     = None
									status       = None
									maction      = None
									rrp          = None
									rrp_date     = None

									# Получаем информацию о товаре
									for attr in item:
										if   attr.tag == word['party_article']:       party_article = attr.text
										elif attr.tag == word['product_name']:        product_name = attr.text
										elif attr.tag == word['vendor_synonym_name']: vendor_synonym_name = attr.text
										elif attr.tag == word['product_article']:     product_article = attr.text
										elif attr.tag == word['price_usd']:           price_usd = self.fixPrice(attr.text)
										elif attr.tag == word['price_rub']:           price_rub = self.fixPrice(attr.text)
										elif attr.tag == word['stock_chehov']:        stock_chehov = self.fixQuantity(attr.text)
										elif attr.tag == word['stock_bykovo']:        stock_bykovo = self.fixQuantity(attr.text)
										elif attr.tag == word['stock_dostavka']:      stock_dostavka = self.fixQuantity(attr.text)
										elif attr.tag == word['stock_samara']:        stock_samara = self.fixQuantity(attr.text)
										elif attr.tag == word['stock_moscow']:        stock_moscow = self.fixQuantity(attr.text)
										elif attr.tag == word['transit_b']:           transit_b = self.fixQuantity(attr.text)
										elif attr.tag == word['transit_d']:           transit_d = self.fixQuantity(attr.text)
										elif attr.tag == word['transit_date']:        transit_date = attr.text
										elif attr.tag == word['pack_minimal']:        pack_minimal = attr.text
										elif attr.tag == word['pack']:                pack = attr.text
										elif attr.tag == word['volume']:              volume = attr.text
										elif attr.tag == word['weight']:              weight = attr.text
										elif attr.tag == word['warranty']:            warranty = attr.text
										elif attr.tag == word['status']:              status = attr.text
										elif attr.tag == word['maction']:             maction = attr.text
										elif attr.tag == word['rrp']:                 rrp = attr.text
										elif attr.tag == word['rrp_date']:            rrp_date = attr.text

									# Обрабатываем синоним производителя
									if vendor_synonym_name:
										vendor_synonym = VendorSynonym.objects.take(
											name        = vendor_synonym_name,
											updater     = self.updater,
											distributor = self.distributor)
									else: continue

									# Получаем объект товара
									if product_article and product_name and vendor_synonym.vendor:
										product = Product.objects.take(
											article  = product_article,
											vendor   = vendor_synonym.vendor,
											name     = product_name,
											category = category_synonym.category,
											unit     = self.default_unit)
									else: continue

									if price_usd:
										price    = price_usd
										currency = self.usd
									elif price_rub:
										price    = price_rub
										currency = self.rub
									else:
										price    = None
										currency = self.usd

									# Записываем партии
									if stock_chehov:
										party = Party.objects.make(
											product    = product,
											stock      = self.stock_chehov,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = stock_chehov,
											unit       = self.default_unit)
										print("{} {} = {} {}".format(product.vendor.name, product.article, party.price, party.currency.alias))

									if stock_bykovo:
										party = Party.objects.make(
											product    = product,
											stock      = self.stock_bykovo,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = stock_bykovo,
											unit       = self.default_unit)
										print("{} {} = {} {}".format(product.vendor.name, product.article, party.price, party.currency.alias))

									if stock_samara:
										party = Party.objects.make(
											product    = product,
											stock      = self.stock_samara,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = stock_samara,
											unit       = self.default_unit)
										print("{} {} = {} {}".format(product.vendor.name, product.article, party.price, party.currency.alias))

									if stock_moscow:
										party = Party.objects.make(
											product = product,
											stock      = self.stock_moscow,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = stock_moscow,
											unit       = self.default_unit)
										print("{} {} = {} {}".format(product.vendor.name, product.article, party.price, party.currency.alias))

									if transit_b:
										party = Party.objects.make(
											product    = product,
											stock      = self.transit_b,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = transit_b,
											unit       = self.default_unit)
										print("{} {} = {} {}".format(product.vendor.name, product.article, party.price, party.currency.alias))

									if transit_d:
										party = Party.objects.make(
											product    = product,
											stock      = self.transit_d,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = transit_d,
											unit       = self.default_unit)
										print("{} {} = {} {}".format(product.vendor.name, product.article, party.price, party.currency.alias))

		print("Обработка прайс-листа завершена.")
		return True


	def fixPrice(self, price):
		price = str(price).strip()
		price = price.replace(',', '.')
		price = price.replace(' ', '')
		if price: price = float(price)
		else: price = None
		return price


	def fixQuantity(self, quantity):
		quantity = str(quantity).strip()
		if quantity in ('', 'call'): quantity = 0
		elif quantity in('+', '+ '): quantity = 5
		elif quantity in ('++', '++ '): quantity = 10
		elif quantity in ('+++', '+++ '): quantity = 50
		elif quantity in ('++++', '++++ '): quantity = 100
		else: quantity = int(quantity)
		return quantity
