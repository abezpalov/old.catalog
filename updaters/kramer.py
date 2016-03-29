import lxml.html
import requests
from django.utils import timezone
from catalog.models import *
from project.models import Log

class Runner:


	name  = 'Kramer'
	alias = 'kramer'
	count = {
		'product' : 0,
		'party'   : 0}
	url = {
		'start' : 'http://kramer.ru/',
		'login' : 'http://kramer.ru/?login=yes',
		'files' : 'http://kramer.ru/partners/prices/',
		'base'  : 'http://kramer.ru',
		'price' : 'http://kramer.ru/filedownload.php?id='}


	def __init__(self):

		# Фиксируем время старта
		self.start_time = timezone.now()

		# Поставщик
		self.distributor = Distributor.objects.take(
			alias = self.alias,
			name  = self.name)

		# Загрузчик
		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = self.distributor)

		# Завод
		self.factory = Stock.objects.take(
			alias             = self.alias + '-factory',
			name              = self.name + ': завод',
			delivery_time_min = 10,
			delivery_time_max = 40,
			distributor       = self.distributor)

		# Производитель
		self.vendor = Vendor.objects.take(
			alias = self.alias,
			name  = self.name)

		# Единица измерения
		self.default_unit = Unit.objects.take(
			alias = 'pcs',
			name  = 'шт.')

		# Тип цены
		self.rrp = PriceType.objects.take(
			alias = 'RRP',
			name  = 'Рекомендованная розничная цена')

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
			full_name = 'Доллар США',
			rate      = 60,
			quantity  = 1)


	def run(self):

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		r = s.get(self.url['start'])
		cookies = r.cookies

		# Авторизуемся
		payload = {
			'backurl': '/',
			'AUTH_FORM': 'Y',
			'TYPE': 'AUTH',
			'USER_LOGIN': self.updater.login,
			'USER_PASSWORD': self.updater.password,
			'Login': 'Войти'}
		r = s.post(self.url['login'], cookies = cookies, data = payload, allow_redirects = True)
		cookies = r.cookies

		# Переходим на закрытую часть
		r = s.get(self.url['files'], cookies = cookies, allow_redirects = True)
		tree = lxml.html.fromstring(r.text)

		# Ищем ссылки
		urls = tree.xpath('//a/@href')
		ok = 0
		for url in urls:
			url = self.url['base'] + url
			if self.url['price'] in url:
				if self.parsePrice(request = s.get(url, cookies = cookies, allow_redirects = True)):
					ok += 1

		if ok < 2:
			Log.objects.add(
				subject     = "catalog.updater.{}".format(self.updater.alias),
				channel     = "error",
				title       = "return False",
				description = "Не получилось загрузить прайс-листы.")
			return False

		# Чистим партии
		Party.objects.clear(stock=self.factory, time = self.start_time)

		Log.objects.add(
			subject     = "catalog.updater.{}".format(self.updater.alias),
			channel     = "info",
			title       = "Updated",
			description = "Обработано продуктов: {} шт.\n Обработано партий: {} шт.".format(self.count['product'], self.count['party']))

		return True


	def parsePrice(self, request):

		from io import BytesIO
		from zipfile import ZipFile

		# Распознаваемые слова
		words = {
			'cable': 'Cable',
			'device': 'device'}

		filename = request.headers.get('content-disposition')
		print(filename)

		xls_data = BytesIO(request.content)

		if words['cable'] in filename:
			print("Получен прайс-лист кабелей и материалов.")
			self.parseCables(xls_data)
			return True
		elif words['device'] in filename:
			print("Получен прайс-лист оборудования.")
			self.parseDevices(xls_data)
			return True


	def parseDevices(self, xls_data):

		import xlrd

		# Номера строк и столбцов
		num = {'header': 4}

		# Распознаваемые слова
		word = {
			'group'         : 'ГРУППА',
			'article'       : 'P/N',
			'model'         : 'Модель',
			'size'          : 'Размер',
			'name'          : 'Описание',
			'price'         : 'Цена, $',
			'dop'           : 'Примечание',
			'group_name'    : '',
			'category_name' : ''}

		book = xlrd.open_workbook(file_contents = xls_data.read())
		sheet = book.sheet_by_index(0)
		for row_num in range(sheet.nrows):
			row = sheet.row_values(row_num)

			# Пустые строки
			if row_num < num['header']:
				continue

			# Заголовок таблицы
			elif row_num == num['header']:
				for cel_num, cel in enumerate(row):
					if   str(cel).strip() == word['article']:  num['article'] = cel_num
					elif str(cel).strip() == word['model']:    num['model']   = cel_num
					elif str(cel).strip() == word['size']:     num['size']    = cel_num
					elif str(cel).strip() == word['name']:     num['name']    = cel_num
					elif str(cel).strip() == word['price']:    num['price']   = cel_num
					elif str(cel).strip() == word['dop']:      num['dop']     = cel_num

				# Проверяем, все ли столбцы распознались
				if not num['article'] == 0 or not num['model'] or not num['size'] or not num['name'] or not num['price'] or not num['dop']:
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else: print("Структура данных без изменений.")

			# Категория
			elif row[num['name']] and not row[num['article']] and not row[num['price']]:
				if word['group'] in row[num['name']]: word['group_name'] = row[num['name']]
				else: word['category_name'] = row[num['name']]
				category_synonym = CategorySynonym.objects.take(
					name = "Devices: {} {}".format(word['group_name'], word['category_name']),
					updater = self.updater,
					distributor = self.distributor)

			# Товар
			elif row[num['name']] and row[num['article']] and row[num['price']]:

				# Определяем имя
				name = "{} {} {}".format(self.vendor.name, row[num['model']], row[num['name']])
				if row[num['size']]: name += " ( размер: {})".format(str(row[num['size']]))

				# Определяем артикул
				article = row[num['article']]

				# Получаем объект товара
				product = Product.objects.take(
					article  = article,
					vendor   = self.vendor,
					name     = name,
					category = category_synonym.category,
					unit     = self.default_unit)
				self.count['product'] += 1

				# Указываем категорию
				if not product.category and category_synonym.category:
					product.category = category_synonym.category
					product.save()

				# Добавляем партии
				price = self.fixPrice(row[num['price']])
				party = Party.objects.make(
					product    = product,
					stock      = self.factory,
					price      = price,
					price_type = self.rrp,
					currency   = self.usd,
					quantity   = -1,
					unit       = self.default_unit,
					time       = self.start_time)
				self.count['party'] += 1

		return True


	def parseCables(self, xls_data):

		import xlrd

		# Номера строк и столбцов
		num = {'header': 4}

		# Распознаваемые слова
		word = {
			'article'       : 'Part Number',
			'model'         : 'Модель',
			'name'          : 'Описание',
			'size'          : 'Метры',
			'price'         : 'Цена,     $',
			'dop'           : 'Примечание',
			'category_name' : ''}

		book = xlrd.open_workbook(file_contents = xls_data.read())
		sheet = book.sheet_by_index(0)
		for row_num in range(sheet.nrows):
			row = sheet.row_values(row_num)

			# Пустые строки
			if row_num < num['header']:
				continue

			# Заголовок таблицы
			elif row_num == num['header']:
				for cel_num, cel in enumerate(row):
					if   str(cel).strip() == word['article']: num['article'] = cel_num
					elif str(cel).strip() == word['model']: num['model'] = cel_num
					elif str(cel).strip() == word['name']:  num['name'] = cel_num
					elif str(cel).strip() == word['size']:  num['size'] = cel_num
					elif str(cel).strip() == word['price']: num['price'] = cel_num
					elif str(cel).strip() == word['dop']:   num['dop'] = cel_num

				# Проверяем, все ли столбцы распознались
				if not num['article'] or not num['model'] or not num['name'] or not num['size'] or not num['price'] or not num['dop']:
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else: print("Структура данных без изменений.")

			# Категория
			elif row[num['name']] and not row[num['article']] and not row[num['price']]:
				word['category_name'] = row[num['name']]
				category_synonym = CategorySynonym.objects.take(
					name = "Cables: {}".format(word['category_name']),
					updater = self.updater,
					distributor = self.distributor)

			# Товар
			elif row[num['name']] and row[num['article']] and row[num['price']]:

				# Определяем имя
				name = '{} {} {}'.format(self.vendor.name, row[num['model']], row[num['name']])
				if row[num['size']]: name += ' (длина: {} м.)'.format(str(row[num['size']]).replace('.', ','))

				# Определяем артикул
				article = row[num['article']]

				# Получаем объект товара
				product = Product.objects.take(
					article  = article,
					vendor   = self.vendor,
					name     = name,
					category = category_synonym.category,
					unit     = self.default_unit)
				self.count['product'] += 1

				# Добавляем партии
				party = Party.objects.make(
					product    = product,
					stock      = self.factory,
					price      = self.fixPrice(row[num['price']]),
					price_type = self.rrp,
					currency   = self.usd,
					quantity   = -1,
					unit       = self.default_unit,
					time       = self.start_time)
				self.count['party'] += 1

		return True


	def fixPrice(self, price):
		if price in ('CALL', '?'): price = None
		else: price = float(price)
		return price
