from datetime import date
from datetime import datetime
from catalog.models import Updater
from catalog.models import Quantity


class Runner:


	name = 'Перерасчет количества'
	alias = 'quantity-recalculate'


	def __init__(self):

		# Получаем необходимые объекты
		self.updater = Updater.objects.take(
			alias = self.alias,
			name  = self.name)


	def run(self):

		Quantity.objects.recalculate()
		print("Обновление завершено")

		return True
