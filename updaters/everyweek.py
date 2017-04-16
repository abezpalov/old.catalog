import datetime
from django.utils import timezone
from catalog.models import *
from anodos.models import Log


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

		from django.db.models import Count

		start = datetime.datetime.now()

		tasks = UpdaterTask.objects.filter(complite = False, name = 'update.product.description').values('updater').annotate(count = Count('updater')).order_by()

		for task in tasks:

#			print('Updater id: {}.'.format(task['updater']))
#			print('Task quantity: {}.'.format(task['count']))

			updater = Updater.objects.get(id = task['updater'])

			print("Загрузчик: {}.".format(updater.name))

			runner = __import__('catalog.updaters.{}'.format(updater.alias), fromlist=['Runner']).Runner()


#			try:
			runner.update_products_description()

				# TODO !!!

#			except Exception as error:
#				Log.objects.add(
#					subject = str('{} update.products.description'.format(updater.name)),
#					channel = "error",
#					title   = "Exception",
#					description = error)

		print("Обработки завершены за {}.".format(datetime.datetime.now() - start))

		return True
