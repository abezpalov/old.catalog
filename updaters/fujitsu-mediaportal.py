from catalog.models import Updater
from catalog.models import Distributor
from catalog.models import Vendor


class Runner:


	name = 'Fujitsu'
	alias = 'fujitsu'


	def __init__(self):

		# Дистрибьютор
		self.distributor = Distributor.objects.take(
			alias = self.alias,
			name  = self.name)

		# Загрузчик
		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = self.distributor)

		# Производитель
		self.vendor = Vendor.objects.take(
			alias = self.alias,
			name  = self.name)

		# Используемые ссылки
		self.url = {
			'start':    'http://mediaportal.ts.fujitsu.com/pages/home.php',
			'base':     'http://mediaportal.ts.fujitsu.com/',
			'external': '//',
			'self':     '#',
			'js':       'JavaScript:'}

	def run(self):

		import lxml.html
		import requests

		links = []

		# Создаем сессию
		s = requests.Session()

		# Зогружаем первую страницу
		try:
			r = s.get(self.url['start'], allow_redirects = True, timeout = 30.0)
			cookies = r.cookies
		except requests.exceptions.Timeout:
			print("Превышен интервал ожидания загрузки первой страницы.")
			return False

		# Получаем ссылки со страницы
		tree = lxml.html.fromstring(r.text)
		urls = tree.xpath('//a/@href')
		for url in urls:

			# Просеиваем ссылки
			if self.url['base'] in url:
				print(url)
			elif self.url['base'] in url:
				url = None
			elif self.url['external'] in url:
				url = None
			elif self.url['js'] in url:
				url = None
			elif self.url['self'] == url:
				url = None
			else:
				url = self.url['base'] + url

			if url and not url in links:
				links.append(url)

		for link in links:
			print(link)

