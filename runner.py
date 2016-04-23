import requests

from django.utils import timezone

from catalog.models import *


class Runner:


	def __init__(self):

		self.start_time = timezone.now()

		self.distributor = Distributor.objects.take(
			alias = self.alias,
			name  = self.name)

		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = self.distributor)

		self.default_unit = Unit.objects.take(alias = 'pcs', name = 'шт.')

		self.dp = PriceType.objects.take(alias = 'DP', name = 'Диллерская цена')
		self.rp = PriceType.objects.take(alias = 'RP', name = 'Розничная цена')

		self.rub = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  = 1)

		self.usd = Currency.objects.take(
			alias     = 'USD',
			name      = '$',
			full_name = 'US Dollar',
			rate      = 60,
			quantity  = 1)

		self.eur = Currency.objects.take(
			alias     = 'EUR',
			name      = 'EUR',
			full_name = 'Euro',
			rate      = 80,
			quantity  = 1)

		self.s      = requests.Session()
		self.cookie = ''


	def take_stock(self, alias_end = 'stock', name_end = 'склад',
				delivery_time_min = 5, delivery_time_max = 10):

		stock = Stock.objects.take(
			alias             = '{}-{}'.format(self.alias, alias_end),
			name              = '{}: {}'.format(self.name, name_end),
			delivery_time_min = delivery_time_min,
			delivery_time_max = delivery_time_max,
			distributor       = self.distributor)

		return stock

	def load_cookie(self, timeout = 100.0):

		try:
			r = self.s.get(self.url['start'], allow_redirects = True,
				timeout = timeout)
			self.cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Ошибка: ревышен интервал ожидания.")
			return None
		except Exception:
			print("Ошибка: нет соединения [{}].".format(url))
			return None

		return True



	def login(self, payload = {}, timeout = 100.0):

		# Параметры авторизации
		if self.updater.login and self.updater.password:
			print('Получены параметры авторизации.')
		else:
			print('Ошибка: отсутствуют параметры авторизации.')
			Log.objects.add(
				subject     = 'catalog.updater.{}'.format(self.updater.alias),
				channel     = 'error',
				title       = 'login error',
				description = 'Ошибка: отсутствуют параметры авторизации.')
			return None

		self.load_cookie()

		# Авторизуемся
		try:
			r = self.s.post(self.url['login'], cookies = self.cookies,
					data = payload, allow_redirects = True, verify = False,
					timeout = timeout)
			self.cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Ошибка: ревышен интервал ожидания.")
			return None
		except Exception:
			print("Ошибка: нет соединения [{}].".format(url))
			return None

		return True


	def load_text(self, url, timeout = 100.0):

		try:
			if 'https://' in url:
				r = self.s.get(url, cookies = self.cookies,
					allow_redirects = False, verify = False, timeout = timeout)
			if 'http://' in url:
				r = self.s.get(url, timeout = timeout)
		except requests.exceptions.Timeout:
			print("Ошибка: ревышен интервал ожидания.")
			return None
		except Exception:
			print("Ошибка: нет соединения [{}].".format(url))
			return None

		return r.text


	def load_html(self, url, timeout = 100.0):

		import lxml.html

		try:
			if 'https://' in url:
				r = self.s.get(url, cookies = self.cookies,
					allow_redirects = False, verify = False, timeout = timeout)
			if 'http://' in url:
				r = self.s.get(url, allow_redirects = True, timeout = timeout)
		except requests.exceptions.Timeout:
			print("Ошибка: ревышен интервал ожидания.")
			return None
		except Exception:
			print("Ошибка: нет соединения [{}].".format(url))
			return None

		try:
			# for test print(r.text[:1000])
			tree = lxml.html.fromstring(r.text)
		except Exception:
			return None
		else:
			return tree


	def load_data(self, url, timeout = 100.0):

		from io import BytesIO

		try:
			r = self.s.get(url, cookies = self.cookies,
					allow_redirects = True, verify = False, timeout = timeout)
		except requests.exceptions.Timeout:
			print("Ошибка: ревышен интервал ожидания.")
			return None
		except Exception:
			print("Ошибка: нет соединения [{}].".format(url))
			return None

		return BytesIO(r.content)


	def fix_price(self, price):

		price = str(price).strip()

		if price in ('Цена не найдена', 'звоните',):
			return None

		translation_map = {
			ord('$') : '', ord(',') : '.', ord(' ') : '',
			ord('р') : '', ord('у') : '',  ord('б') : '',
			ord('R') : '', ord('U') : '',  ord('B') : ''}

		price = price.translate(translation_map)

		try:
			price = float(price)
		except ValueError:
			return None

		if not price:
			return None

		return price


	def fix_quantity(self, quantity):

		quantity = str(quantity).strip()

		try:
			if quantity in ('', '0*'):
				return 0
			elif quantity == 'мало':
				return 5
			elif quantity == 'много':
				return 10
			else:
				return int(quantity)
		except Exception:
			return 0
