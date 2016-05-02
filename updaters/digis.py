from project.models import Log

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):


	name  = 'Digis'
	alias = 'digis'

	url = {
		'start' : 'http://digis.ru/distribution/',
		'login' : 'http://digis.ru/distribution/?login=yes',
		'files' : 'http://digis.ru/personal/profile/price/',
		'base'  : 'http://digis.ru',
		'price' : '/bitrix/redirect.php?event1=news_out&event2=/personal/profile/price/p14u/daily_price_cs_pdl.xlsx'}


	def __init__(self):

		super().__init__()

		self.stock   = self.take_stock('stock',   'склад',     3, 10)
		self.transit = self.take_stock('transit', 'транзит',  10, 40)
		self.factory = self.take_stock('factory', 'на заказ', 20, 60)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		# Авторизуемся
		payload = {
			'AUTH_FORM'     : 'Y',
			'TYPE'          : 'AUTH',
			'backurl'       : '/distribution/',
			'href'          : self.url['start'],
			'USER_LOGIN'    : self.updater.login,
			'USER_PASSWORD' : self.updater.password,
			'USER_REMEMBER' : 'Y',
			'Login'         : 'Войти'}
		self.login(payload)


		# Заходим на страницу загрузки
		tree = self.load_html(self.url['files'])

		# Получаем ссылки со страницы
		urls = tree.xpath('//a/@href')

		parsed = []

		for url in urls:
			if self.url['price'] in url:

				# Дописываем префикс url при необходимости
				if not self.url['base'] in url:
					url = self.url['base'] + url

				if not url in parsed:

					parsed.append(url)

					# Скачиваем и парсим
					data = self.load_data(url)
					self.parse(data)

		# Чистим устаревшие партии
		Party.objects.clear(stock = self.factory, time = self.start_time)
		Party.objects.clear(stock = self.stock,   time = self.start_time)
		Party.objects.clear(stock = self.transit, time = self.start_time)

		# Пишем в лог
		self.log()


	def parse(self, data):

		import xlrd

		# Номера строк и столбцов
		num = {'header': 10}

		# Распознаваемые слова
		word = {
			'category'           : 'Категория',
			'category_sub'       : 'Подкатегория',
			'product_vendor'     : 'Бренд',
			'party_article'      : 'Код',
			'product_article'    : 'Артикул',
			'product_name'       : 'Наименование',
			'quantity_factory'   : 'На складе',
			'quantity_stock'     : 'Доступно к заказу',
			'quantity_transit'   : 'Транзит',
			'party_price_in'     : 'Цена (партн)',
			'party_currency_in'  : None,
			'party_price_out'    : 'Цена (розн)',
			'party_currency_out' : None,
			'product_warranty'   : 'Гарантия'}

		currency = {
			'RUB' : self.rub,
			'RUR' : self.rub,
			'руб' : self.rub,
			'руб.': self.rub,
			'USD' : self.usd,
			'EUR' : self.eur,
			''    : None}

		book = xlrd.open_workbook(file_contents = data.read())
		sheet = book.sheet_by_index(1)

		for row_num in range(sheet.nrows):
			row = sheet.row_values(row_num)

			# Пустые строки
			if row_num < num['header']:
				continue

			# Заголовок таблицы
			elif row_num == num['header']:
				for cel_num, cel in enumerate(row):
					if   str(cel).strip() == word['category']:
						num['category'] = cel_num
					elif str(cel).strip() == word['category_sub']:
						num['category_sub'] = cel_num
					elif str(cel).strip() == word['product_vendor']:
						num['product_vendor'] = cel_num
					elif str(cel).strip() == word['party_article']:
						num['party_article'] = cel_num
					elif str(cel).strip() == word['product_article']:
						num['product_article'] = cel_num
					elif str(cel).strip() == word['product_name']:
						num['product_name'] = cel_num
					elif str(cel).strip() == word['quantity_factory']:
						num['quantity_factory'] = cel_num
					elif str(cel).strip() == word['quantity_stock']:
						num['quantity_stock'] = cel_num
					elif str(cel).strip() == word['quantity_transit']:
						num['quantity_transit'] = cel_num
					elif str(cel).strip() == word['party_price_in']:
						num['party_price'] = cel_num
						num['party_currency'] = cel_num + 1
					elif str(cel).strip() == word['party_price_out']:
						num['party_price_out'] = cel_num
						num['party_currency_out'] = cel_num + 1
					elif str(cel).strip() == word['product_warranty']:
						num['product_warranty'] = cel_num

				# Проверяем, все ли столбцы распознались
				if not len(num) == 15:
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else:
					print("Структура данных без изменений.")

			# Товар
			elif row[num['product_article']] and row[num['product_vendor']]:

				# Синоним категории
				category_synonym = CategorySynonym.objects.take(
					name        = "{} | {}".format(
									row[num['category']],
									row[num['category_sub']]),
					updater     = self.updater,
					distributor = self.distributor)

				# Синоним производителя
				vendor_synonym = VendorSynonym.objects.take(
					name        = row[num['product_vendor']],
					updater     = self.updater,
					distributor = self.distributor)

				# Продукт
				product_article    = row[num['product_article']]
				product_name       = row[num['product_name']]

				# Гарантия
				product_warranty = self.fix_warranty(row[num['product_warranty']])

				if product_article and product_name and vendor_synonym.vendor:

					product = Product.objects.take(
						article  = product_article,
						vendor   = vendor_synonym.vendor,
						name     = product_name,
						category = category_synonym.category,
						unit     = self.default_unit)
					self.count['product'] += 1

					parameter_to_product = product.get_parameter_to_product('warranty')
					if parameter_to_product:
						parameter_to_product.set_value(product_warranty)

					# Партии
					party_article = row[num['party_article']]

					quantity            = {}
					quantity['stock']   = self.fix_quantity_stock(row[num['quantity_stock']])
					quantity['transit'] = self.fix_quantity_transit(row[num['quantity_transit']])
					quantity['factory'] = self.fix_quantity_factory(row[num['quantity_factory']])

					party_price         = self.fix_price(row[num['party_price']])
					party_currency      = currency[row[num['party_currency']]]

					party_price_out     = self.fix_price(row[num['party_price_out']])
					party_currency_out  = currency[row[num['party_currency_out']]]

					# Партии на складе
					if quantity['stock']:
						party = Party.objects.make(
							product        = product,
							stock          = self.stock,
							article        = party_article,
							price          = party_price,
							price_type     = self.dp,
							currency       = party_currency,
							price_out      = party_price,
							price_type_out = self.rp,
							currency_out   = party_currency,
							quantity       = quantity['stock'],
							unit           = self.default_unit,
							time           = self.start_time)
						self.count['party'] += 1

					# Партии в транзите
					if quantity['transit']:
						party = Party.objects.make(
							product        = product,
							stock          = self.transit,
							article        = party_article,
							price          = party_price,
							price_type     = self.dp,
							currency       = party_currency,
							price_out      = party_price,
							price_type_out = self.rp,
							currency_out   = party_currency,
							quantity       = quantity['transit'],
							unit           = self.default_unit,
							time           = self.start_time)
						self.count['party'] += 1

					# Партии на заказ
					if quantity['factory'] is None:
						party = Party.objects.make(
							product        = product,
							stock          = self.factory,
							article        = party_article,
							price          = party_price,
							price_type     = self.dp,
							currency       = party_currency,
							price_out      = party_price,
							price_type_out = self.rp,
							currency_out   = party_currency,
							quantity       = quantity['factory'],
							unit           = self.default_unit,
							time           = self.start_time)
						self.count['party'] += 1


	def fix_quantity_factory(self, quantity):

		quantity = str(quantity).strip()

		if quantity in ('под заказ'):
			return None
		else:
			return 0


	def fix_quantity_stock(self, quantity):

		quantity = str(quantity).strip()

		quantity = quantity.replace('более ', '')

		return int(float(quantity))


	def fix_quantity_transit(self, quantity):

		quantity = str(quantity).strip()

		if quantity:
			return 5
		else:
			return None


	def fix_warranty(self, text):

		x = 1
		r = 1

		if 'год' in text or 'лет' in text:
			x = 12
		elif 'дней':
			r = 30

		try:
			return int(text.strip().split(' ')[0]) * x // r
		except Exception:
			return None
