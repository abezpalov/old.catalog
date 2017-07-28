""" Шаблон дистрибьюторского загрузчика

"""

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

	name  = ''
	alias = ''
	url = {
		'start'  : '',
		'login'  : '',
		'price'  : ''}


	def __init__(self):

		super().__init__()

		self.stock = self.take_stock('stock', 'склад', 3, 10)


	def run(self):

		# Авторизуемся
		payload = {}
		self.login(payload)

		# Получаем данные
		###

		# Парсим
		###

		# Пишем устаревшие партии
		Party.objects.clear(stock = self.stock, time = self.start_time)

		# Пишем результат в лог
		self.log()


	def parse(self, data):
		pass
