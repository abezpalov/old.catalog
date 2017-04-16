import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

	name  = 'Merlion'
	alias = 'merlion'

	url = {
			'start' : 'https://b2b.merlion.com/',
			'login' : 'https://b2b.merlion.com/',
			'links' : 'https://b2b.merlion.com/?action=Y3F86565&action1=YC2E8B7C',
			'base'  : 'https://b2b.merlion.com/'}


	def __init__(self):

		super().__init__()

		self.stock_samara = self.take_stock('samara-stock', 'склад в Самаре', 1, 3)
		self.stock_moscow = self.take_stock('moscow-stock', 'склад в Москве', 3, 10)
		self.stock_chehov = self.take_stock('chehov-stock', 'склад в Москве (Чехов)', 3, 10)
		self.stock_bykovo = self.take_stock('bykovo-stock', 'склад в Москве (Быково)', 3, 10)
		self.stock_dostavka = self.take_stock('dostavka-stock', 'склад в Москве (склад доставки)', 3, 10)
		self.transit_b = self.take_stock('b-transit', 'ближний транзит', 10, 20)
		self.transit_d = self.take_stock('d-transit', 'дальний транзит', 20, 60)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		payload = {
			'client'   : self.updater.login.split('|')[0],
			'login'    : self.updater.login.split('|')[1],
			'password' : self.updater.password,
			'Ok'       : '%C2%EE%E9%F2%E8'}
		self.login(payload)

		# Получаем ссылки на прайс-листы
		tree = self.load_html(self.url['links'])

		forms = tree.xpath('//form')

		for form in forms:

			url = self.url['base']

			elements = form.xpath('.//input')

			for n, element in enumerate(elements):

				if element.name and element.value:

					if n:
						url = '{}&{}={}'.format(url, element.name, element.value)
					else:
						url = '{}?{}={}'.format(url, element.name, element.value)

			# Выбираем формат XML
			if 'type=xml' in url:

				# Загружаем прайс-лист
				data = self.load_data(url)
				data = self.unpack(data)

				self.parse(data)

		# Чистим партии
		Party.objects.clear(stock = self.stock_samara,   time = self.start_time)
		Party.objects.clear(stock = self.stock_moscow,   time = self.start_time)
		Party.objects.clear(stock = self.stock_chehov,   time = self.start_time)
		Party.objects.clear(stock = self.stock_bykovo,   time = self.start_time)
		Party.objects.clear(stock = self.stock_dostavka, time = self.start_time)
		Party.objects.clear(stock = self.transit_b,      time = self.start_time)
		Party.objects.clear(stock = self.transit_d,      time = self.start_time)

		self.log()


	def parse(self, data):

		import lxml.etree

		try:
			tree = lxml.etree.parse(data)

		except Exception:
			return None

		# Словарь для составления имени синонима категории
		g = {0: '', 1: '', 2: ''}

		# Распознаваемые слова
		word = {
			'party_article'       : 'No',
			'product_name'        : 'Name',
			'vendor_synonym_name' : 'Brand',
			'product_article'     : 'PartNo',
			'price_usd'           : 'Price',
			'price_rub'           : 'PriceR',
			'stock_chehov'        : 'Avail_SV_CHEHOV',
			'stock_bykovo'        : 'Avail_SV_BYKOVO',
			'stock_dostavka'      : 'Avail_DOSTAVKA',
			'stock_samara'        : 'Avail_RSMR',
			'stock_moscow'        : 'Avail_MSK',
			'transit_b'           : 'Avail_Expect',
			'transit_d'           : 'Avail_ExpectNext',
			'transit_date'        : 'Date_ExpectNext',
			'pack_minimal'        : 'Min_Pack',
			'pack'                : 'Pack',
			'volume'              : 'Vol',
			'weight'              : 'WT',
			'warranty'            : 'Warranty',
			'status'              : 'Status',
			'maction'             : 'MAction',
			'rrp'                 : 'RRP',
			'rrp_date'            : 'RRP_Date'}

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
									category_synonym = self.take_categorysynonym(category_synonym_name)
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
										if attr.tag == word['party_article']:
											party_article = attr.text
										elif attr.tag == word['product_name']:
											product_name = attr.text
										elif attr.tag == word['vendor_synonym_name']:
											vendor_synonym_name = attr.text
										elif attr.tag == word['product_article']:
											product_article = attr.text
										elif attr.tag == word['price_usd']:
											price_usd = self.fix_price(attr.text)
										elif attr.tag == word['price_rub']:
											price_rub = self.fix_price(attr.text)
										elif attr.tag == word['stock_chehov']:
											stock_chehov = self.fix_quantity(attr.text)
										elif attr.tag == word['stock_bykovo']:
											stock_bykovo = self.fix_quantity(attr.text)
										elif attr.tag == word['stock_dostavka']:
											stock_dostavka = self.fix_quantity(attr.text)
										elif attr.tag == word['stock_samara']:
											stock_samara = self.fix_quantity(attr.text)
										elif attr.tag == word['stock_moscow']:
											stock_moscow = self.fix_quantity(attr.text)
										elif attr.tag == word['transit_b']:
											transit_b = self.fix_quantity(attr.text)
										elif attr.tag == word['transit_d']:
											transit_d = self.fix_quantity(attr.text)
										elif attr.tag == word['transit_date']:
											transit_date = attr.text
										elif attr.tag == word['pack_minimal']:
											pack_minimal = attr.text
										elif attr.tag == word['pack']:
											pack = attr.text
										elif attr.tag == word['volume']:
											volume = attr.text
										elif attr.tag == word['weight']:
											weight = attr.text
										elif attr.tag == word['warranty']:
											warranty = attr.text
										elif attr.tag == word['status']:
											status = attr.text
										elif attr.tag == word['maction']:
											maction = attr.text
										elif attr.tag == word['rrp']:
											rrp = attr.text
										elif attr.tag == word['rrp_date']:
											rrp_date = attr.text

									# Обрабатываем синоним производителя
									if vendor_synonym_name:
										vendor_synonym = self.take_vendorsynonym(vendor_synonym_name)
									else:
										continue

									# Получаем объект товара
									if product_article and product_name and vendor_synonym.vendor:
										product = Product.objects.take(
											article  = product_article,
											vendor   = vendor_synonym.vendor,
											name     = product_name,
											category = category_synonym.category,
											unit     = self.default_unit)
										self.count['product'] += 1
									else:
										continue

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
											unit       = self.default_unit,
											time       = self.start_time)
										self.count['party'] += 1

									if stock_bykovo:
										party = Party.objects.make(
											product    = product,
											stock      = self.stock_bykovo,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = stock_bykovo,
											unit       = self.default_unit,
											time       = self.start_time)
										self.count['party'] += 1

									if stock_samara:
										party = Party.objects.make(
											product    = product,
											stock      = self.stock_samara,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = stock_samara,
											unit       = self.default_unit,
											time       = self.start_time)
										self.count['party'] += 1

									if stock_moscow:
										party = Party.objects.make(
											product = product,
											stock      = self.stock_moscow,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = stock_moscow,
											unit       = self.default_unit,
											time       = self.start_time)
										self.count['party'] += 1

									if transit_b:
										party = Party.objects.make(
											product    = product,
											stock      = self.transit_b,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = transit_b,
											unit       = self.default_unit,
											time       = self.start_time)
										self.count['party'] += 1

									if transit_d:
										party = Party.objects.make(
											product    = product,
											stock      = self.transit_d,
											price      = price,
											price_type = self.dp,
											currency   = currency,
											quantity   = transit_d,
											unit       = self.default_unit,
											time       = self.start_time)
										self.count['party'] += 1

		return True
