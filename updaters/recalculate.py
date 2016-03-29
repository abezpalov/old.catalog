from catalog.models import *


class Runner:


	name = 'Перерасчет розничных цен и количества'
	alias = 'recalculate'


	def __init__(self):

		# Получаем необходимые объекты
		self.updater = Updater.objects.take(
			alias = self.alias,
			name  = self.name)


	def run(self):

		products = Product.objects.all()

		for n, product in enumerate(products):
			print("{} of {}. {} {}".format(
				str(n+1),
				len(products),
				product.vendor.name,
				product.article))

			product.recalculate()

		Log.objects.add(
			subject     = "catalog.updater.{}".format(self.updater.alias),
			channel     = "info",
			title       = "Updated",
			description = "Обновлены розничные цены и количества: {} шт.".format(len(products)))

		return True
