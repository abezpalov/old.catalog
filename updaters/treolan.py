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
		self.name = 'Treolan'
		self.alias = 'treolan'

		# Получаем необходимые объекты
		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.stock = Stock.objects.take(alias=self.alias+'-stock', name=self.name+': склад', delivery_time_min = 3, delivery_time_max = 10, distributor=self.distributor)
		self.transit =Stock.objects.take(alias=self.alias+'-transit', name=self.name+': транзит', delivery_time_min = 10, delivery_time_max = 40, distributor=self.distributor)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.dp = PriceType.objects.take(alias='DP', name='Диллерская цена')
		self.rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)
		self.usd = Currency.objects.take(alias='USD', name='$', full_name='US Dollar', rate=60, quantity=1)

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.stock)
		Party.objects.clear(stock=self.transit)

		# Используемые ссылки
		self.url_login = 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F'
		self.url_price = 'https://b2b.treolan.ru/Catalog/SearchToExcel?&comodity=true&withMarketingProgramsOnly=false&availableAtStockOnly=false&rusDescription=true&condition=0&catalogProductsOnly=true&order=0&getExcel=true&searchBylink=false&take=50&skip=0'

	def run(self):

		import lxml.html
		import requests

		# Номера строк и столбцов
		num = {'header': 0}

		# Распознаваемые слова
		word = {
			'article': 'Артикул',
			'name': 'Наименование',
			'vendor': 'Производитель',
			'stock': 'Св.',
			'transit': 'Св.+Тр.',
			'transit_date': 'Б. Тр.',
			'price_usd': 'Цена*',
			'price_rub': 'Цена руб.**',
			'dop': 'Доп.'}

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
			payload = {'UserName': self.updater.login, 'Password': self.updater.password, 'RememberMe': 'false'}
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
			if trn == num['header']:
				for tdn, td in enumerate(tr):
					if   td[0].text == word['article']:      num['article'] = tdn
					elif td[0].text == word['name']:         num['name'] = tdn
					elif td[0].text == word['vendor']:       num['vendor'] = tdn
					elif td[0].text == word['stock']:        num['stock'] = tdn
					elif td[0].text == word['transit']:      num['transit'] = tdn
					elif td[0].text == word['transit_date']: num['transit_date'] = tdn
					elif td[0].text == word['price_usd']:    num['price_usd'] = tdn
					elif td[0].text == word['price_rub']:    num['price_rub'] = tdn
					elif td[0].text == word['dop']:          num['dop'] = tdn

				# Проверяем, все ли столбцы распознались
				if not num['article'] == 0 or not num['name'] or not num['vendor'] or not num['stock'] or not num['transit'] or not num['price_usd'] or not num['price_rub']:
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else: print("Структура данных без изменений.")

			# Категория
			elif len(tr) == 1:
				category_synonym = CategorySynonym.objects.take(name=tr[0][0].text.strip(), updater=self.updater, distributor=self.distributor)

			# Товар
			elif len(tr) == 9:
				for tdn, td in enumerate(tr):
					if   tdn == num['article']: article = str(td.text).strip()
					elif tdn == num['name']: name = str(td.text).strip()
					elif tdn == num['vendor']: vendor_synonym_name = str(td.text).strip()
					elif tdn == num['stock']: stock = self.fixQuantity(td.text)
					elif tdn == num['transit']: transit = self.fixQuantity(td.text) - stock
					elif tdn == num['transit_date']: transit_date = td.text
					elif tdn == num['price_usd']: price_usd = self.fixPrice(td.text)
					elif tdn == num['price_rub']: price_rub = self.fixPrice(td.text)
					elif tdn == num['dop']: dop = td.text

				# Обрабатываем синоним производителя
				if vendor_synonym_name:
					vendor_synonym = VendorSynonym.objects.take(name=vendor_synonym_name, updater=self.updater, distributor=self.distributor)
				else: continue

				# Получаем объект товара
				if article and name and vendor_synonym.vendor:
					product = Product.objects.take(article=article, vendor=vendor_synonym.vendor, name=name, category = category_synonym.category, unit = self.default_unit)
				else: continue

				# Цена в долларах
				if price_usd:
					if stock or not transit:
						party = Party.objects.make(product=product, stock=self.stock, price = price_usd, price_type = self.dp, currency = self.usd, quantity = stock, unit = self.default_unit)
					if transit:
						party = Party.objects.make(product=product, stock=self.transit, price = price_usd, price_type = self.dp, currency = self.usd, quantity = transit, unit = self.default_unit)
					print(product.vendor.name + ' ' + product.article + ' = ' + str(party.price) + ' ' + party.currency.alias + ' ' + party.price_type.alias)

				# Цена в рублях
				elif price_rub:
					if stock or not transit:
						party = Party.objects.make(product=product, stock=self.stock, price = price_rub, price_type = self.dp, currency = self.rub, quantity = stock, unit = self.default_unit)
					if transit:
						party = Party.objects.make(product=product, stock=self.transit, price = price_rub, price_type = self.dp, currency = self.rub, quantity = transit, unit = self.default_unit)
					print(product.vendor.name + ' ' + product.article + ' = ' + str(party.price) + ' ' + party.currency.alias + ' ' + party.price_type.alias)

				# Цена не определена
				else:
					if stock or not transit:
						party = Party.objects.make(product=product, stock=self.stock, price = None, price_type = self.dp, currency = self.rub, quantity = stock, unit = self.default_unit)
					if transit:
						party = Party.objects.make(product=product, stock=self.transit, price = None, price_type = self.dp, currency = self.rub, quantity = transit, unit = self.default_unit)
					print(product.vendor.name + ' ' + product.article)

		print("Обработка прайс-листа завершена.")
		return True

	def fixPrice(self, price):
		price = str(price).strip()
		price = price.replace(',', '.')
		price = price.replace(' ', '')
		if price: price = float(price)
		else: price = None
		return price

	def fixQuantity(self, quantity):
		quantity = str(quantity).strip()
		if quantity in ('', '0*'): quantity = 0
		elif quantity == 'мало': quantity = 5
		elif quantity == 'много': quantity = 10
		elif quantity == 'Поставка\n 7 дней': quantity = 0
		else: quantity = int(quantity)
		return quantity
