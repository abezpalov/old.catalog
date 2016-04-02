import datetime
from django.utils import timezone
from catalog.models import Updater
from project.models import Log


class Runner:

	def __init__(self):

		self.name  = 'Служебное: ежедневный запуск'
		self.alias = 'everyday'

		self.updaters = [
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

			'recalculate']

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
					subject    = "Catalog Updater Everyday: {}".format(updater),
					channel    = "error",
					title      = "Exception",
					description = error)

		print("Обработки завершены за {}.".format(datetime.datetime.now() - start))

		return True
