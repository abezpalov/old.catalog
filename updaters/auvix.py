from project.models import Log

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

	name  = 'Auvix'
	alias = 'auvix'
	url = {
		'start'  : 'http://b2b.auvix.ru/',
		'login'  : 'http://b2b.auvix.ru/?login=yes',
		'price'  : 'http://b2b.auvix.ru/prices/Price_AUVIX_dealer_csv.zip'}


	def __init__(self):

		super().__init__()

		self.stock   = self.take_stock('stock',   'склад', 3, 10)
		self.factory = self.take_stock('factory', 'на заказ', 20, 80)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		payload = {
			'AUTH_FORM'     : 'Y',
			'TYPE'          : 'AUTH',
			'backurl'       : '/',
			'USER_LOGIN'    : self.updater.login,
			'USER_PASSWORD' : self.updater.password,
			'Login'         : '%C2%A0',
			'USER_REMEMBER' : 'Y'}

		if not self.login(payload):
			return False

		print(self.url['price'])

		data = self.load_data(self.url['price'])
		print(type(data))

		data = self.unpack(data)

		print(type(data))

		self.parse(data)

		Party.objects.clear(stock = self.stock,   time = self.start_time)
		Party.objects.clear(stock = self.factory, time = self.start_time)

		Log.objects.add(
			subject     = "catalog.updater.{}".format(self.updater.alias),
			channel     = "info",
			title       = "Updated",
			description = "Products: {}; Parties: {}.".format(
				self.count['product'],
				self.count['party']))

	def parse(self, data):

		num = {}

		data = data.read().decode('cp1251')

		# Распознаваемые слова
		word = {
			'party_article'       : 'Идентификатор',
			'party_price_out'     : 'Розничная цена в валюте товара',
			'party_price'         : 'Дилерская цена в валюте товара',
			'party_quantity'      : 'Наличие на складе 0 - нет/1 - есть)',
			'product_category'    : 'Категория',
			'product_article'     : 'Модель',
			'product_name'        : 'Название',
			'product_vendor'      : 'Производитель',
			'party_currency'      : 'Валюта товара',
			'party_price_out_rub' : 'Дилерская цена в рублях'}

		currency = {
			'USD'   : self.usd,
			'Евро'  : self.eur,
			'Рубль' : self.rub}

		for rn, row in enumerate(data.split('\n')):

			# Распознаём 
			if rn == 0:

				for cn, cel in enumerate(row.split(';')):

					if str(cel).strip() == word['party_article']:
						num['party_article'] = cn
					elif str(cel).strip() == word['party_price_out']:
						num['party_price_out'] = cn
					elif str(cel).strip() == word['party_price']:
						num['party_price'] = cn
					elif str(cel).strip() == word['party_quantity']:
						num['party_quantity'] = cn
					elif str(cel).strip() == word['product_category']:
						num['product_category'] = cn
					elif str(cel).strip() == word['product_article']:
						num['product_article'] = cn
					elif str(cel).strip() == word['product_name']:
						num['product_name'] = cn
					elif str(cel).strip() == word['product_vendor']:
						num['product_vendor'] = cn
					elif str(cel).strip() == word['party_currency']:
						num['party_currency'] = cn
					elif str(cel).strip() == word['party_price_out_rub']:
						num['party_price_out_rub'] = cn

				if len(num) < 10:
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else:
					print("Структура данных без изменений.")

			else:

				row = row.split(';')

				if len(row) < 10:
					continue

				product_article     = self.fix_article(row[num['product_article']])
				product_name        = row[num['product_name']]
				product_vendor      = self.take_vendorsynonym(row[num['product_vendor']]).vendor
				product_category    = self.take_categorysynonym(row[num['product_category']]).category

				party_article       = row[num['party_article']]
				party_price_out     = self.fix_price(row[num['party_price_out']])
				party_price         = self.fix_price(row[num['party_price']])
				party_quantity      = self.fix_quantity(row[num['party_quantity']])
				party_currency      = currency.get(row[num['party_currency']], None)

				party_price_out_rub = self.fix_price(row[num['party_price_out_rub']])

				if product_article and product_name and product_vendor:

					# Получаем объект товара
					product = Product.objects.take(
						article  = product_article,
						vendor   = product_vendor,
						name     = product_name,
						category = product_category,
						unit     = self.default_unit)
					self.count['product'] += 1

					# Добавляем партии
					if party_currency:

						if party_quantity is None:

							party = Party.objects.make(
								product    = product,
								stock      = self.stock,
								price      = party_price,
								price_type = self.dp,
								currency   = party_currency,
								quantity   = None,
								unit       = self.default_unit,
								time       = self.start_time)
							self.count['party'] += 1

						else:

							party = Party.objects.make(
								product    = product,
								stock      = self.factory,
								price      = party_price,
								price_type = self.dp,
								currency   = party_currency,
								quantity   = None,
								unit       = self.default_unit,
								time       = self.start_time)
							self.count['party'] += 1


	def fix_quantity(self, quantity):

		if quantity == '1':
			return None
		else:
			return 0


	def fix_article(self, article):

		if 'Уценка' in article or 'демо' in article or 'ДЕМО' in article or 'б.у.' in article:
			return None

		article = article.replace('SAMS ', '')
		article = article.replace('SH ', '')
		article = article.replace('LG ', '')
		article = article.replace('PNC ', '')
		article = article.replace('PHIL ', '')

		return article
