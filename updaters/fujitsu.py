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
		self.name = 'Fujitsu'
		self.alias = 'fujitsu'
		self.message = ''

		# Получаем необходимые объекты
		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.factory = Stock.objects.take(alias=self.alias+'-factory', name=self.name+': на заказ', delivery_time_min = 40, delivery_time_max = 60, distributor=self.distributor)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.price_type_dp = PriceType.objects.take(alias='RDP', name='Рекомендованная диллерская цена')
		self.usd = Currency.objects.take(alias='USD', name='$', full_name='US Dollar', rate=60, quantity=1)

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.factory)

		# Используемые ссылки
		self.url_start = 'https://globalpartners.ts.fujitsu.com/com/Pages/Default.aspx'
		self.url_login = 'https://globalpartners.ts.fujitsu.com/CookieAuth.dll?Logon'
		self.url_links = 'https://globalpartners.ts.fujitsu.com/sites/CPP/ru/config-tools/Pages/default.aspx'

	def run(self):

		import lxml.html
		import requests

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		try:
			r = s.get(self.url_start, allow_redirects=True, timeout=100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания загрузки Cookies.'
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
			r = s.post(self.url_login, cookies=cookies, data=payload, allow_redirects=True, verify=False, timeout=100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания подтверждения авторизации.'
			return False

		# Заходим на страницу загрузки
		r = s.get(self.url_links, cookies=cookies, timeout=100.0)

		# TODO
		tree = lxml.html.fromstring(r.text)
		urls = tree.xpath('//a/@href')
		for url in urls:
			self.message += url + '\n'


		return False
