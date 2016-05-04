import datetime
from django.utils import timezone
from catalog.models import *
from project.models import Log


class Runner:


	def __init__(self):

		self.name  = 'Служебное: еженедельный запуск'
		self.alias = 'everyweek'
		self.updaters = []

		# Загрузчик
		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = None)


	def run(self):

		start = datetime.datetime.now()

		tasks = UpdaterTask.objects.filter(complite = False)

		print("Нашёл {} задач.".format(len(tasks)))

		for task in tasks:

			try:
				print("Выполняю задачу {}.".format(task))

				Updater = __import__('catalog.updaters.{}'.format(task.updater.alias), fromlist=['Runner'])
				runner = Updater.Runner()

				if 'update.product.description' == task.name:
					runner.update_product_description(task.subject)

					# TODO !!!

			except Exception as error:
				Log.objects.add(
					subject = str(task),
					channel = "error",
					title   = "Exception",
					description = error)

		print("Обработки завершены за {}.".format(datetime.datetime.now() - start))

		return True
