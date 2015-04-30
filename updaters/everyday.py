from catalog.models import Updater
from catalog.models import Log


class Runner:

	name  = 'Служебное: ежедневный запуск'
	alias = 'everyday'

	updaters = [
		'cbr',

		'axoft',
		'digis',
		'landata',
		'merlion',
		'ocs',
		'rrc',
		'treolan',
		'cmo',
		'kramer',

		'fujitsu',
		'marvel',

		'price-recalculate',
		'quantity-recalculate']

	def __init__(self):

		# Загрузчик
		self.updater = Updater.objects.take(
			alias       = self.alias,
			name        = self.name,
			distributor = None)


	def run(self):

		import datetime
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
			except Exception  as error:
				Log.objects.add(
					subject    = "everyday: {}".format(updater),
					channel    = "error",
					title      = "ConnectionError",
					description = error)

		print("Обработки завершены за {}.".format(datetime.datetime.now() - start))

		return True
