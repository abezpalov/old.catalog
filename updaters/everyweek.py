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

		for updater in self.updaters:

			# Выполняем необходимый загрузчик
			try:
				print("Пробую выполнить загрузчик {}".format(updater))
				Updater = __import__('catalog.updaters.{}'.format(updater), fromlist=['Runner'])
				runner = Updater.Runner()
				if runner.updater.state:
					if runner.run():
						runner.updater.updated = timezone.now()
						runner.updater.save()

			except Exception as error:
				Log.objects.add(
					subject    = "Catalog Updater Everyweek: {}".format(updater),
					channel    = "error",
					title      = "Exception",
					description = error)

		tasks = UpdaterTask.objects.all()

		print("Нашёл {} задач.".format(len(tasks)))

		for task in tasks:

			Updater = __import__('catalog.updaters.{}'.format(task.updater.alias), fromlist=['Runner'])
			runner = Updater.Runner()

			if 'update.product.description' == task.name:
				runner.updateProductDescription(task.subject)

				# TODO !!!


		print("Обработки завершены за {}.".format(datetime.datetime.now() - start))

		return True
