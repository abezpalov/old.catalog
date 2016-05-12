import datetime
from django.utils import timezone
from catalog.models import *
from project.models import Log


class Runner:

	name  = 'Служебное: ежедневный запуск'
	alias = 'everyday'

	max_time = datetime.timedelta(0, 22*60*60, 0)

	updaters = [
		'cbr',

		'axoft',
		'cmo',
		'digis',
		'fujitsu',
		'kramer',
		'landata',
		'marvel',
		'merlion',
		'ocs',
		'rrc',
		'treolan',
		'mics',

		'recalculate']

	def __init__(self):

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
				Runner = __import__('catalog.updaters.' + updater, fromlist=['Runner'])
				runner = Runner.Runner()
				if runner.updater.state:
					if runner.run():
						runner.updater.updated = timezone.now()
						runner.updater.save()

			except Exception as error:
				Log.objects.add(
					subject    = "catalog.updater.{}".format(updater),
					channel    = "error",
					title      = "Exception",
					description = error)

		print("Обработки завершены за {}.".format(datetime.datetime.now() - start))

		tasks = UpdaterTask.objects.filter(complite = False, name = 'update.product.description').values('updater').annotate(count = Count('updater')).order_by()

		for task in tasks:

			updater = Updater.objects.get(id = task['updater'])

			print("Загрузчик: {}.".format(updater.name))

			runner = __import__('catalog.updaters.{}'.format(updater.alias), fromlist=['Runner']).Runner()

			try:
				runner.update_products_description()

				# TODO !!!

			except Exception as error:
				Log.objects.add(
					subject = str('{} update.products.description'.format(updater.name)),
					channel = "error",
					title   = "Exception",
					description = error)

			# Проверяем не вышло ли время
			if timezone.now() - self.start > self.max_time:
				print("Время вышло {}.".format(timezone.now() - self.start))
				return True

		print("Обработки завершены за {}.".format(datetime.datetime.now() - start))

		return True
