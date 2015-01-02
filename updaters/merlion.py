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
		self.name = 'Merlion'
		self.alias = 'merlion'
		self.message = ''

		# Получаем необходимые объекты
		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.stock_smr = Stock.objects.take(alias=self.alias+'-smr-stock', name=self.name+': самарский склад', delivery_time_min = 3, delivery_time_max = 10, distributor=self.distributor)
		self.stock_msk = Stock.objects.take(alias=self.alias+'-msk-stock', name=self.name+': московский склад', delivery_time_min = 3, delivery_time_max = 10, distributor=self.distributor)
		self.transit =Stock.objects.take(alias=self.alias+'-transit', name=self.name+': транзит', delivery_time_min = 10, delivery_time_max = 60, distributor=self.distributor)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.price_type_dp = PriceType.objects.take(alias='DP', name='Диллерская цена')
		self.rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)
		self.usd = Currency.objects.take(alias='USD', name='$', full_name='US Dollar', rate=60, quantity=1)
		self.eur = Currency.objects.take(alias='EUR', name='EUR', full_name='Euro', rate=80, quantity=1)

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.stock_smr)
		Party.objects.clear(stock=self.stock_msk)
		Party.objects.clear(stock=self.transit)

		# Используемые ссылки
		self.url_login = 'https://b2b.merlion.com/'
		self.url_price_smr = 'https://b2b.merlion.com/?action=Y3F86565&action1=YD56AF97&lol=988a0b0e1746efc896603ff6ed71ca96&type=xml'
		self.url_price_msk = 'https://b2b.merlion.com/?action=Y3F86565&action1=YD56AF97&lol=8833aa7b2fdc8497f30f85592dae6747&type=xml'

	def run(self):

		import requests
		from io import BytesIO
		from zipfile import ZipFile

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		try:
			r = s.get(self.url_login, timeout=100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания загрузки Cookies.'
			return False

		# Авторизуемся
		try:
			payload = {
				'client': self.updater.login.split('|')[0],
				'login': self.updater.login.split('|')[1],
				'password': self.updater.password,
				'Ok': '%C2%EE%E9%F2%E8'}
			r = s.post(self.url_login, cookies=cookies, data=payload, allow_redirects=True, verify=False, timeout=100.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			self.message = 'Превышение интервала ожидания подтверждения авторизации.'
			return False

		# Получаем архив с прайс-листом
		request = s.get(self.url_price_smr, cookies=cookies)
		zip_data = ZipFile(BytesIO(request.content))

		# TODO Извлекаем данные
		for name in zip_data.namelist():

			self.message += name + '\n'
			name = bytes(name, 'CP437').decode('CP866')

			xls_data = zip_data.read(name)
			self.message += xls_data















		return False
