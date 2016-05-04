import datetime
from django.utils import timezone
from catalog.models import Updater
from project.models import Log


class Runner:

	name  = 'Служебное: ежедневный запуск'
	alias = 'everyday'

	max_time = datetime.timedelta(0, 82800, 0)

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

			# Проверяем не вышло ли время
			if timezone.now() - self.start > self.max_time:
				print("Время вышло {}.".format(timezone.now() - self.start))
				return True
