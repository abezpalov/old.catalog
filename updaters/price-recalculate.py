from datetime import date
from datetime import datetime
from catalog.models import Updater
from catalog.models import Price


class Runner:


	def __init__(self):

		# Инициируем переменные
		self.name = 'Перерасчет розничных цен'
		self.alias = 'price-recalculate'

		# Получаем необходимые объекты
		self.updater = Updater.objects.take(alias=self.alias, name=self.name)


	def run(self):

		Price.objects.recalculate()
		print("Обновление завершено")

		return True
