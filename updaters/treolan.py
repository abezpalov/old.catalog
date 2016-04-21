import lxml.html
import requests
from django.utils import timezone
from catalog.models import *
from project.models import Log


class Runner:


	def __init__(self):

		self.name  = 'Treolan'
		self.alias = 'treolan'
		self.count = {
			'product' : 0,
			'party'   : 0}
		self.url_login = 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F'
		self.url_price = 'https://b2b.treolan.ru/Catalog/SearchToExcel?Template=&Commodity=true&IncludeFullPriceList=false&OrderBy=0&Groups=&Vendors=&IncludeSubGroups=false&Condition=0&PriceMin=&PriceMax=&Currency=0&AvailableAtStockOnly=false&AdditionalParamsStr=&AdditionalParams=&AddParamsShow=&GetExcel=false&FromLeftCol=false&CatalogProductsOnly=true&RusDescription=false&skip=0&take=50&LoadResults=false&DemoOnly=false&ShowHpCarePack=false&MpTypes=-1&showActualGoods=false'

		self.num = {'header': 0}

		self.word = {
			'article'      : 'Артикул',
			'name'         : 'Наименование',
			'vendor'       : 'Производитель',
			'stock'        : 'Св.',
			'transit'      : 'Св.+Тр.',
			'transit_date' : 'Б. Тр.',
			'price'        : 'Цена',
			'dop'          : 'Доп.'}

#		currency = {
#			'General'           : None,
#			'#,##0.00[$р.-419]' : self.rub,
#			'[$$-409]#,##0.00'  : self.usd,
#			'[$€-2]\\ #,##0.00' : self.eur}

		self.distributor = Distributor.objects.take(
			alias = self.alias,
			name  = self.name)

		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = self.distributor)

		self.stock = Stock.objects.take(
			alias             = self.alias + '-stock',
			name              = self.name + ': склад',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)

		self.transit = Stock.objects.take(
			alias             = self.alias + '-transit',
			name              = self.name + ': транзит',
			delivery_time_min = 10,
			delivery_time_max = 40,
			distributor       = self.distributor)

		self.default_unit = Unit.objects.take(alias = 'pcs', name = 'шт.')

		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')

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


	def run(self):

		# Фиксируем время старта
		self.start_time = timezone.now()

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
				'UserName'   : self.updater.login,
				'Password'   : self.updater.password,
				'RememberMe' : 'false'}
			r = s.post(self.url_login, cookies=cookies, data=payload, allow_redirects=True, verify=False, timeout=100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания подтверждения авторизации.")
			return False

		# Загружаем общий прайс
		try:
			r = s.get(self.url_price, cookies=cookies, allow_redirects=False, verify=False, timeout=100.0)
			tree = lxml.html.fromstring(r.text)
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания загрузки прайс-листа.")
			return False

		# Парсим
		try:
			table = tree.xpath("//table")[0]
		except IndexError:
			print("Не получилось загрузить прайс-лист.")
			print("Проверьте параметры доступа.")
			return False

		for trn, tr in enumerate(table):

			# Заголовок таблицы
			if trn == self.num['header']:
				for tdn, td in enumerate(tr):
					if td[0].text == self.word['article']:
						self.num['article'] = tdn
					elif td[0].text == self.word['name']:
						self.num['name'] = tdn
					elif td[0].text == self.word['vendor']:
						self.num['vendor'] = tdn
					elif td[0].text == self.word['stock']:
						self.num['stock'] = tdn
					elif td[0].text == self.word['transit']:
						self.num['transit'] = tdn
					elif td[0].text == self.word['transit_date']:
						self.num['transit_date'] = tdn
					elif td[0].text == self.word['price']:
						self.num['price'] = tdn
					elif td[0].text == self.word['dop']:
						self.num['dop'] = tdn

				# Проверяем, все ли столбцы распознались
				try:
					if self.num['article'] == 0 and self.num['name']\
							and self.num['vendor'] and self.num['stock']\
							and self.num['transit'] and self.num['price']:
						print("Структура данных без изменений.")
				except Exception:
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

					if tdn == self.num['article']:
						article = str(td.text).strip()

					elif tdn == self.num['name']:
						name = str(td.text).strip()

					elif tdn == self.num['vendor']:
						vendor_synonym = VendorSynonym.objects.take(
							name        = str(td.text).strip(),
							updater     = self.updater,
							distributor = self.distributor)

					elif tdn == self.num['stock']:
						stock = self.fix_quantity(td.text)

					elif tdn == self.num['transit']:
						transit = self.fix_quantity(td.text) - stock

					elif tdn == self.num['transit_date']:
						transit_date = td.text

					elif tdn == self.num['price']:
						price = td.text.strip()
						if 'руб' in price:
							currency = self.rub
						elif '$' in price:
							currency = self.usd
						price = self.fix_price(price)

					elif tdn == self.num['dop']:
						dop = td.text

				# Получаем объект товара
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
						product    = product,
						stock      = self.stock,
						price      = price,
						price_type = self.dp,
						currency   = currency,
						quantity   = stock,
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1

				if transit:
					party = Party.objects.make(
						product    = product,
						stock      = self.transit,
						price      = price,
						price_type = self.dp,
						currency   = currency,
						quantity   = transit,
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1

		# Чистим партии
		Party.objects.clear(stock = self.stock,   time = self.start_time)
		Party.objects.clear(stock = self.transit, time = self.start_time)

		Log.objects.add(
			subject     = "catalog.updater.{}".format(self.updater.alias),
			channel     = "info",
			title       = "Updated",
			description = "Обработано продуктов: {} шт.\n Обработано партий: {} шт.".format(self.count['product'], self.count['party']))

		return True


	def fix_price(self, price):

		price = price.strip()

		translation_map = {
			ord('$') : '',
			ord('р') : '',
			ord('у') : '',
			ord('б') : '',
			ord(',') : '.',
			ord(' ') : ''}

		price = price.translate(translation_map)

		if price:
			price = float(price)
		else:
			price = None

		return price


	def fix_quantity(self, quantity):

		quantity = str(quantity).strip()

		try:
			if quantity in ('', '0*'):
				return 0
			elif quantity == 'мало':
				return 5
			elif quantity == 'много':
				return 10
			else:
				return int(quantity)
		except Exception:
			return 0
