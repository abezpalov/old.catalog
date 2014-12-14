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
		self.name = 'Kramer'
		self.alias = 'kramer'
		self.message = ''

		# Получаем необходимые объекты
		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.factory = Stock.objects.take(alias=self.alias+'-factory', name=self.name+': завод', delivery_time_min = 10, delivery_time_max = 40, distributor=self.distributor)
		self.vendor = Vendor.objects.take(alias=self.alias, name=self.name)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.price_type_rrp = PriceType.objects.take(alias='RRP', name='Рекомендованная розничная цена')
		self.rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)
		self.usd = Currency.objects.take(alias='USD', name='$', full_name='Доллар США', rate=60, quantity=1)

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.factory)

		# Фильтры ссылок
		self.devices_url = "http://www.kramer.ru/Useful_files/Kramer-RUS-List-Price-"
		self.cables_url = "http://www.kramer.ru/Useful_files/Kramer-Cable-List-Price-"

	def run(self):

		import lxml.html
		import requests

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		url = 'http://kramer.ru/'
		r = s.get(url)
		cookies = r.cookies

		# Авторизуемся
		url = 'http://kramer.ru/'
		payload = {'dealer_login': self.updater.login, 'dealer_pass': self.updater.password}
		r = s.post(url, cookies=cookies, data=payload, allow_redirects=True)
		cookies = r.cookies

		# Переходим на закрытую часть
		url = 'http://kramer.ru/closed/files/'
		r = s.get(url, cookies=cookies, allow_redirects=True)
		tree = lxml.html.fromstring(r.text)

		# Ещем ссылки
		urls = tree.xpath('//a/@href')
		for url in urls:
			if self.devices_url in url:

				# Получаем прайс-лист из архива
				xls_data = self.getXLS(request = s.get(url, cookies=cookies, allow_redirects=True))

				# Парсим прайс-лист
				self.parseDevices(xls_data)

			elif self.cables_url in url:

				# Получаем прайс-лист из архива
				xls_data = self.getXLS(request = s.get(url, cookies=cookies, allow_redirects=True))

				# Парсим прайс-лист
				self.parseCables(xls_data)

		return True

	def getXLS(self, request):

		from io import BytesIO
		from zipfile import ZipFile

		zip_data = ZipFile(BytesIO(request.content))
		xls_data = zip_data.open(zip_data.namelist()[0])

		self.message += 'Получен прайс-лист: ' + zip_data.namelist()[0] + '\n'

		return xls_data

	def parseDevices(self, xls_data):

		import xlrd

		# Номера строк и столбцов
		num = {'header': 4}

		# Распознаваемые слова
		word = {
			'group': 'ГРУППА',
			'article': 'P/N',
			'model': 'Модель',
			'size': 'Размер',
			'format': 'Формат',
			'name': 'Описание',
			'price': 'Цена, $',
			'dop': 'Примечание',
			'group_name': '',
			'category_name': ''}

		book = xlrd.open_workbook(file_contents=xls_data.read())
		sheet = book.sheet_by_index(0)
		for row_num in range(sheet.nrows):
			row = sheet.row_values(row_num)

			# Пустые строки
			if row_num < num['header']:
				continue

			# Заголовок таблицы
			elif row_num == num['header']:
				for cel_num, cel in enumerate(row):
					if str(cel).strip() == word['article']: num['article'] = cel_num
					elif str(cel).strip() == word['model']: num['model'] = cel_num
					elif str(cel).strip() == word['size']: num['size'] = cel_num
					elif str(cel).strip() == word['format']: num['format'] = cel_num
					elif str(cel).strip() == word['name']: num['name'] = cel_num
					elif str(cel).strip() == word['price']: num['price'] = cel_num
					elif str(cel).strip() == word['dop']: num['dop'] = cel_num

				# Проверяем, все ли столбцы распознались
				if not num['article'] == 0 or not num['model'] or not num['size'] or not num['format'] or not num['name'] or not num['price'] or not num['dop']:
					self.message += "Ошибка структуры данных: не все столбцы опознаны.\n"
					return False
				else: self.message += "Структура данных без изменений.\n"

			# Категория
			elif row[num['name']] and not row[num['article']] and not row[num['price']]:
				if word['group'] in row[num['name']]: word['group_name'] = row[num['name']]
				else: word['category_name'] = row[num['name']]
				categorySynonym = CategorySynonym.objects.take(name=word['group_name'] + ' ' + word['category_name'], updater=self.updater, distributor=self.distributor)

			# Товар
			elif row[num['name']] and row[num['article']] and row[num['price']]:

				# Получаем объект товара
				try:
					product = Product.objects.get(article=row[num['article']], vendor=self.vendor)
					if not product.category and categorySynonym.category:
						product.category = categorySynonym.category
						product.save()
				except Product.DoesNotExist:

					# Формируем имя
					name = self.vendor.name + ' ' + str(row[num['model']]) + ' ' + str(row[num['name']])
					if row[num['size']] or row[num['format']]:
						name += ' ('
						if row[num['size']]: name += 'размер: ' + str(row[num['size']])
						if row[num['size']] and row[num['format']]: name += ', '
						if row[num['format']]: name += 'формат: ' + str(row[num['format']])
						name += ')'

					# Добавляем товар в базу
					product = Product(name=name[:500], full_name=name, article=row[num['article']], vendor=self.vendor, category=categorySynonym.category, unit=self.default_unit, description = '', created=datetime.now(), modified=datetime.now())
					product.save()

				# Добавляем партии
				price = self.fixPrice(row[num['price']])
				party = Party.objects.make(product=product, stock=self.factory, price = price, price_type = self.price_type_rrp, currency = self.usd, quantity = -1, unit = self.default_unit)

		return True


	def parseCables(self, xls_data):

		import xlrd

		# Номера строк и столбцов
		num = {'header': 4}

		# Распознаваемые слова
		word = {
			'article': 'Part Number',
			'model': 'Модель',
			'name': 'Описание',
			'size': 'Метры',
			'price': 'Цена,     $',
			'dop': 'Примечание',
			'category_name': ''}

		book = xlrd.open_workbook(file_contents=xls_data.read())
		sheet = book.sheet_by_index(0)
		for row_num in range(sheet.nrows):
			row = sheet.row_values(row_num)

			# Пустые строки
			if row_num < num['header']:
				continue

			# Заголовок таблицы
			elif row_num == num['header']:
				for cel_num, cel in enumerate(row):
					if str(cel).strip() == word['article']: num['article'] = cel_num
					elif str(cel).strip() == word['model']: num['model'] = cel_num
					elif str(cel).strip() == word['name']: num['name'] = cel_num
					elif str(cel).strip() == word['size']: num['size'] = cel_num
					elif str(cel).strip() == word['price']: num['price'] = cel_num
					elif str(cel).strip() == word['dop']: num['dop'] = cel_num

				# Проверяем, все ли столбцы распознались
				if not num['article'] or not num['model'] or not num['name'] or not num['size'] or not num['price'] or not num['dop']:
					self.message += "Ошибка структуры данных: не все столбцы опознаны.\n"
					return False
				else: self.message += "Структура данных без изменений.\n"

			# Категория
			elif row[num['name']] and not row[num['article']] and not row[num['price']]:
				word['category_name'] = row[num['name']]
				categorySynonym = CategorySynonym.objects.take(word['category_name'], updater=self.updater, distributor=self.distributor)

			# Товар
			elif row[num['name']] and row[num['article']] and row[num['price']]:

				# Получаем объект товара
				try:
					product = Product.objects.get(article=row[num['article']], vendor=self.vendor)
					if not product.category and categorySynonym.category:
						product.category = categorySynonym.category
						product.save()
				except Product.DoesNotExist:

					# Формируем имя
					name = self.vendor.name + ' ' + str(row[num['model']]) + ' ' + str(row[num['name']])
					if row[num['size']]: name += ' (длина: ' + str(row[num['size']]).replace('.', ',') + ' м.)'

					# Добавляем товар в базу
					product = Product(name=name[:500], full_name=name, article=row[num['article']], vendor=self.vendor, category=categorySynonym.category, unit=self.default_unit, description = '', created=datetime.now(), modified=datetime.now())
					product.save()

				# Добавляем партии
				price = self.fixPrice(row[num['price']])
				party = Party.objects.make(product=product, stock=self.factory, price = price, price_type = self.price_type_rrp, currency = self.usd, quantity = -1, unit = self.default_unit)

		return True

	def fixPrice(self, price):
		if price in ('CALL', '?'): price = -1
		else: price = float(price)
		return price
