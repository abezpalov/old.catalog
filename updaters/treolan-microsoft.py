import re
import requests
import lxml.html
from io import BytesIO
from zipfile import ZipFile
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


	parent_name  = 'Treolan'
	parent_alias = 'treolan'
	name         = 'Treolan: Microsoft на заказ'
	alias        = 'treolan-microsoft'


	def __init__(self):

		# Поставщик
		self.distributor = Distributor.objects.take(
			alias = self.parent_alias,
			name  = self.parent_name)

		# Загрузчики
		self.parent_updater = Updater.objects.take(
			alias       = self.parent_alias,
			name        = self.parent_name,
			distributor = self.distributor)
		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = self.distributor)

		# Склад
		self.stock = Stock.objects.take(
			alias             = self.alias + '-on-order',
			name              = self.name + ': Mictosoft на заказ',
			delivery_time_min = 3,
			delivery_time_max = 10,
			distributor       = self.distributor)
		Party.objects.clear(stock = self.stock)

		# Единица измерения
		self.default_unit = Unit.objects.take(alias = 'pcs', name = 'шт.')

		# Тип цены
		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')

		# Валюта
		self.rub = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  = 1)

		# Забираем параметры доступа у родительского загрузчика
		if not self.updater.login and self.parent_updater.login:
			self.updater.login = self.parent_updater.login
			self.updater.save()
		if not self.updater.password and self.parent_updater.password:
			self.updater.password = self.parent_updater.password
			self.updater.save()

		# Используемые ссылки
		self.url = {
			'login':  'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F',
			'prices': 'https://b2b.treolan.ru/FullPriceListFiles',
			'prefix': 'https://b2b.treolan.ru'}

		# Регулярное выражение для выбора прайс-листа
		self.r = {
			'zip': re.compile('^\/FullPriceListFiles\/Download\/[0-9]+\/ms___[0-9]+.zip$'),
			'olp': re.compile('^ms___[0-9]+.xlsx$'),
			'box': re.compile('^msbox___[0-9]+.xlsx$'),
			'olv': re.compile('^msolv___[0-9]+.xlsx$'),
			'wwf': re.compile('^wwf___[0-9]+.xlsx$')}

	def run(self):

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		try:
			r = s.get(self.url['login'], timeout = 100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышен интервал ожидания загрузки Cookies.")
			return False

		# Авторизуемся
		try:
			payload = {'UserName': self.updater.login, 'Password': self.updater.password, 'RememberMe': 'false'}
			r = s.post(
				self.url['login'],
				cookies         = cookies,
				data            = payload,
				allow_redirects = True,
				verify          = False,
				timeout         = 100.0)
			cookies = r.cookies
			print('Авторизовался.')
		except requests.exceptions.Timeout:
			print("Превышен интервал ожидания подтверждения авторизации.")
			return False

		# Загружаем страницу полных прайс-листов
		try:
			r = s.get(
				self.url['prices'],
				cookies = cookies,
				verify  = False,
				timeout = 100.0)
			print('Загрузил страницу полных прайс-листов.')
		except requests.exceptions.Timeout:
			print("Превышен интервал ожидания загрузки страницы.")
			return False

		# Проходим по всем ссылкам
		tree = lxml.html.fromstring(r.text)
		urls = tree.xpath('//a/@href')
		del(tree)
		for url in urls:

			# Сслыка на нужный прайс
			if re.match(self.r['zip'], url):

				# Ссылка найдена
				url = self.url['prefix'] + url
				price_found = True
				print('Найден прайс-лист: ' + url)

				try:
					r = s.get(
						url,
						cookies = cookies,
						verify  = False,
						timeout = 100.0)
					print('Прайс-лист загружен. Проверяю.')
				except requests.exceptions.Timeout:
					print("Превышен интервал ожидания загрузки прайс-листа.")
					return False

				# Извлекаем данные для обработки
				zip_data = ZipFile(BytesIO(r.content))
				for file_name in zip_data.namelist():

					# Извлекаем файл
					data = zip_data.open(file_name)

					# Выбираем парсер и передаем ему данные
					if re.match(self.r['olp'], file_name):
						self.parseOLP(data)
					elif re.match(self.r['box'], file_name):
						self.parseOLP(data)
					elif re.match(self.r['olv'], file_name):
						self.parseOLP(data)
					elif re.match(self.r['wwf'], file_name):
						self.parseOLP(data)						

		return False


	def parseOLP(self, data):

		# TODO Получаем таблицу данных


		return True


	def parseBox(self, data):


		return True


	def parseOLV(self, data):


		return True


	def parseWWF(self, data):


		return True

