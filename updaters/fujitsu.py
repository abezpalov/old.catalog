from catalog.models import *


class Runner:


	name = 'Fujitsu'
	alias = 'fujitsu'

	url = {
		'start': 'https://partners.ts.fujitsu.com/com/Pages/Default.aspx',
		'login': 'https://partners.ts.fujitsu.com/CookieAuth.dll?Logon',
		'links': 'https://partners.ts.fujitsu.com/sites/CPP/ru/config-tools/Pages/default.aspx',
		'search': '2016.zip',
		'prefix': 'https://partners.ts.fujitsu.com'}


	def __init__(self):

		# Дистрибьютор
		self.distributor = Distributor.objects.take(
			alias = self.alias,
			name  = self.name)

		# Загрузчик
		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = self.distributor)

		# Производитель
		self.vendor = Vendor.objects.take(
			alias = self.alias,
			name = self.name)

		# Завод
		self.factory = Stock.objects.take(
			alias             = self.alias + '-factory',
			name              = self.name + ': на заказ',
			delivery_time_min = 40,
			delivery_time_max = 60,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.factory)

		# Единица измерения
		self.default_unit = Unit.objects.take(
			alias = 'pcs',
			name  = 'шт.')

		# Тип цены
		self.rdp = PriceType.objects.take(
			alias = 'RDP-Fujitsu',
			name  = 'Рекомендованная диллерская цена Fujitsu')

		# Валюта
		self.usd = Currency.objects.take(
			alias     = 'USD',
			name      = '$',
			full_name = 'US Dollar',
			rate      = 60,
			quantity  = 1)

	def run(self):

		import lxml.html
		import requests

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		try:
			r = s.get(self.url['start'], allow_redirects = True, timeout = 30.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания загрузки Cookies.")
			return False

		# Авторизуемся
		try:
			payload = {
				'curl': '/',
				'flags': '0',
				'forcedownlevel': '0',
				'formdir': '15',
				'username': self.updater.login,
				'password': self.updater.password,
				'SubmitCreds': 'Sign In',
				'trusted': '0'}
			r = s.post(self.url['login'], cookies = cookies, data = payload, allow_redirects = True, verify = False, timeout = 30.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания подтверждения авторизации.")
			return False

		# Заходим на страницу загрузки
		try:
			r = s.get(self.url['links'], cookies = cookies, timeout = 30.0)
		except requests.exceptions.Timeout:
			print("Превышение интервала загрузки ссылок.")
			return False

		# Получаем ссылки со страницы
		tree = lxml.html.fromstring(r.text)
		urls = tree.xpath('//a/@href')
		for url in urls:
			if self.url['search'] in url:

				# Скачиваем архив
				url = self.url['prefix'] + url
				print("Архив найден: {}".format(url))
				r = s.get(url, cookies = cookies)

				# Парсим sys_arc.mdb
				mdb = self.getMDB(r, 'sys_arc.mdb')
				self.parseCategories(mdb)
				self.parseProducts(mdb)

				# Парсим prices.mdb
				mdb = self.getMDB(r, 'prices.mdb')
				self.parsePrices(mdb)

				return True

		print("Архив не найден.")
		return False


	def getMDB(self, r, mdb_name):

		from io import BytesIO
		from zipfile import ZipFile

		zip_data = ZipFile(BytesIO(r.content))

		zip_data.extract(mdb_name, '/tmp')
		print("Получены данные: {}".format(mdb_name))

		return "/tmp/{}".format(mdb_name)


	def parseCategories(self, mdb):

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
					name = "{} | {}".format(row[num['numb']], row[num['name']].strip().replace('"', '')),
					updater = self.updater,
					distributor = self.distributor)
				self.category_synonyms[row[num['numb']]] = category_synonym

				print("{} из {}: {}".format(rown + 1, len(rows), category_synonym.name))

		return True


	def parseProducts(self, mdb):

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
					print("Error: Не опознаны необходимые столбцы.")
					return False

			# Строка с данными
			elif rown + 1 < len(rows):

				# Артикул
				article = row[num['article']].strip().replace('"', '')

				# Имя
				name = row[num['name']].strip().replace('"', '')

				# Статус
				if '50' == row[num['status']].strip().replace('"', ''): self.quantity[article] = -1
				else: self.quantity[article] = None

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

					print("{} из {}: {}".format(rown + 1, len(rows), article))

		return True


	def parsePrices(self, mdb):

		import sys, subprocess, os

		# Номера строк и столбцов
		num = {}

		# Распознаваемые слова
		word = {
			'price_n':       'SPNr',
			'price_a':       'SPName',
			'article':       'SachNr'}

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
						product = product,
						stock = self.factory,
						price = price,
						price_type = self.rdp,
						currency = self.usd,
						quantity = quantity,
						unit = self.default_unit)

					print("{} из {}: {} = {} {} {}".format(rown + 1, len(rows), article, str(price), self.usd.alias, self.rdp.alias))

				except KeyError: continue
				except Product.DoesNotExist: continue

		return True
