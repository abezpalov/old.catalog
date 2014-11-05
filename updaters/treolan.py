from catalog.models import Updater, Currency, CategorySynonym, VendorSynonym, Category, Vendor
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
			self.updater = Updater(alias=self.alias, name=self.name, created=datetime.now(), modified=datetime.now(), updated=datetime.now())
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

		# Получаем куки
		url = 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2f'
		r = s.get(url)
		cookies = r.cookies

		# Авторизуемся
		url = 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F'
		payload = {'UserName': 'GST_zhd', 'Password': 'uatokhjt', 'RememberMe': 'false'}
		r = s.post(url, cookies=cookies, data=payload, allow_redirects=True, verify=False)
		cookies = r.cookies

		# Загружаем общий прайс
		url = 'https://b2b.treolan.ru/Catalog/SearchToExcel?&comodity=true&withMarketingProgramsOnly=false&availableAtStockOnly=false&rusDescription=true&condition=0&catalogProductsOnly=true&order=0&getExcel=true&searchBylink=false&take=50&skip=0'
		r = s.get(url, cookies=cookies, allow_redirects=False, verify=False)
		# self.message = r.text+"\n"
		self.message += "Прайс загружен.\n"
		tree = lxml.html.fromstring(r.text)

		# Парсим
		table = tree.xpath("//table")[0]
		head = True;
		for tr in table:

			# Заголовок таблицы
			if True == head :
				tdn = 0
				n = 0
				for td in tr :
					if td[0].text == 'Артикул' :
						nArticle = tdn
						n += 1
					elif td[0].text == 'Наименование' :
						nName = tdn
						n += 1
					elif td[0].text == 'Производитель' :
						nVendor = tdn
						n += 1
					elif td[0].text == 'Св.' :
						nStock = tdn
						n += 1
					elif td[0].text == 'Св.+Тр.' :
						nTransit = tdn
						self.message += str(tdn) + "\n"
						n += 1
					elif td[0].text == 'Б. Тр.' :
						nTransitDate = tdn
						self.message += str(tdn) + "\n"
						n += 1
					elif td[0].text == 'Цена*' :
						nPriceUSD = tdn
						self.message += str(tdn) + "\n"
						n += 1
					elif td[0].text == 'Цена руб.**' :
						nPriceRUB = tdn
						self.message += str(tdn) + "\n"
						n += 1
					elif td[0].text == 'Доп.' :
						nDop = tdn
						self.message += str(tdn) + "\n"
						n += 1
					tdn += 1

				# Проверяем, все ли столбцы распознались
				if n < 8 :
					self.message += "Ошибка структуры данных: не все столбцы опознаны.\n"
					return False

			# Категория
			elif len(tr) == 1 :
				# Обрабатываем синоним категории
				categorySynonymName = tr[0][0].text.strip()
				try:
					categorySynonym = CategorySynonym.objects.get(name=categorySynonymName)
				except CategorySynonym.DoesNotExist:
					categorySynonym = CategorySynonym(name=categorySynonymName, updater=self.updater, created=datetime.now(), modified=datetime.now())
					categorySynonym.save()

			# Товар
			elif len(tr) == 9 :
				tdn = 0
				for td in tr :
					if   tdn == nArticle :
						article = str(td.text).strip()
					elif tdn == nName :
						name = str(td.text).strip()
					elif tdn == nVendor :
						vendorSynonymName = str(td.text).strip()
					elif tdn == nStock :
						stock = str(td.text).strip()
					elif tdn == nTransit :
						transit = str(td.text).strip()
					elif tdn == nTransitDate :
						transitDate = str(td.text).strip()
					elif tdn == nPriceUSD :
						priceUSD = str(td.text).strip()
					elif tdn == nPriceRUB :
						priceRUB = str(td.text).strip()
					elif tdn == nDop :
						dop = str(td.text).strip()
					tdn += 1

				# Обрабатываем синоним производителя
				if vendorSynonymName != "" :
					try:
						vendorSynonym = VendorSynonym.objects.get(name=vendorSynonymName)
					except VendorSynonym.DoesNotExist:
						vendorSynonym = VendorSynonym(name=vendorSynonymName, updater=self.updater, created=datetime.now(), modified=datetime.now())
						vendorSynonym.save()

				# Обрабатываем товар

				# Обрабатываем партии

			head = False


		# Обрабатываем цены

		# Отмечаемся и уходим
		self.updater.updated = datetime.now()
		self.updater.save()
		return True
