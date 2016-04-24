# Шаблон дистрибьюторского загрузчика

from project.models import Log

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

		self.count = {
			'product' : 0,
			'party'   : 0}

	def run(self):

		payload = {}
		self.login(payload)

		###

		Party.objects.clear(stock = self.stock, time = self.start_time)

		Log.objects.add(
			subject     = "catalog.updater.{}".format(self.updater.alias),
			channel     = "info",
			title       = "Updated",
			description = "Products: {}; Parties: {}.".format(
				self.count['product'],
				self.count['party']))
