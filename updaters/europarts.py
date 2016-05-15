import re

from project.models import Log

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

	name  = 'EuroParts'
	alias = 'europarts'
	url = {
		'start' : 'http://euro-parts.ru/catalog/index.aspx',
		'base'  : 'http://euro-parts.ru',
		'price' : ''}


	def __init__(self):

		super().__init__()

		self.stock = self.take_stock('stock', 'склад', 3, 10)

		self.count = {
			'product' : 0,
			'party'   : 0}

		self.reg = re.compile('usd: (?P<price>[0-9\.]+)')

		self.done = set()


	def run(self):

		# Загружаем стартовую страницу
		tree = self.load_html(self.url['start'])

		# Список производителей
		vs = tree.xpath('//ul[@class="list ul-brand-list"]/li')
		print('Производителей: {}'.format(len(vs)))

		for v in vs:

			vendor_id = v.get('value')
			vendor_name = v.xpath('.//span[@class="name"]')[0].text
			print('\n{} [{}]'.format(vendor_name, vendor_id))

			vendor = self.take_vendorsynonym(vendor_name).vendor

			# Если вендор не привязан к синониму, переходим к следующему
			if vendor is None:
				print('vendor is None')
				continue

			# Списки категорий
			try:
				div = tree.xpath('//div[@id="categories"]/div[@brandid="{}"]'.format(vendor_id))[0]
			except Exception:
				print('Exception in div = tree.xpath')
				continue

			cs = div.xpath('.//ul[@class="list"]/li')
			print('Категорий: {}'.format(len(cs)))

			for c in cs:

				category_id   = c.get('value')
				category_name = c.xpath('.//a')[0].text
				category_url  = c.xpath('.//a')[0].get('href').replace('//', '/')
				print('\n{} [{}]'.format(category_name, category_id))

#				print('{} [{}|{}]: {}'.format(vendor_name, vendor_id, category_id, category_url))

				category = self.take_categorysynonym(category_name).category
#				print(category)
				url = '{}{}'.format(self.url['base'], category_url)

				tree = self.load_html(url)
				ms = tree.xpath('//div[@class="catalog-list"]/ul/li')
				for m in ms:

					model_id = m.get('modelid')
					model_name = m.xpath('.//a')[0].text
					print('\n{}'.format(model_name))

					url = '{}/actions/get_items.ashx?brandId={}&categoryId={}&modelId={}'.format(
						self.url['base'],
						vendor_id,
						category_id,
						model_id)
					tree = self.load_html(url)

					self.parse(tree, vendor, category)

		# Чистим устаревшие партии
		Party.objects.clear(stock = self.stock, time = self.start_time)

		# Пишем результат в лог
		self.log()


	def parse(self, tree, vendor, category):

		rows = tree.xpath('.//div[@class="rows"]/ul[@class="row"]')

		print('Позиций: {}'.format(len(rows)))

		for row in rows:

			# Получаем объект товара
			product_article = row.xpath('.//li[@class="title"]/a')[0].text
			product_name    = row.xpath('.//li[@class="title"]/small[@class="name"]')[0].text

			if product_article and product_name:
				product = Product.objects.take(
					article  = product_article,
					vendor   = vendor,
					name     = product_name,
					category = category,
					unit     = self.default_unit)
				if product in self.done:
					continue
				else:
					self.count['product'] += 1
					self.done.add(product)
			else:
				continue

			party_quantity = self.fix_quantity(row.xpath('.//li[@class="stock"]')[0].text)
			party_price = self.fix_price(row.get('data'))

			# Добавляем партии
			party = Party.objects.make(
				product    = product,
				stock      = self.stock,
				article    = None,
				price      = party_price,
				price_type = self.dp,
				currency   = self.usd,
				quantity   = None,
				unit       = self.default_unit,
				time       = self.start_time)
			self.count['party'] += 1

			if party_quantity:
				party = Party.objects.make(
					product    = product,
					stock      = self.stock,
					article    = None,
					price      = pary_price,
					price_type = self.dp,
					currency   = self.usd,
					quantity   = party_quantity,
					unit       = self.default_unit,
					time       = self.start_time)
				self.count['party'] += 1

			product_link    = '{}{}'.format(
				self.url['base'], row.xpath('.//li[@class="title"]/a')[0].get('href'))


	def fix_article(self, quantity):

		quantity = str(quantity).strip()

		if 'Уточняйте' in quantity:
			return None
		elif 'Да' in quantity:
			return 1


	def fix_price(self, data):

		# Регулярное выражение
		# Из строки '{price: {rur: 15099, usd: 227.87}}'
		# достать 227.87

		price = re.search(self.reg, data)

		try:
			return float(price.group('price'))
		except Exception:
			return None
