from project.models import Log

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

	name = 'Landata'
	alias = 'landata'
	url = {
		'start'  : 'http://www.landata.ru/forpartners/',
		'login'  : 'http://www.landata.ru/forpartners/',
		'price'  : 'http://www.landata.ru/forpartners/sklad/sklad_tranzit_online/',
		'filter' : '?vendor_code='}


	def __init__(self):

		super().__init__()

		self.s1 = self.take_stock('stock-1', 'склад № 1', 3, 10)
		self.s2 = self.take_stock('stock-2', 'склад № 2', 3, 10)
		self.bt = self.take_stock('b-transit', 'ближний транзит', 10, 30)
		self.dt = self.take_stock('d-transit', 'дальний транзит', 20, 60)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		import time

		payload = {
			'AUTH_FORM'     : 'Y',
			'TYPE'          : 'AUTH',
			'backurl'       : '/index.php',
			'USER_LOGIN'    : self.updater.login,
			'USER_PASSWORD' : self.updater.password,
			'Login'         : '%C2%EE%E9%F2%E8'}
		self.login(payload)

		# Заходим на начальную страницу каталога
		tree = self.load_html(self.url['price'])

		# Проходим по всем ссылкам
		urls = tree.xpath('//a/@href')
		done = []
		for url in urls:
			if self.url['filter'] in url:

				# Проверяем ссылку
				url = self.url['price'] + url
				if url in done:
					continue

				# Загружаем и парсим страницу
				tree = self.load_html(url)
				self.parse(tree, url.split(self.url['filter'])[1])
				done.append(url)

				# Ждем, чтобы не получить отбой сервера
				time.sleep(1)

		# Чистим партии
		Party.objects.clear(stock = self.s1, time = self.start_time)
		Party.objects.clear(stock = self.s2, time = self.start_time)
		Party.objects.clear(stock = self.bt, time = self.start_time)
		Party.objects.clear(stock = self.dt, time = self.start_time)

		self.log()


	def parse(self, tree, vendor_synonym_name):

		# Номера строк и столбцов
		num = {'headers': 9}

		# Распознаваемые слова
		word = {
			'party_article'   : 'Н/н',
			'product_article' : 'Код',
			'product_name'    : 'Наименование',
#			's1'              : 'Р',
			's2'              : 'C',
			'bt'              : 'БТ',
			'dt'              : 'ДТ',
			'price'           : 'Цена Dealer',
			'currency_alias'  : 'Валюта'}

		# Валюты
		currencies = {
			'RUB' : self.rub,
			'USD' : self.usd,
			'EUR' : self.eur}

		# Обрабатываем синоним производителя
		if vendor_synonym_name:
			vendor_synonym = VendorSynonym.objects.take(
				name = vendor_synonym_name,
				updater = self.updater,
				distributor = self.distributor)
		else: return False

		# Получаем объект производителя
		vendor = vendor_synonym.vendor
		if not vendor:
			return False

		table = tree.xpath('//table[@class="table  table-striped tablevendor"]//tr')

		# Проходим по строкам таблицы
		for trn, tr in enumerate(table):

			# Заголовок таблицы
			if not trn:
				for thn, th in enumerate(tr):
					if   th.text == word['party_article']:
						num['party_article'] = thn
					elif th.text == word['product_article']:
						num['product_article'] = thn
					elif th.text == word['product_name']:
						num['product_name'] = thn
#					elif th.text == word['s1']:
#						num['s1'] = thn
					elif th.text == word['s2']:
						num['s2'] = thn
					elif th.text == word['bt']:
						num['bt'] = thn
					elif th.text == word['dt']:
						num['dt'] = thn
					elif th.text == word['price']:
						num['price'] = thn
					elif th.text == word['currency_alias']:
						num['currency_alias'] = thn

				# Проверяем, все ли столбцы распознались
				if len(num) < num['headers']:
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else:
					pass

			# Строка товара
			else:

				try:
					# Обрабатываем информацию о товаре
					product_article = tr[num['product_article']].text.strip().split('//')[0]
					product_name    = tr[num['product_name']].text.strip()
					if product_article and product_name:
						product = Product.objects.take(
							article = product_article,
							vendor = vendor,
							name = product_name,
							category = None,
							unit = self.default_unit)
						self.count['product'] += 1
					else: continue

					# Обрабатываем информацию о партиях
					party_article = tr[num['party_article']].text.strip()

					price = self.fix_price(tr[num['price']].text)

					currency_alias = tr[num['currency_alias']].text.strip()
					if currency_alias: currency = currencies[currency_alias]
					else: currency =  None

#					s1 = self.fixQuantity(tr[num['s1']].text)
					s2 = self.fix_quantity(tr[num['s2']].text)
					bt = self.fix_quantity(tr[num['bt']].text)
					dt = self.fix_quantity(tr[num['dt']].text)

					# Записываем партии
#					if s1:
#						party = Party.objects.make(
#							product    = product,
#							stock      = self.s1,
#							price      = price,
#							price_type = self.dp,
#							currency   = currency,
#							quantity   = s1,
#							unit       = self.default_unit)
#						print("{} {} = {} {}".format(product.vendor, product.article, party.price, party.currency))

					if s2:
						party = Party.objects.make(
							product    = product,
							stock      = self.s2,
							price      = price,
							price_type = self.dp,
							currency   = currency,
							quantity   = s2,
							unit       = self.default_unit,
							time       = self.start_time)
						self.count['party'] += 1

					if bt:
						party = Party.objects.make(
							product    = product,
							stock      = self.bt,
							price      = price,
							price_type = self.dp,
							currency   = currency,
							quantity   = bt,
							unit       = self.default_unit,
							time       = self.start_time)
						self.count['party'] += 1

					if dt:
						party = Party.objects.make(
							product    = product,
							stock      = self.dt,
							price      = price,
							price_type = self.dp,
							currency   = currency,
							quantity   = dt,
							unit       = self.default_unit,
							time       = self.start_time)
						self.count['party'] += 1
				except:
					continue

		return True
