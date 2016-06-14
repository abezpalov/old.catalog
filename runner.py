import requests

from django.utils import timezone

from project.models import Log
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

		self.dp = PriceType.objects.take(
			alias = 'DP', name = 'Диллерская цена')

		self.rp = PriceType.objects.take(
			alias = 'RP', name = 'Розничная цена')

		self.rrp = PriceType.objects.take(
			alias = 'RRP', name  = 'Рекомендованная розничная цена')

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

		self.s = requests.Session()


	def take_stock(self, alias_end = 'stock', name_end = 'склад',
				delivery_time_min = 5, delivery_time_max = 10):

		stock = Stock.objects.take(
			alias             = '{}-{}'.format(self.alias, alias_end),
			name              = '{}: {}'.format(self.name, name_end),
			delivery_time_min = delivery_time_min,
			delivery_time_max = delivery_time_max,
			distributor       = self.distributor)

		return stock


	def take_categorysynonym(self, name):

		return CategorySynonym.objects.take(
			name        = name,
			updater     = self.updater)


	def take_vendorsynonym(self, name):

		return VendorSynonym.objects.take(
			name        = name,
			updater     = self.updater)


	def take_parametersynonym(self, name):

		return ParameterSynonym.objects.take(
			name        = name,
			updater     = self.updater)


	def load(self, url, result_type = None, timeout = 100.0, try_quantity = 10):

		import time

		try:
			self.cookies
		except AttributeError:
			self.cookies = None

		for i in range(try_quantity):

			try:
				if self.cookies is None:
					r = self.s.get(url, allow_redirects = True, verify = False,
						timeout = timeout)
					self.cookies = r.cookies
				else:
					r = self.s.get(url, cookies = self.cookies,
						allow_redirects = True, verify = False, timeout = timeout)
					self.cookies = r.cookies

			except requests.exceptions.Timeout:
				print("Ошибка: превышен интервал ожидания [{}].".format(url))
				if i + 1 == try_quantity:
					return None
				else:
					time.sleep(10)
					print("Пробую ещё раз.")

			except Exception:
				print("Ошибка: нет соединения [{}].".format(url))
				if i + 1 == try_quantity:
					return None
				else:
					time.sleep(10)
					print("Пробую ещё раз.")

			else:
				break

		if result_type == 'cookie':
			return r.cookie
		elif result_type == 'text':
			return r.text
		elif result_type == 'content':
			return r.content
		elif result_type == 'request':
			return r

		return r


	def load_cookie(self, timeout = 100.0):

		self.load(self.url['start'], timeout = 100.0)

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

		return self.load(url, result_type = 'text', timeout = 100.0)


	def load_html(self, url, timeout = 100.0):

		import lxml.html

		text = self.load(url, result_type = 'text', timeout = 100.0)

		try:
			tree = lxml.html.fromstring(text)

		except Exception:
			return None

		return tree


	def load_xml(self, url, timeout = 100.0):

		import lxml.etree

		text = self.load(url, result_type = 'text', timeout = 500.0)

		try:
			tree = lxml.etree.fromstring(text.encode('utf-8'))

		except Exception:
			return None

		return tree


	def load_data(self, url, timeout = 100.0):

		from io import BytesIO

		content = self.load(url, result_type = 'content', timeout = 100.0)

		return BytesIO(content)


	def unpack(self, data):

		from catalog.lib.zipfile import ZipFile

		try:
			zip_data = ZipFile(data)
			data = zip_data.open(zip_data.namelist()[0])
		except Exception:
			return None
		else:
			return data


	def fix_price(self, price):

		price = str(price).strip()

		if price in ('Цена не найдена', 'звоните', 'CALL', '?',):
			return None

		translation_map = {
			ord('$') : '', ord('€') : '', ord(' ') : '',
			ord('р') : '', ord('у') : '', ord('б') : '',
			ord('R') : '', ord('U') : '', ord('B') : '',
			ord('+') : '', ord(',') : '.'}

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
			if quantity in ('', '0*', 'call'):
				return 0

			elif quantity == 'Есть':
				return 1

			elif quantity in('мало', '+', '+ '):
				return 5

			elif quantity in ('много', '++', '++ '):
				return 10

			elif quantity in ('+++', '+++ '):
				return 50

			elif quantity in ('++++', '++++ '):
				return 100

			else:
				return int(quantity)

		except Exception:
			return 0


	def log(self):

		if self.count['product'] and self.count['party']:
			Log.objects.add(
				subject     = "catalog.updater.{}".format(self.updater.alias),
				channel     = "info",
				title       = "Updated",
				description = "Updated: products - {}; parties - {}.".format(
					'{:,}'.format(self.count['product']).replace(',', ' '),
					'{:,}'.format(self.count['party']).replace(',', ' ')))

		else:
			Log.objects.add(
				subject     = "catalog.updater.{}".format(self.updater.alias),
				channel     = "error",
				title       = "Error",
				description = "Updated error: products - {}; parties - {}.".format(
					'{:,}'.format(self.count['product']).replace(',', ' '),
					'{:,}'.format(self.count['party']).replace(',', ' ')))
