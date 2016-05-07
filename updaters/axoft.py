from project.models import Log

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):


	name  = 'Axsoft'
	alias = 'axoft'

	url = {
		'start'   : 'http://axoft.ru/',
		'login'   : 'http://axoft.ru/',
		'vendors' : 'http://axoft.ru/vendors/',
		'prefix'  : 'http://axoft.ru'}

	word = {
		'vendor' : '/vendors/',
		'price'  : '/pricelists/download.php?'}


	def __init__(self):

		super().__init__()

		self.stock = self.take_stock('on-order', 'на заказ', 5, 40)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		# Авторизуемся
		payload = {
			'backurl'       : '/',
			'AUTH_FORM'     : 'Y',
			'TYPE'          : 'AUTH',
			'IS_POPUP'      : '1',
			'USER_LOGIN'    : self.updater.login,
			'USER_PASSWORD' : self.updater.password,
			'Login'         : 'Вход для партнеров'}
		self.login(payload)

		# Получаем список производителей
		prices = self.get_prices_urls()

		# Проходим по каждому прайс-листу
		for n, price in enumerate(prices):

			print("Прайс-лист {} из {}: {}".format(
				n + 1,
				len(prices),
				price[0]))

			# Синоним производителя
			vendor_synonym = self.take_vendorsynonym(price[0])

			if vendor_synonym.vendor:

				# Скачиваем архив с прайс-листом
				data = self.load_data(price[1])

				# Распаковываем и парсим
				data = self.unpack(data)

				if data is not None:
					self.parse(data, vendor_synonym.vendor)

		# Чистим устаревшие партии
		Party.objects.clear(stock = self.stock, time = self.start_time)

		# Пишем в лог
		self.log()


	def get_prices_urls(self):

		prices  = set()

		tree = self.load_html(self.url['vendors'])

		links = tree.xpath('//a')

		# Выбираем ссылкки на страницы производителей
		for n, link in enumerate(links):

			vendor_name = link.text
			vendor_url  = '{}{}'.format(self.url['prefix'], link.get('href'))

			if self.word['vendor'] in vendor_url:

				tree = self.load_html(vendor_url)

				if tree is not None:

					# Добавляем в список ссылок на прайс-листы соответсвующие
					for url in tree.xpath('//a/@href'):

						if self.word['price'] in url:

							if not self.url['prefix'] in url:
								url  = '{}{}'.format(self.url['prefix'], url)

							price = (vendor_name, url,)
							prices.add(price)

							print('Ссылка {} из {}: {} [{}].'.format(
									n + 1,
									len(links),
									price[1],
									price[0]))

		return prices


	def parse(self, data, vendor):

		import xlrd

		# Номера строк и столбцов
		num = {
			'header_line' : 3,
			'first_line'  : 5}

		# Распознаваемые слова
		word = {
			'party_article'   : 'AxoftSKU',
			'product_article' : 'VendorSKU',
			'product_name'    : 'ProductDescription',
			'product_version' : 'Version',
			'price_in'        : 'Partner',
			'price_out'       : 'Retail',
			'product_vat'     : 'NDS'}

		# Сопоставление валют
		currencies = {
			'General'           : None,
			'#,##0.00[$р.-419]' : self.rub,
			'[$$-409]#,##0.00'  : self.usd,
			'[$€-2]\\ #,##0.00' : self.eur}

		# Имя категории поставщика
		category_synonym_name = None

		# Парсим
		try:
			book = xlrd.open_workbook(
				file_contents   = data.read(),
				formatting_info = True)
		except NotImplementedError:
			print("Ошибка: непонятная ошибка при открытии файла.")
			return False
		sheet = book.sheet_by_index(0)

		# Получаем словарь форматов (потребуется при получении валюты)
		formats = book.format_map

		# Проходим по всем строкам
		for row_num in range(sheet.nrows):
			row = sheet.row_values(row_num)

			# Заголовок
			if row_num == num['header_line']:

				# Разбираем заголовок
				for cel_num, cel in enumerate(row):
					if   str(cel).strip() == word['party_article']:
						num['party_article'] = cel_num
					elif str(cel).strip() == word['product_article']:
						num['product_article'] = cel_num
					elif str(cel).strip() == word['product_name']:
						num['product_name'] = cel_num
					elif str(cel).strip() == word['product_version']:
						num['product_version'] = cel_num
					elif str(cel).strip() == word['price_in']:
						num['price_in'] = cel_num
					elif str(cel).strip() == word['price_out']:
						num['price_out'] = cel_num
					elif str(cel).strip() == word['product_vat']:
						num['product_vat'] = cel_num

				# Проверяем, все ли столбцы распознались
				if len(num) < 9:
					print(len(num))
					for n in num:
						print(n)
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else: print("Структура данных без изменений.")

			# Строка с данными
			elif row_num >= num['first_line']:

				# Определяем значение переменных
				if row[num['product_article']]:
					product_article = row[num['product_article']]
				else:
					product_article = row[num['party_article']]
				party_article       = row[num['party_article']]
				product_name        = row[num['product_name']]
				product_version     = row[num['product_version']]
				price_in            = self.fix_price(row[num['price_in']])
				price_out           = self.fix_price(row[num['price_out']])
				product_vat         = row[num['product_vat']]

				# Валюта входной цены
				xfx = sheet.cell_xf_index(row_num, num['price_in'])
				xf = book.xf_list[xfx]
				format_str = formats[xf.format_key].format_str
				price_currency_in = currencies[format_str]

				# Валюта выходной цены
				xfx = sheet.cell_xf_index(row_num, num['price_out'])
				xf = book.xf_list[xfx]
				format_str = formats[xf.format_key].format_str
				price_currency_out = currencies[format_str]

				# Имя синонима категории
				if product_name and not product_article:
					category_synonym_name = "{}: {}".format(
						vendor.name,
						row[num['product_name']])

				# Продукт
				elif product_article and product_name:

					# Получаем объект категории
					if category_synonym_name:
						category_synonym = self.take_categorysynonym(category_synonym_name)
						category = category_synonym.category
					else:
						category = None

					# Получаем объект товара
					product = Product.objects.take(
						article  = product_article,
						vendor   = vendor,
						name     = product_name,
						category = category,
						unit     = self.default_unit)
					self.count['product'] += 1

					# Добавляем партии
					party = Party.objects.make(
						product        = product,
						stock          = self.stock,
						price          = price_in,
						price_type     = self.dp,
						currency       = price_currency_in,
						price_out      = price_out,
						price_type_out = self.rp,
						currency_out   = price_currency_out,
						quantity       = -1,
						unit           = self.default_unit,
						time           = self.start_time)
					self.count['party'] += 1

		return True
