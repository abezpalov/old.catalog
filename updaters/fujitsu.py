from project.models import Log

import catalog.runner
from catalog.models import *






import sys, subprocess, os

class Runner(catalog.runner.Runner):


	name  = 'Fujitsu'
	alias = 'fujitsu'
	count = {
		'product' : 0,
		'party'   : 0}
	url = {
		'start'  : 'https://partners.ts.fujitsu.com/com/Pages/Default.aspx',
		'login'  : 'https://partners.ts.fujitsu.com/CookieAuth.dll?Logon',
		'links'  : 'https://partners.ts.fujitsu.com/sites/CPP/ru/config-tools/Pages/default.aspx',
		'search' : '2016.zip',
		'prefix' : 'https://partners.ts.fujitsu.com'}


	def __init__(self):

		super().__init__()

		self.vendor = Vendor.objects.take(
			alias = self.alias,
			name  = self.name)

		self.stock = self.take_stock('factory', 'на заказ', 40, 60)

		self.rdp = PriceType.objects.take(
			alias = 'RDP-Fujitsu',
			name  = 'Рекомендованная диллерская цена Fujitsu')


	def run(self):

		payload = {
			'curl': '/',
			'flags': '0',
			'forcedownlevel': '0',
			'formdir': '15',
			'username': self.updater.login,
			'password': self.updater.password,
			'SubmitCreds': 'Sign In',
			'trusted': '0'}
		self.login(payload)

		# Заходим на страницу загрузки
		tree = self.load_html(self.url['links'])

		# Получаем ссылки со страницы
		urls = tree.xpath('//a/@href')
		for url in urls:
			if self.url['search'] in url:

				# Скачиваем архив
				url = self.url['prefix'] + url

				data = self.load_data(url)

				# Парсим sys_arc.mdb
				mdb = self.unpack(data, 'sys_arc.mdb')
				self.parse_categories(mdb)
				self.parse_products(mdb)

				# Парсим prices.mdb
				mdb = self.unpack(data, 'prices.mdb')
				self.parse_prices(mdb)

				Party.objects.clear(stock = self.factory, time = self.start_time)

				Log.objects.add(
					subject     = "catalog.updater.{}".format(self.updater.alias),
					channel     = "info",
					title       = "Updated",
					description = "Products: {}; Parties: {}.".format(
						self.count['product'],
						self.count['party']))

				return True

		Log.objects.add(
			subject     = "catalog.updater.{}".format(self.updater.alias),
			channel     = "error",
			title       = "return False",
			description = "Не найден прайс-лист.")

		return False


	def unpack(self, data, mdb_name):

		from zipfile import ZipFile

		zip_data = ZipFile(data)

		zip_data.extract(mdb_name, '/tmp')
		print("Получены данные: {}".format(mdb_name))

		return "/tmp/{}".format(mdb_name)


	def parse_categories(self, mdb):

		import sys, subprocess, os

		# Синонимы категорий
		self.category_synonyms = {}

		# Номера строк и столбцов
		num = {}

		# Распознаваемые слова
		word = {
			'numb': 'PraesKategLfdNr',
			'name': 'PraesKateg'}

		# Загружаем таблицу категорий
		rows = subprocess.Popen(["mdb-export", "-R", "{%row%}", "-d", "{%col%}", mdb, 'PraesentationsKategorien'], stdout = subprocess.PIPE).communicate()[0]
		rows = rows.decode("utf-8").split("{%row%}")

		for rown, row in enumerate(rows):

			row = row.split("{%col%}")

			# Заголовок
			if not rown:

				for celn, cel in enumerate(row):

					cel = cel.strip().replace('"', '')
					if   cel.strip() == word['numb']: num['numb'] = celn
					elif cel.strip() == word['name']: num['name'] = celn

				if len(num) == 2:
					print("Все столбцы распознаны")
				else:
					print("Error: Не опознаны необходимые столбцы.")
					return False

			# Строка с данными
			elif rown + 1 < len(rows):

				# Получаем объект синонима
				category_synonym = CategorySynonym.objects.take(
					name        = "{} | {}".format(
						row[num['numb']],
						row[num['name']].strip().replace('"', '')),
					updater     = self.updater,
					distributor = self.distributor)
				self.category_synonyms[row[num['numb']]] = category_synonym

				#print("{} из {}: {}".format(rown + 1, len(rows), category_synonym.name))

		return True


	def parse_products(self, mdb):

		import sys, subprocess, os

		# Номера строк и столбцов
		num = {}

		# Распознаваемые слова
		word = {
			'article':       'SachNr',
			'name':          'Benennung',
			'status':        'VertStat',
			'category_numb': 'PraesKategNr',
			'description-1': 'Beschreibung',
			'description-2': 'CfgHint'}

		# Статусы продуктов
		self.quantity = {}

		# Загружаем таблицу продуктов
		rows = subprocess.Popen(["mdb-export", "-R", "{%row%}", "-d", "{%col%}", mdb, 'Komp'], stdout = subprocess.PIPE).communicate()[0]
		rows = rows.decode("utf-8").split("{%row%}")

		for rown, row in enumerate(rows):

			row = row.split("{%col%}")

			# Заголовок
			if not rown:

				for celn, cel in enumerate(row):
					print("{}. {}".format(celn, cel))

					cel = cel.strip().replace('"', '')
					if   cel.strip() == word['article']:       num['article']       = celn
					elif cel.strip() == word['name']:          num['name']          = celn
					elif cel.strip() == word['status']:        num['status']        = celn
					elif cel.strip() == word['category_numb']: num['category_numb'] = celn
					elif cel.strip() == word['description-1']: num['description-1'] = celn
					elif cel.strip() == word['description-2']: num['description-2'] = celn

				if len(num) == 6:
					print("Все столбцы распознаны")
				else:
					Log.objects.add(
						subject     = "catalog.updater.{}".format(self.updater.alias),
						channel     = "error",
						title       = "error",
						description = "Не опознаны необходимые столбцы.")
					return False

			# Строка с данными
			elif rown + 1 < len(rows):

				# Артикул
				article = row[num['article']].strip().replace('"', '')

				# Имя
				name = row[num['name']].strip().replace('"', '')

				# Статус
				if '50' == row[num['status']].strip().replace('"', ''):
					self.quantity[article] = -1
				else:
					self.quantity[article] = None

				# Категория
				try:
					category = self.category_synonyms[row[num['category_numb']].strip().replace('"', '')].category
				except KeyError:
					category = None

				# Описание
				if len(row[num['description-1']].strip().replace('"', '')) > len(row[num['description-2']].strip().replace('"', '')):
					description = row[num['description-1']].strip().replace('"', '')
				elif len(row[num['description-2']].strip().replace('"', '')):
					description = row[num['description-1']].strip().replace('"', '')
				else:
					description = None

				# Добавляем продукт в базу
				if article and name:
					product = Product.objects.take(
						article     = article,
						vendor      = self.vendor,
						name        = name,
						category    = category,
						unit        = self.default_unit,
						description = description)
					self.count['product'] += 1

		return True


	def parse_prices(self, mdb):

		import sys, subprocess, os

		# Номера строк и столбцов
		num = {}

		# Распознаваемые слова
		word = {
			'price_n' : 'SPNr',
			'price_a' : 'SPName',
			'article' : 'SachNr'}

		price_types = {}

		# Загружаем таблицу типов цен
		rows = subprocess.Popen(["mdb-export", "-R", "{%row%}", "-d", "{%col%}", mdb, 'PriceSpec'], stdout = subprocess.PIPE).communicate()[0]
		rows = rows.decode("utf-8").split("{%row%}")

		for rown, row in enumerate(rows):

			row = row.split("{%col%}")

			# Заголовок
			if not rown:

				for celn, cel in enumerate(row):
					print("{}. {}".format(celn, cel))

					cel = cel.strip().replace('"', '')
					if   cel.strip() == word['price_n']: num['price_n'] = celn
					elif cel.strip() == word['price_a']: num['price_a'] = celn

				if len(num) == 2:
					print("Все столбцы распознаны")
				else:
					print("Error: Не опознаны необходимые столбцы.")
					return False

			# Строка с данными
			elif rown + 1 < len(rows):
				price_types[row[num['price_a']].strip().replace('"', '')] = row[num['price_n']].strip().replace('"', '')

		word['price'] = "SP" + price_types["RDP"]

		# Загружаем таблицу цен
		rows = subprocess.Popen(["mdb-export", "-R", "{%row%}", "-d", "{%col%}", mdb, 'Prices'], stdout = subprocess.PIPE).communicate()[0]
		rows = rows.decode("utf-8").split("%row%}")

		for rown, row in enumerate(rows):

			row = row.split("{%col%}")

			# Заголовок
			if not rown:

				for celn, cel in enumerate(row):
					print("{}. {}".format(celn, cel))

					cel = cel.strip().replace('"', '')
					if   cel.strip() == word['article']: num['article'] = celn
					elif cel.strip() == word['price']:   num['price']   = celn

				if len(num) == 4:
					print("Все столбцы распознаны")
				else:
					print("Error: Не опознаны необходимые столбцы.")
					return False

			# Строка с данными
			elif rown + 1 < len(rows):

				article = row[num['article']].strip().replace('"', '')
				price = float(row[num['price']].strip().replace('"', '') or 0)

				try:
					# Получаем объект товара
					product = Product.objects.get(article = article, vendor = self.vendor)

					quantity = self.quantity[article]

					# Добавляем партии
					party = Party.objects.make(
						product    = product,
						stock      = self.factory,
						price      = price,
						price_type = self.rdp,
						currency   = self.usd,
						quantity   = quantity,
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1

				except KeyError: continue
				except Product.DoesNotExist: continue

		return True
