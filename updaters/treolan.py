from catalog.models import Updater
from catalog.models import Currency
from catalog.models import CategorySynonym
from datetime import date
from datetime import datetime
import lxml.html
import requests


class Update:


	def __init__(self):

		# Инициируем переменные
		self.name = 'Treolan'
		self.alias = 'treolan'
		self.message = ''

		try: # self.updater
			self.updater = Updater.objects.get(alias=self.alias)
		except Updater.DoesNotExist:
			self.updater = Updater(alias=self.alias, name=self.name, created=datetime.now(), modified=datetime.now())
			self.updater.save()

		try: # self.currency_rub
			self.currency_rub = Currency.objects.get(alias='RUB')
		except Currency.DoesNotExist:
			self.currency_rub = Currency(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1, created=datetime.now(), modified=datetime.now())
			self.currency_rub.save()

		try: # self.currency_usd
			self.currency_usd = Currency.objects.get(alias='USD')
		except Currency.DoesNotExist:
			self.currency_usd = Currency(alias='USD', name='$', full_name='US Dollar', rate=38, quantity=1, created=datetime.now(), modified=datetime.now())
			self.currency_usd.save()

		if self.updater.state: self.run()


	def run(self):

		# Создаем сессию
		s = requests.Session()

		# Авторизуемся
		url = 'https://b2b.treolan.ru/processlogin.asp'
		payload = {'client': 'GST_zhd', 'pass': 'uatokhjt', 'remember': 'on', 'x': '8', 'y': '7'}
		r = s.post(url, data=payload, allow_redirects=False, verify=False)

		# Загружаем общий прайс
		url = 'https://b2b.treolan.ru/catalog.excel.asp?category=04030AB1-678B-457D-8976-AC7297C65CE6&vendor=0&ncfltr=1&daysback=0&reporttype=stock&price_min=&price_max=&hdn_extParams=&tvh=0&srh=&sart=on&podbor=1'
		r = s.get(url, allow_redirects=False, verify=False)
		self.message = r.text
		tree = lxml.html.fromstring(r.text)

		# Парсим
		table = tree.xpath("//table/tr")
		for tr in table:

			# Заголовок таблицы
			if tr.attrib["class"] == "sHead" :
				tdn = 0
				for td in tr :
					if   td.text == 'Артикул'       : nArticle     = tdn
					elif td.text == 'Наименование'  : nName        = tdn
					elif td.text == 'Производитель' : nVendor      = tdn
					elif td.text == 'Св.'           : nStock       = tdn
					elif td.text == 'Св.+Тр.'       : nTransit     = tdn
					elif td.text == 'Б. Тр.'        : nTransitDate = tdn
					elif td.text == 'Цена*'         : nPriceUSD    = tdn
					elif td.text == 'Цена руб.**'   : nPriceRUB    = tdn
					elif td.text == 'Доп.'          : nDop         = tdn
					elif td.text == 'Гар.'          : nWarranty    = tdn
					tdn += 1

			# Категория TODO test
			elif tr.attrib["class"] == "sGroup" :
				categorySynonymName = tr[0].text.strip()
				self.message = categorySynonymName
			try:
				categorySynonym = CategorySynonym.objects.get(name=categorySynonymName)
			except CategorySynonym.DoesNotExist:
				categorySynonym = CategorySynonym(name=categorySynonymName, updater=self.updater, created=datetime.now(), modified=datetime.now())
				categorySynonym.save()

			# Товар
			elif tr.attrib["class"] == "sGroup" :
				tdn = 0
				for td in tr :
					if   tdn == nArticle     : article     = td.text
					elif tdn == nName        : name        = td.text
					elif tdn == nVendor      : vendor      = td.text
					elif tdn == nStock       : stock       = td.text
					elif tdn == nTransit     : transit     = td.text
					elif tdn == nTransitDate : transitDate = td.text
					elif tdn == nPriceUSD    : priceUSD    = td.text
					elif tdn == nPriceRUB    : priceRUB    = td.text
					elif tdn == nDop         : dop         = td.text
					elif tdn == nWarranty    : warranty    = td.text
					tdn += 1

		# Отмечаемся и уходим
		self.updater.modified = datetime.now()
		self.updater.save()
		return True
