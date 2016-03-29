import requests
import lxml.html
from datetime import date
from django.utils import timezone
from catalog.models import *
from project.models import Log

class Runner:


	name  = 'Обновление курсов валют (Центральный банк России)'
	alias = 'cbr'
	count = 0


	def __init__(self):

		# Загрузчик
		self.updater = Updater.objects.take(
			alias = self.alias,
			name  = self.name)

		# Основная валюта
		self.rub = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  = 1)

		self.url = 'http://cbr.ru/eng/currency_base/D_print.aspx?date_req={}'\
			.format(date.today().strftime("%d.%m.%Y"))


	def run(self):

		# Номера строк и столбцов
		num = {'header': 0}

		# Распознаваемые слова
		word = {
			'alias':    'Char code',
			'quantity': 'Unit',
			'name':     'Currency',
			'rate':     'Rate'}

		# Создаем сессию
		s = requests.Session()

		# Загружаем данные
		try:
			r = s.get(self.url, timeout = 100.0)
			tree = lxml.html.fromstring(r.text)
		except requests.exceptions.Timeout:
			Log.objects.add(
				subject     = "updater.{}".format(self.updater.alias),
				channel     = "error",
				title       = "requests.exceptions.Timeout",
				description = "Превышение интервала ожидания загрузки.")
			return False

		table = tree.xpath("//table[@class='CBRTBL']/tr")
		for trn, tr in enumerate(table):

			# Заголовок таблицы
			if trn == num['header']:
				for tdn, td in enumerate(tr):
					if   td[0].text == word['alias']:    num['alias']    = tdn
					elif td[0].text == word['quantity']: num['quantity'] = tdn
					elif td[0].text == word['name']:     num['name']     = tdn
					elif td[0].text == word['rate']:     num['rate']     = tdn

			# Валюта
			else:

				# Определяем значения переменных
				alias    = tr[num['alias']].text.strip()
				quantity = tr[num['quantity']].text.strip()
				name     = tr[num['name']].text.strip()
				rate     = tr[num['rate']].text.strip()

				# Записываем информацию в базу
				currency = Currency.objects.take(
					alias     = alias,
					name      = name,
					full_name = name,
					rate      = rate,
					quantity  = quantity)
				currency.rate     = rate
				currency.quantity = quantity
				currency.modified = timezone.now()
				currency.save()

				self.count += 1
				print('{} = {} / {}'.format(
					currency.alias,
					currency.rate,
					currency.quantity))

		Log.objects.add(
			subject     = "updater.{}".format(self.updater.alias),
			channel     = "info",
			title       = "Updated",
			description = "Обновлены курсы валют: {} шт.".format(self.count))

		return True
