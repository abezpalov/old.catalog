from catalog.models import *
from project.models import Log


class Runner:

	name = 'Перерасчет розничных цен и количества'
	alias = 'recalculate'


	def __init__(self):

		self.updater = Updater.objects.take(
			alias = self.alias,
			name  = self.name)


	def run(self):

		products = Product.objects.values('id')

		for n, product in enumerate(products):

			product = Product.objects.get(id = product['id'])

			print('{} of {}. {} {}'.format(
				'{:,}'.format(n+1).replace(',', ' '),
				'{:,}'.format(len(products)).replace(',', ' '),
				product.vendor.name,
				product.article))

			product.recalculate()

		Log.objects.add(
			subject     = "catalog.updater.{}".format(self.updater.alias),
			channel     = "info",
			title       = "Updated",
			description = "Products: {}.".format(
				'{:,}'.format(len(products)).replace(',', ' ')))
