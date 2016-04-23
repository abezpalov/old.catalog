from project.models import Log

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):


	name  = 'Treolan'
	alias = 'treolan'

	url = {
		'start' : 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F',
		'login' : 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F',
		'price' : 'https://b2b.treolan.ru/Catalog/SearchToExcel?Template=&Commodity=true&IncludeFullPriceList=false&OrderBy=0&Groups=&Vendors=&IncludeSubGroups=false&Condition=0&PriceMin=&PriceMax=&Currency=0&AvailableAtStockOnly=false&AdditionalParamsStr=&AdditionalParams=&AddParamsShow=&GetExcel=false&FromLeftCol=false&CatalogProductsOnly=true&RusDescription=false&skip=0&take=50&LoadResults=false&DemoOnly=false&ShowHpCarePack=false&MpTypes=-1&showActualGoods=false'}


	def __init__(self):

		super().__init__()

		self.stock   = self.take_stock('stock', 'склад', 3, 10)
		self.transit = self.take_stock('transit', 'транзит', 10, 40)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		# Авторизуемся
		payload = {
			'UserName'   : self.updater.login,
			'Password'   : self.updater.password,
			'RememberMe' : 'false'}
		self.login(payload)

		# Получаем HTML-данные
		tree = self.load_html(self.url['price'])

		# Парсим прайс-лист
		self.parce(tree)

		# Чистим партии
		Party.objects.clear(stock = self.stock,   time = self.start_time)
		Party.objects.clear(stock = self.transit, time = self.start_time)

		Log.objects.add(
			subject     = "catalog.updater.{}".format(self.updater.alias),
			channel     = "info",
			title       = "Updated",
			description = "Products: {}; Parties: {}.".format(
				self.count['product'],
				self.count['party']))

		return True


	def parce(self, tree):

		num = {'header': 0}

		word = {
			'article'      : 'Артикул',
			'name'         : 'Наименование',
			'vendor'       : 'Производитель',
			'stock'        : 'Св.',
			'transit'      : 'Св.+Тр.',
			'transit_date' : 'Б. Тр.',
			'price'        : 'Цена',
			'dop'          : 'Доп.'}

		# Парсим
		try:
			table = tree.xpath("//table")[0]
		except IndexError:
			print("Не получилось загрузить прайс-лист.")
			print("Проверьте параметры доступа.")
			return False

		for trn, tr in enumerate(table):

			# Заголовок таблицы
			if trn == num['header']:
				for tdn, td in enumerate(tr):
					if td[0].text == word['article']:
						num['article'] = tdn
					elif td[0].text == word['name']:
						num['name'] = tdn
					elif td[0].text == word['vendor']:
						num['vendor'] = tdn
					elif td[0].text == word['stock']:
						num['stock'] = tdn
					elif td[0].text == word['transit']:
						num['transit'] = tdn
					elif td[0].text == word['transit_date']:
						num['transit_date'] = tdn
					elif td[0].text == word['price']:
						num['price'] = tdn
					elif td[0].text == word['dop']:
						num['dop'] = tdn

				# Проверяем, все ли столбцы распознались
				if 'article' in num and 'name'in num and num['vendor']\
					and num['stock'] and num['transit'] and num['price']:
					print("Структура данных без изменений.")
				else:
					return False

			# Категория
			elif len(tr) == 1:
				category_synonym = CategorySynonym.objects.take(
					name = tr[0][0].text.strip(),
					updater = self.updater,
					distributor = self.distributor)

			# Товар
			elif len(tr) == 8:

				article = ''
				name = ''
				vendor_synonym = None
				stock = 0
				transit = 0
				transit_date = None
				price = 0
				currency = None
				dop = ''

				for tdn, td in enumerate(tr):

					if tdn == num['article']:
						article = str(td.text).strip()

					elif tdn == num['name']:
						name = str(td.text).strip()

					elif tdn == num['vendor']:
						vendor_synonym = VendorSynonym.objects.take(
							name        = str(td.text).strip(),
							updater     = self.updater,
							distributor = self.distributor)

					elif tdn == num['stock']:
						stock = self.fix_quantity(td.text)

					elif tdn == num['transit']:
						transit = self.fix_quantity(td.text) - stock

					elif tdn == num['transit_date']:
						transit_date = td.text

					elif tdn == num['price']:
						price = td.text.strip()
						if 'руб' in price:
							currency = self.rub
						elif '$' in price:
							currency = self.usd
						price = self.fix_price(price)

					elif tdn == num['dop']:
						dop = td.text

				if article and name and vendor_synonym.vendor:
					product = Product.objects.take(
						article  = article,
						vendor   = vendor_synonym.vendor,
						name     = name,
						category = category_synonym.category,
						unit     = self.default_unit)
					self.count['product'] += 1
				else:
					continue

				if stock or not transit:
					party = Party.objects.make(
						product      = product,
						stock        = self.stock,
						price        = price,
						price_type   = self.dp,
						currency     = currency,
						quantity     = stock,
						unit         = self.default_unit,
						product_name = name,
						time         = self.start_time)
					self.count['party'] += 1

				if transit:
					party = Party.objects.make(
						product      = product,
						stock        = self.transit,
						price        = price,
						price_type   = self.dp,
						currency     = currency,
						quantity     = transit,
						unit         = self.default_unit,
						product_name = name,
						time         = self.start_time)
					self.count['party'] += 1

		return True
