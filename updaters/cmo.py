import requests
import lxml.html
from django.utils import timezone
from catalog.models import *
from project.models import Log

class Runner:


	name  = 'ЦМО'
	alias = 'cmo'
	count = {
		'product' : 0,
		'party'   : 0}


	def __init__(self):

		# Фиксируем время старта
		self.start_time = timezone.now()

		# Дистрибьютор
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
			delivery_time_max = 20,
			distributor       = self.distributor)

		# Производитель
		self.vendor = Vendor.objects.take(alias = self.alias, name = self.name)

		# Единица измерения
		self.default_unit = Unit.objects.take(alias = 'pcs', name = 'шт.')

		# Тип цены
		self.rp = PriceType.objects.take(alias = 'RP', name = 'Розничная цена')

		# Валюта
		self.rub = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  = 1)

		# Переменные
		self.url = 'http://cmo.ru/price/'


	def run(self):

		# Номера строк и столбцов
		num = {'header': 0}

		# Распознаваемые слова
		word = {
			'article':    'Артикул',
			'code':       'Код (ID)',
			'name':       'Наименование продукции'}

		# Создаем сессию
		s = requests.Session()

		# Загружаем данные
		try:
			r = s.get(self.url, timeout = 100.0)
			tree = lxml.html.fromstring(r.text)
		except requests.exceptions.Timeout:
			print("Превышение интервала ожидания загрузки.")
			return False

		# Парсим
		tables = tree.xpath(".//div[@class='price-list']")

		# Проходим по таблицам
		for table in tables:

			groups = table.xpath(".//li[@id]")

			# Прохидим по группам
			for group in groups:

				# Определяем синоним категории
				group_name = group.xpath(".//div[@class='item-text-root']")[0]

				category_synonym = CategorySynonym.objects.take(
					name        = str(group_name.text).strip(),
					updater     = self.updater,
					distributor = self.distributor)

				elements = group.xpath(".//div[@class='item-text']")

				# Проходим по элементам
				for element in elements:

					# Артикулы
					try:
						party_article   = element.xpath(".//div[@class='service-num']")[0].text.strip()
						product_article = element.xpath(".//div[@class='service-code']")[0].text.strip()
					except: continue

					# Наименование
					try:
						product_name = element.xpath(".//div[@class='name-text']/a")[0].text.strip()
						product_link = element.xpath(".//div[@class='name-text']/a")[0].get('href').strip()
					except: continue

					# Цена
					try:
						price = element.xpath(".//div[@class='price']")[0].text.strip()
						price = self.fixPrice(price)
					except: continue

					# Получаем объект товара
					if product_article and product_name:
						product = Product.objects.take(
							article  = product_article,
							vendor   = self.vendor,
							name     = product_name,
							category = category_synonym.category,
							unit     = self.default_unit)
						self.count['product'] += 1
					else: continue

					# Добавляем партии
					party = Party.objects.make(
						product    = product,
						stock      = self.factory,
						article    = party_article,
						price      = price,
						price_type = self.rp,
						currency   = self.rub,
						quantity   = -1,
						unit       = self.default_unit,
						time       = self.start_time)
					self.count['party'] += 1

		# Чистим устаревшие партии
		Party.objects.clear(stock = self.factory, time = self.start_time)

		Log.objects.add(
			subject     = "catalog.updater.{}".format(self.updater.alias),
			channel     = "info",
			title       = "Updated",
			description = "Обработано продуктов: {} шт.\n Обработано партий: {} шт.".format(self.count['product'], self.count['party']))

		return True


	def fixPrice(self, price):
		price = str(price).strip()
		if price in ('Цена не найдена'): price = None
		else:
			price = price.replace('RUB', '')
			price = price.replace(' ', '')
			price = float(price)
		return price
