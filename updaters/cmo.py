from project.models import Log

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):


	name  = 'ЦМО'
	alias = 'cmo'

	url = {
		'start' : 'http://cmo.ru/',
		'price' : 'http://cmo.ru/price/'}


	def __init__(self):

		super().__init__()

		self.stock   = self.take_stock('factory', 'завод', 10, 20)

		self.vendor = Vendor.objects.take(alias = self.alias, name = self.name)

		self.count = {
			'product' : 0,
			'party'   : 0}


	def run(self):

		# Получаем HTML-данные
		r = self.load_cookie()
		tree = self.load_html(self.url['price'])

		if tree is None:
			return False

		self.parse(tree)

		# Чистим устаревшие партии
		Party.objects.clear(stock = self.stock, time = self.start_time)

		# Пишем в лог
		self.log()


	def parse(self, tree):

		# Номера строк и столбцов
		num = {'header': 0}

		# Распознаваемые слова
		word = {
			'article' : 'Артикул',
			'code'    : 'Код (ID)',
			'name'    : 'Наименование продукции'}

		# Парсим
		tables = tree.xpath(".//div[@class='price-list']")

		# Проходим по таблицам
		for table in tables:

			groups = table.xpath(".//li[@id]")

			# Прохидим по группам
			for group in groups:

				# Определяем синоним категории
				group_name = group.xpath(".//div[@class='item-text-root']")[0]

				category_synonym = self.take_categorysynonym(group_name.text)

				elements = group.xpath(".//div[@class='item-text']")

				# Проходим по элементам
				for element in elements:

					# Артикулы
					try:
						party_article   = element.xpath(".//div[@class='service-num']")[0].text.strip()
						product_article = element.xpath(".//div[@class='service-code']")[0].text.strip()
					except Exception:
						continue

					# Наименование
					try:
						product_name = element.xpath(".//div[@class='name-text']/a")[0].text.strip()
						product_link = element.xpath(".//div[@class='name-text']/a")[0].get('href').strip()
					except Exception:
						continue

					# Цена
					try:
						price = element.xpath(".//div[@class='price']")[0].text.strip()
						price = self.fix_price(price)
					except Exception:
						continue

					# Получаем объект товара
					if product_article and product_name:
						product = Product.objects.take(
							article  = product_article,
							vendor   = self.vendor,
							name     = product_name,
							category = category_synonym.category,
							unit     = self.default_unit)
						self.count['product'] += 1
					else:
						continue

					# Добавляем партии
					party = Party.objects.make(
						product    = product,
						stock      = self.stock,
						article    = party_article,
						price      = price,
						price_type = self.rp,
						currency   = self.rub,
						quantity   = -1,
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1
