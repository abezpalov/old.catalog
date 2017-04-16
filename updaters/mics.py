import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

	name  = 'Mics'
	alias = 'mics'
	url = {
		'start' : 'http://www.mics.ru/ru/content/main/',
		'login' : 'https://www.mics.ru/ru/ajax/authorize/',
		'price' : 'https://www.mics.ru/ru/ajax/price/?action=getXMLprice'}


	def __init__(self):

		super().__init__()

		self.stock = self.take_stock('stock', 'склад', 3, 10)
		self.transit = self.take_stock('transit', 'транзит', 10, 40)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		payload = {
			'login'    : self.updater.login,
			'password' : self.updater.password,
			'action'   : 'authorize'}
		self.login(payload)

		tree = self.load_xml(self.url['price'])

		self.parse(tree)

		Party.objects.clear(stock = self.stock, time = self.start_time)

		self.log()


	def parse(self, tree):

		currencies = {
			'RUB' : self.rub,
			'USD' : self.usd,
			'EUR' : self.eur,
			''    : None}

		categories = {}
		for o in tree.xpath('..//Group'):

			category_id = o.attrib.get('GroupID')
			parent_id = o.attrib.get('ParentID')

			category_name = o.attrib.get('Name').strip()

			try:
				parent_name = categories[parent_id]
			except Exception:
				parent_name = None

			if parent_name:
				category_name = '{} | {}'.format(parent_name, category_name)

			category_synonym = self.take_categorysynonym(category_name)
			categories[category_id] = category_synonym.category

		vendors = {}
		for o in tree.xpath('..//Vendor'):

			vendor_id = o.attrib.get('VendorID')

			vendor_name = o.attrib.get('Name')

			vendors[vendor_id] = vendor_name

			for key in vendors:

				vendor_synonym = self.take_vendorsynonym(vendors[key])
				vendors[key] = vendor_synonym.vendor

		for o in tree.xpath('..//Ware'):

			party_article   = o.attrib.get('WareID')
			product_article = o.attrib.get('Partnumber')
			product_name    = o.attrib.get('Name')
			vendor          = vendors[o.attrib.get('VendorID')]
			category        = categories[o.attrib.get('GroupID')]
			stock           = self.fix_quantity(o.attrib.get('Stock_TK11'))
			transit         = self.fix_transit(o.attrib.get('Transit_TK11'))
			price           = self.fix_price(o.attrib.get('Price_TK11'))
			currency        = currencies[o.attrib.get('Currency')]

			try:
				product_description = o.attrib.get('Description')
			except Exception:
				product_description = ''

			if product_article and product_name and vendor:

				product = Product.objects.take(
					article  = product_article,
					vendor   = vendor,
					name     = product_name,
					category = category,
					unit     = self.default_unit)
				self.count['product'] += 1

				if not product.description and product_description:
					product.description = product_description
					product.save()

				if stock:

					party = Party.objects.make(
						product      = product,
						stock        = self.stock,
						article      = party_article,
						price        = price,
						price_type   = self.dp,
						currency     = currency,
						quantity     = stock,
						unit         = self.default_unit,
						product_name = product_name,
						time         = self.start_time)
					self.count['party'] += 1

				if transit is None:

					party = Party.objects.make(
						product      = product,
						stock        = self.transit,
						article      = party_article,
						price        = price,
						price_type   = self.dp,
						currency     = currency,
						quantity     = transit,
						unit         = self.default_unit,
						product_name = product_name,
						time         = self.start_time)
					self.count['party'] += 1

		return True


	def fix_transit(self, value):

		if value == 'Транзит':
			return None
		else:
			return 0
