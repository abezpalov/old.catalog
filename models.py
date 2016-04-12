import uuid
from django.db import models
from django.utils import timezone


class ConnectorManager(models.Manager):


	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result


	def take(self, *args, **kwargs):

		alias = str(kwargs.get('alias', '')).strip()
		name  = str(kwargs.get('name', '')).strip()

		if not alias:
			return None

		try:
			result = self.get(alias = alias)

		except self.DoesNotExist:

			if not name:
				return None

			result = Connector(
				alias    = alias,
				name     = name,
				created  = timezone.now(),
				modified = timezone.now())
			result.save()

		return result

class Connector(models.Model):

	name     = models.CharField(max_length = 100)
	alias    = models.CharField(max_length = 100, unique = True)
	login    = models.CharField(max_length = 100)
	password = models.CharField(max_length = 100)
	state    = models.BooleanField(default = True)
	created  = models.DateTimeField()
	modified = models.DateTimeField()

	objects  = ConnectorManager()


	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['alias']    = self.alias
		result['login']    = self.login
		result['password'] = self.password
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class DistributorManager(models.Manager):


	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result


	def take(self, *args, **kwargs):

		alias = str(kwargs.get('alias', '')).strip()
		name  = str(kwargs.get('name', '')).strip()

		if not alias:
			return None

		try:
			result = self.get(alias = alias)

		except self.DoesNotExist:

			if not name:
				return None

			result = Connector(
				alias    = alias,
				name     = name,
				created  = timezone.now(),
				modified = timezone.now())
			result.save()

		return result


class Distributor(models.Model):

	name        = models.CharField(max_length = 100)
	alias       = models.CharField(max_length = 100, unique = True)
	description = models.TextField()
	connector   = models.ForeignKey(Connector, null = True, default = None)
	state       = models.BooleanField(default = True)
	created     = models.DateTimeField()
	modified    = models.DateTimeField()

	objects     = DistributorManager()


	def getDicted(self):

		result = {}

		result['id']          = self.id
		result['name']        = self.name
		result['alias']       = self.alias
		result['description'] = self.description
		result['state']       = self.state
		result['created']     = str(self.created)
		result['modified']    = str(self.modified)

		try:    result['connector'] = self.connector.getDicted()
		except: result['connector'] = None

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class UpdaterManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, alias, name, distributor = None):
		try:
			updater = self.get(alias = alias)
		except Updater.DoesNotExist:
			updater = Updater(
				alias       = alias,
				name        = name,
				distributor = distributor,
				created     = timezone.now(),
				modified    = timezone.now(),
				updated     = timezone.now())
			updater.save()
		return updater


class Updater(models.Model):

	name        = models.CharField(max_length = 100)
	alias       = models.CharField(max_length = 100, unique = True)
	distributor = models.ForeignKey(Distributor, null = True, default = None)
	login       = models.CharField(max_length = 100)
	password    = models.CharField(max_length = 100)
	state       = models.BooleanField(default = True)
	created     = models.DateTimeField()
	modified    = models.DateTimeField()
	updated     = models.DateTimeField()

	objects     = UpdaterManager()

	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['alias']    = self.alias
		result['login']    = self.login
		result['password'] = self.password
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)
		result['updated']  = str(self.updated)

		try:    result['distributor'] = self.distributor.getDicted()
		except: result['distributor'] = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class StockManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, alias, name, delivery_time_min = 10, delivery_time_max = 20,
			distributor=None):
		try:
			stock = self.get(alias = alias)
		except Stock.DoesNotExist:
			stock = Stock(
				alias             = alias,
				name              = name,
				delivery_time_min = delivery_time_min,
				delivery_time_max = delivery_time_max,
				distributor       = distributor,
				created           = timezone.now(),
				modified          = timezone.now())
			stock.save()
		return stock


class Stock(models.Model):

	name              = models.CharField(max_length = 100)
	alias             = models.CharField(max_length = 100, unique = True)
	distributor       = models.ForeignKey(Distributor, null = True, default = None)
	delivery_time_min = models.IntegerField()
	delivery_time_max = models.IntegerField()
	state             = models.BooleanField(default = True)
	created           = models.DateTimeField()
	modified          = models.DateTimeField()

	objects           = StockManager()

	def getDicted(self):

		result = {}

		result['id']                = self.id
		result['name']              = self.name
		result['alias']             = self.alias
		result['delivery_time_min'] = self.delivery_time_min
		result['delivery_time_max'] = self.delivery_time_max
		result['state']             = self.state
		result['created']           = str(self.created)
		result['modified']          = str(self.modified)

		try:    result['distributor'] = self.distributor.getDicted()
		except: result['distributor'] = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class CategoryManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def getCategoryTree(self, tree, parent = None):
		"Функция: дерево категорий (используется рекурсия)."

		# Получаем список дочерних категорий
		categories = self.filter(parent = parent).order_by('order')

		# Проходим по списку категорий с рекурсивным погружением
		for category in categories:
			tree.append(category)
			tree = self.getCategoryTree(tree, category)

		return tree


	def getCategoryHTMLTree(self, root, parent = None, first = None):
		"Функция: дерево категорий (используется рекурсия)."

		# Импортируем
		from lxml import etree

		# Получаем список дочерних категорий
		categories = self.filter(parent = parent).filter(state = True).order_by('order')

		# Проходим по списку категорий с рекурсивным погружением
		if len(categories):
			ul = etree.SubElement(root, "ul")
			ul.attrib['class'] = 'no-bullet'
			if first:
				li = etree.SubElement(ul, "li")
				i = etree.SubElement(li, "i")
				i.text = ''
				i.attrib['class'] = 'fa fa-circle-thin'
				a = etree.SubElement(li, "a")
				a.attrib['data-do'] = 'filter-products-select-category'
				a.attrib['data-id'] = ''
				a.attrib['class'] = 'tm-li-category-name'
				a.text = 'Все категории'

			for category in categories:
				li = etree.SubElement(ul, "li")

				# Если есть дочерние
				childs = self.filter(parent=category).filter(state=True).order_by('order')
				if len(childs):
					li.attrib['class'] = 'closed'
					i = etree.SubElement(li, "i")
					i.attrib['data-do'] = 'switch-li-status'
					i.attrib['data-state'] = 'closed'
					i.text = ''
					i.attrib['class'] = 'fa fa-plus-square-o'
				else:
					i = etree.SubElement(li, "i")
					i.text = ''
					i.attrib['class'] = 'fa fa-circle-thin'
				a = etree.SubElement(li, "a")
				a.attrib['data-do'] = 'filter-products-select-category'
				a.attrib['data-id'] = str(category.id)
				a.attrib['class'] = 'tm-li-category-name'
				a.text = category.name
				self.getCategoryHTMLTree(li, category)

		# Возвращаем результат
		return root


class Category(models.Model):

	name        = models.TextField()
	name_search = models.CharField(max_length = 512, null = True)
	alias       = models.CharField(max_length = 100)
	description = models.TextField()
	parent      = models.ForeignKey('self', null = True, default = None)
	level       = models.IntegerField()
	order       = models.IntegerField()
	path        = models.CharField(max_length = 512)
	state       = models.BooleanField(default = True)
	created     = models.DateTimeField()
	modified    = models.DateTimeField()

	objects     = CategoryManager()

	def getDicted(self):

		result = {}

		result['id']          = self.id
		result['name']        = self.name
		result['name_search'] = self.name_search
		result['alias']       = self.alias
		result['description'] = self.description
		result['level']       = self.level
		result['order']       = self.order
		result['path']        = self.path
		result['state']       = self.state
		result['created']     = str(self.created)
		result['modified']    = str(self.modified)

		try:    result['parent'] = self.parent.getDicted()
		except: result['parent'] = None

		return result

	def __str__(self):
		return self.name_search

	class Meta:
		ordering = ['order']


class VendorManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, alias, name):
		try:
			vendor = self.get(alias=alias)
		except Vendor.DoesNotExist:
			vendor = Vendor(alias=alias, name=name, created=timezone.now(), modified=timezone.now())
			vendor.save()
		return vendor


class Vendor(models.Model):

	name        = models.CharField(max_length = 100, unique = True)
	alias       = models.CharField(max_length = 100, unique = True)
	description = models.TextField()
	state       = models.BooleanField(default = True)
	created     = models.DateTimeField()
	modified    = models.DateTimeField()

	objects     = VendorManager()

	def getDicted(self):

		result = {}

		result['id']          = self.id
		result['name']        = self.name
		result['alias']       = self.alias
		result['description'] = self.description
		result['state']       = self.state
		result['created']     = str(self.created)
		result['modified']    = str(self.modified)

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class UnitManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, alias, name):
		try:
			unit = self.get(alias=alias)
		except Unit.DoesNotExist:
			unit = Unit(
				alias    = alias,
				name     = name,
				created  = timezone.now(),
				modified = timezone.now())
			unit.save()
		return unit


class Unit(models.Model):

	name     = models.CharField(max_length = 100, unique = True)
	alias    = models.CharField(max_length = 100, unique = True)
	state    = models.BooleanField(default = True)
	created  = models.DateTimeField()
	modified = models.DateTimeField()

	objects  = UnitManager()

	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['alias']    = self.alias
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class PriceTypeManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, alias, name):
		try:
			price_type = self.get(alias=alias)
		except PriceType.DoesNotExist:
			price_type = PriceType(
				alias    = alias,
				name     = name,
				created  = timezone.now(),
				modified = timezone.now())
			price_type.save()
		return price_type


class PriceType(models.Model):

	name       = models.CharField(max_length = 100)
	alias      = models.CharField(max_length = 100, unique = True)
	state      = models.BooleanField(default = True)
	multiplier = models.DecimalField(max_digits = 10, decimal_places = 4, default = 1.0)
	created    = models.DateTimeField()
	modified   = models.DateTimeField()

	objects    = PriceTypeManager()

	def getDicted(self):

		result = {}

		result['id']         = self.id
		result['name']       = self.name
		result['alias']      = self.alias
		result['state']      = self.state
		result['multiplier'] = str(self.multiplier)
		result['created']    = str(self.created)
		result['modified']   = str(self.modified)

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class CurrencyManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, alias, name, full_name, rate = 1, quantity = 1):
		try:
			currency = self.get(alias = alias)
		except Currency.DoesNotExist:
			currency = Currency(
				alias     = alias,
				name      = name,
				full_name = full_name,
				rate      = rate,
				quantity  = quantity,
				created   = timezone.now(),
				modified  = timezone.now())
			currency.save()
		return currency


class Currency(models.Model):
	name      = models.CharField(max_length = 100)
	full_name = models.CharField(max_length = 100)
	alias     = models.CharField(max_length = 100, unique = True)
	rate      = models.DecimalField(max_digits = 10, decimal_places = 4)
	quantity  = models.DecimalField(max_digits = 10, decimal_places = 3)
	state     = models.BooleanField(default = True)
	created   = models.DateTimeField()
	modified  = models.DateTimeField()

	objects   = CurrencyManager()

	def getDicted(self):

		result = {}

		result['id']        = self.id
		result['name']      = self.name
		result['full_name'] = self.full_name
		result['alias']     = self.alias
		result['rate']      = str(self.rate)
		result['quantity']  = str(self.quantity)
		result['state']     = self.state
		result['created']   = str(self.created)
		result['modified']  = str(self.modified)

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['alias']


class Price(models.Model):
	price      = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None)
	price_type = models.ForeignKey(PriceType, null = True, default = None)
	currency   = models.ForeignKey(Currency, null = True, default = None)
	fixed      = models.BooleanField(default = False)
	state      = models.BooleanField(default = True)
	created    = models.DateTimeField()
	modified   = models.DateTimeField()


	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['price']    = str(self.price)
		result['fixed']    = self.fixed
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:    result['price_type'] = self.price_type.getDicted()
		except: result['price_type'] = None

		try:    result['currency'] = self.currency.getDicted()
		except: result['currency'] = None

		result['price_str'] = self._get_price_str()
		result['price_xml'] = self._get_price_xml()

		return result

	def _get_price_str(self):

		try:
			price    = self.price
			currency = self.currency
		except: return ''

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', ' ')
			price = price.replace('.', ',')
			price = price + ' ' + currency.name
		else: return ''

		return price

	price_str = property(_get_price_str)

	def _get_price_xml(self):

		try:
			price    = self.price
			currency = self.currency
		except: return ''

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', '&nbsp;')
			price = price.replace('.', ',')
			price = price + '&nbsp;' + currency.name
		else: return '<i class="fa fa-phone"></i>'

		return price

	price_xml = property(_get_price_xml)

	class Meta:
		ordering = ['-created']


class Quantity(models.Model):

	on_stock   = models.IntegerField(null = True, default = None)
	on_transit = models.IntegerField(null = True, default = None)
	on_factory = models.IntegerField(null = True, default = None)
	unit       = models.ForeignKey(Unit, null = True, default = None)
	fixed      = models.BooleanField(default = False)
	state      = models.BooleanField(default = True)
	created    = models.DateTimeField()
	modified   = models.DateTimeField()


	def getDicted(self):

		result = {}

		result['id']         = self.id
		result['on_stock']   = self.on_stock
		result['on_transit'] = self.on_transit
		result['on_factory'] = self.on_factory
		result['fixed']      = self.fixed
		result['state']      = self.state
		result['created']    = str(self.created)
		result['modified']   = str(self.modified)

		try:    result['unit'] = self.unit.getDicted()
		except: result['unit'] = None

		return result

	class Meta:
		ordering = ['-created']


class ProductManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, article, vendor, name, category = None, unit = None,
			description = None):

		name = str(name).strip()
		name = name.replace("\u00AD", "")
		name = name.replace("™", "")
		name = name.replace("®", "")

		article = str(article).strip()
		article = article.replace("\u00AD", "")
		article = article.replace("™", "")
		article = article.replace("®", "")
		article = article[:100]

		try:
			product = self.get(article = article, vendor = vendor)
			if not product.category and category:
				product.category = category
				product.modified = timezone.now()
				product.save()
			if not product.description and description:
				product.description = description
				product.modified    = timezone.now()
				product.save()
		except Product.DoesNotExist:
			product = Product(
				name        = name,
				name_search = name[:512],
				article     = article,
				vendor      = vendor,
				category    = category,
				unit        = unit,
				created     = timezone.now(),
				modified    = timezone.now())
			product.save()
		except Product.MultipleObjectsReturned:
			print("MultipleObjectsReturned: {} {}".format(vendor, article))
			products = self.get(article = article, vendor = vendor)
			product  = products[0]

		if product.duble:
			product = self.get(id = product.duble)

		print('{} {}'.format(
			product.vendor,
			product.article))

		return product

	def fixNames(self):
		products = self.all()
		for product in products:
			product.name     = product.name.replace("\u00AD", '')
			product.modified = timezone.now()
			product.save()
		return True


class Product(models.Model):

	name        = models.TextField()
	name_search = models.CharField(max_length = 512, null = True)
	article     = models.CharField(max_length = 100)
	vendor      = models.ForeignKey(Vendor)
	category    = models.ForeignKey(Category, null = True, default = None)
	unit        = models.ForeignKey(Unit, null = True, default = None)
	description = models.TextField()
	duble       = models.ForeignKey('self', null = True, default = None)
	edited      = models.BooleanField(default = False)
	state       = models.BooleanField(default = True)
	price       = models.ForeignKey(Price, null = True, default = None)
	quantity    = models.ForeignKey(Quantity, null = True, default = None)
	created     = models.DateTimeField()
	modified    = models.DateTimeField()

	objects     = ProductManager()

	def getDicted(self):

		result = {}

		result['id']          = self.id
		result['name']        = self.name
		result['name_search'] = self.name_search
		result['article']     = self.article
		result['description'] = self.description
		result['edited']      = self.edited
		result['state']       = self.state
		result['created']     = str(self.created)
		result['modified']    = str(self.modified)

		try:    result['vendor']   = self.vendor.getDicted()
		except: result['vendor']   = None

		try:    result['category'] = self.category.getDicted()
		except: result['category'] = None

		try:    result['unit']     = self.unit.getDicted()
		except: result['unit']     = None

		try:    result['duble']    = self.duble.getDicted()
		except: result['duble']    = None

		try:    result['price']    = self.price.getDicted()
		except: result['price']    = None

		try:    result['quantity'] = self.quantity.getDicted()
		except: result['quantity'] = None

		return result

	def __str__(self):
		return self.name

	def recalculate(self):

		from catalog.models import Party
		from catalog.models import Unit
		from catalog.models import Currency
		from catalog.models import PriceType

		# Определяем переменные
		rp = PriceType.objects.take(
			alias = 'RP',
			name  = 'Розничная цена')

		rub = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  = 1)

		# Получаем партии продукта
		parties = Party.objects.filter(product=self)

		# Получаем объект количества
		if self.quantity:
			quantity = self.quantity
		else:
			quantity = Quantity()
			quantity.created = timezone.now()

		# Вычисляем количество товара
		on_stock   = [0]
		on_transit = [0]
		on_factory = [0]

		for party in parties:
			if party.quantity:
				if 'stock' in party.stock.alias:
					on_stock.append(party.quantity)
				elif 'transit' in party.stock.alias:
					on_transit.append(party.quantity)
				elif 'factory' in party.stock.alias:
					on_factory.append(party.quantity)
				elif 'delivery' in party.stock.alias:
					on_factory.append(party.quantity)

		# Записываем информацию в базу
		if -1 in on_stock: quantity.on_stock = -1
		else: quantity.on_stock = sum(on_stock)

		if -1 in on_transit: quantity.on_transit = -1
		else: quantity.on_transit = sum(on_transit)

		if -1 in on_factory: quantity.on_factory = -1
		else: quantity.on_factory = sum(on_factory)

		quantity.modified = timezone.now()
		quantity.save()

		# Если объект количества не привязан к продукту, привязываем
		if self.quantity is None:
			self.quantity = quantity
			self.save()

		# Получаем цену
		if self.price:
			price = self.price
		else:
			price = Price()
			price.created = timezone.now()

		# Вычисляем розничные цены на основании входных цен
		prices = []
		for party in parties:
			if party.price and party.currency and party.price_type:
				prices.append(party.price * party.currency.rate * party.price_type.multiplier / party.currency.quantity)

		# Записываем лучшую в базу
		if len(prices):
			price.price      = min(prices)
			price.price_type = rp
			price.currency   = rub
		else:
			price.price      = None
			price.price_type = rp
			price.currency   = rub
		price.modified = timezone.now()
		price.save()

		# Если цена не привязана к продукту, привязываем
		if self.price is None:
			self.price = price
			self.save()

		return True


	class Meta:
		ordering = ['name']


class PartyManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def make(self, product, stock, article = None,
			price = None, price_type = None, currency = None,
			price_out = None, price_type_out = None, currency_out = None,
			quantity = None, unit = None, time = None):

		if time:
			Party.objects.filter(product = product, stock = stock, created__gt = time).delete()

		party = Party(
			product        = product,
			stock          = stock,
			article        = article,
			price          = price,
			price_type     = price_type,
			currency       = currency,
			price_out      = price_out,
			price_type_out = price_type_out,
			currency_out   = currency,
			quantity       = quantity,
			unit           = unit,
			created        = timezone.now(),
			modified       = timezone.now())
		party.save()

		party.product.recalculate()

		return party


	def clear(self, stock, time = None):
		if time:
			Party.objects.filter(stock = stock, created__gt = time).delete()
		else:
			Party.objects.filter(stock = stock).delete()
		return True


class Party(models.Model):

	id             = models.CharField(max_length = 100, primary_key = True, default = uuid.uuid4, editable = False)
	product        = models.ForeignKey(Product)
	stock          = models.ForeignKey(Stock)
	article        = models.CharField(max_length = 100, null = True, default = None) # Артикул поставщика
	price          = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None)
	price_type     = models.ForeignKey(PriceType, null = True, default = None)
	currency       = models.ForeignKey(Currency, null = True, default = None)
	price_out      = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None)
	price_type_out = models.ForeignKey(PriceType, related_name = 'party_requests_currency_out', null = True, default = None)
	currency_out   = models.ForeignKey(Currency, related_name = 'party_requests_currency_out', null = True, default = None)
	quantity       = models.IntegerField(null = True, default = None)
	unit           = models.ForeignKey(Unit, null = True, default = None)
	comment        = models.TextField()
	state          = models.BooleanField(default = True)
	created        = models.DateTimeField()
	modified       = models.DateTimeField()

	objects        = PartyManager()

	def getDicted(self):

		result = {}

		result['id']        = self.id
		result['article']   = self.article
		result['price']     = str(self.price)
		result['price_out'] = self.price_out
		result['quantity']  = self.description
		result['comment']   = self.comment
		result['state']     = self.state
		result['created']   = str(self.created)
		result['modified']  = str(self.modified)

		try:    result['product']        = self.product.getDicted()
		except: result['product']        = None

		try:    result['stock']          = self.stock.getDicted()
		except: result['stock']          = None

		try:    result['price_type']     = self.price_type.getDicted()
		except: result['price_type']     = None

		try:    result['currency']       = self.currency.getDicted()
		except: result['currency']       = None

		try:    result['price_type_out'] = self.price_type_out.getDicted()
		except: result['price_type_out'] = None

		try:    result['currency_out']   = self.currency_out.getDicted()
		except: result['currency_out']   = None

		try:    result['unit']           = self.unit.getDicted()
		except: result['unit']           = None

		result['price_str']     = self._get_price_str()
		result['price_xml']     = self._get_price_xml()
		result['price_out_str'] = self._get_price_out_str()
		result['price_out_xml'] = self._get_price_out_xml()

		return result

	def _get_price_str(self):

		try:
			price = self.price
			currency = self.currency
		except: return ''

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', ' ')
			price = price.replace('.', ',')
			price = price + ' ' + currency.name
		else: return ''

		return price

	price_str = property(_get_price_str)

	def _get_price_xml(self):

		try:
			price = self.price
			currency = self.currency
		except: return ''

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', '&nbsp;')
			price = price.replace('.', ',')
			price = price + '&nbsp;' + currency.name
		else: return ''

		return price

	price_xml = property(_get_price_xml)

	def _get_price_out_str(self):
		try:
			price = self.price_out * self.currency_out.rate / self.currency_out.quantity
		except:
			try:
				price = self.price * self.price_type.multiplier * self.currency.rate / self.currency.quantity
			except: return ''

		currency = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  = 1)

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', '&nbsp;')
			price = price.replace('.', ',')
			price = price + '&nbsp;' + currency.name
		else: return ''

		return price

	price_out_str = property(_get_price_out_str)

	class Meta:
		ordering = ['-created']


class PartyHystory(models.Model):

	id             = models.CharField(max_length = 100, primary_key = True, default = uuid.uuid4, editable = False)
	product        = models.ForeignKey(Product)
	stock          = models.ForeignKey(Stock)
	price          = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None)
	price_type     = models.ForeignKey(PriceType, null = True, default = None)
	currency       = models.ForeignKey(Currency, null = True, default = None)
	price_out      = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None)
	price_type_out = models.ForeignKey(PriceType, related_name = 'party_hystory_requests_price_type_out', null = True, default = None)
	currency_out   = models.ForeignKey(Currency, related_name = 'party_hystory_requests_currency_out', null = True, default = None)
	quantity       = models.IntegerField(null = True, default = None)
	unit           = models.ForeignKey(Unit, null = True, default = None)
	comment        = models.TextField()
	date           = models.DateField()

	def getDicted(self):

		result = {}

		result['id']        = self.id
		result['article']   = self.article
		result['price']     = str(self.price)
		result['price_out'] = self.price_out
		result['quantity']  = self.description
		result['comment']   = self.comment
		result['date']      = str(self.date)

		try:    result['product']        = self.product.getDicted()
		except: result['product']        = None

		try:    result['stock']          = self.stock.getDicted()
		except: result['stock']          = None

		try:    result['price_type']     = self.price_type.getDicted()
		except: result['price_type']     = None

		try:    result['currency']       = self.currency.getDicted()
		except: result['currency']       = None

		try:    result['price_type_out'] = self.price_type_out.getDicted()
		except: result['price_type_out'] = None

		try:    result['currency_out']   = self.currency_out.getDicted()
		except: result['currency_out']   = None

		try:    result['unit']           = self.unit.getDicted()
		except: result['unit']           = None

		return result

	class Meta:
		ordering = ['-date']


class PriceHystory(models.Model):

	id         = models.CharField(max_length = 100, primary_key = True, default = uuid.uuid4, editable = False)
	product    = models.ForeignKey(Product)
	price      = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None)
	price_type = models.ForeignKey(PriceType, null = True, default = None)
	currency   = models.ForeignKey(Currency, null = True, default = None)
	date       = models.DateField()

	def getDicted(self):

		result = {}

		result['id']    = self.id
		result['price'] = str(self.price)
		result['date']  = str(self.date)

		try:    result['product']    = self.product.getDicted()
		except: result['product']    = None

		try:    result['price_type'] = self.price_type.getDicted()
		except: result['price_type'] = None

		try:    result['currency']   = self.currency.getDicted()
		except: result['currency']   = None

		return result

	class Meta:
		ordering = ['-date']


class QuantityHystory(models.Model):

	id         = models.CharField(max_length = 100, primary_key = True, default = uuid.uuid4, editable = False)
	product    = models.ForeignKey(Product)
	on_stock   = models.IntegerField(null = True, default = None)
	on_transit = models.IntegerField(null = True, default = None)
	on_factory = models.IntegerField(null = True, default = None)
	unit       = models.ForeignKey(Unit, null = True, default = None)
	date       = models.DateField()

	def getDicted(self):

		result = {}

		result['id']         = self.id
		result['on_stock']   = self.on_stock
		result['on_transit'] = self.on_transit
		result['on_factory'] = self.on_factory
		result['date']       = str(self.date)

		try:    result['product'] = self.product.getDicted()
		except: result['product'] = None

		try:    result['unit']    = self.unit.getDicted()
		except: result['unit']    = None

		return result

	class Meta:
		ordering = ['-date']


class ParameterTypeManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result


class ParameterType(models.Model):

	name      = models.CharField(max_length = 100, unique = True)
	alias     = models.CharField(max_length = 100, unique = True)
	order     = models.IntegerField(default = 0)
	state     = models.BooleanField(default = True)
	created   = models.DateTimeField()
	modified  = models.DateTimeField()

	objects   = ParameterTypeManager()

	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['alias']    = self.alias
		result['order']    = self.order
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		return result

	def __str__(self):
		return self.alias

	class Meta:
		ordering = ['name']


class ParameterManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result


class Parameter(models.Model):

	name           = models.CharField(max_length = 100, unique = True)
	alias          = models.CharField(max_length = 100, unique = True)
	parameter_type = models.ForeignKey(ParameterType, null = True, default = None)
	order          = models.IntegerField(default = 0)
	state          = models.BooleanField(default = True)
	created        = models.DateTimeField()
	modified       = models.DateTimeField()

	objects        = ParameterManager()

	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['alias']    = self.alias
		result['order']    = self.order
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:    result['parameter_type'] = self.parameter_type.getDicted()
		except: result['parameter_type'] = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['order', 'name']


class ParameterValueManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result


class ParameterValue(models.Model):

	parameter    = models.ForeignKey(Parameter)
	value_text   = models.CharField(max_length = 100)
	value_search = models.CharField(max_length = 100, null = True, default = None)
	order        = models.IntegerField()
	state        = models.BooleanField(default = True)
	created      = models.DateTimeField()
	modified     = models.DateTimeField()

	objects      = ParameterValueManager()

	def getDicted(self):

		result = {}

		result['id']           = self.id
		result['parameter']    = self.parameter
		result['value_text']   = self.value_text
		result['value_search'] = self.value_search
		result['order']        = self.order
		result['state']        = self.state
		result['created']      = str(self.created)
		result['modified']     = str(self.modified)

		try:    result['parameter'] = self.parameter.getDicted()
		except: result['parameter'] = None

		return result

	def __str__(self):
		return self.value

	class Meta:
		ordering = ['order', 'value_search']


class ParameterValueSynonymManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result


class ParameterValueSynonym(models.Model):

	name            = models.CharField(max_length = 1024)
	updater         = models.ForeignKey(Updater, null = True, default = None)
	distributor     = models.ForeignKey(Distributor, null = True, default = None)
	parameter       = models.ForeignKey(Parameter)
	parameter_value = models.ForeignKey(ParameterValue)
	created         = models.DateTimeField()
	modified        = models.DateTimeField()

	objects         = ParameterValueSynonymManager()

	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:    result['updater']         = self.updater.getDicted()
		except: result['updater']         = None

		try:    result['distributor']     = self.distributor.getDicted()
		except: result['distributor']     = None

		try:    result['parameter']       = self.parameter.getDicted()
		except: result['parameter']       = None

		try:    result['parameter_value'] = self.parameter_value.getDicted()
		except: result['parameter_value'] = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class ParameterToProductManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, parameter, product):

		try:
			parameter_to_product = self.get(
				parameter = parameter,
				product   = product)
		except ParameterToProduct.DoesNotExist:
			parameter_to_product = ParameterToProduct(
				parameter = parameter,
				product   = product,
				created   = timezone.now(),
				modified  = timezone.now())
			parameter_to_product.save()

		return parameter_to_product


class ParameterToProduct(models.Model):

	id            = models.CharField(max_length = 100, primary_key = True, default = uuid.uuid4, editable = False)
	parameter     = models.ForeignKey(Parameter)
	product       = models.ForeignKey(Product)
	value_text    = models.TextField()
	value_search  = models.CharField(max_length = 100, null = True, default = None)
	value_integer = models.IntegerField(null = True, default = None)
	value_decimal = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None)
	value_list    = models.ForeignKey(ParameterValue, null = True, default = None)
	state         = models.BooleanField(default = True)
	created       = models.DateTimeField()
	modified      = models.DateTimeField()

	objects       = ParameterToProductManager()

	def getDicted(self):

		result = {}

		result['id']            = self.id
		result['value_text']    = self.value_text
		result['value_search']  = self.value_search
		result['value_integer'] = self.value_integer
		result['value_decimal'] = str(self.value_decimal)
		result['state']         = self.state
		result['created']       = str(self.created)
		result['modified']      = str(self.modified)

		try:    result['parameter']       = self.parameter.getDicted()
		except: result['parameter']       = None

		try:    result['product']         = self.product.getDicted()
		except: result['product']         = None

		try:    result['value_list']      = self.value_list.getDicted()
		except: result['value_list']      = None

		try:    result['parameter_value'] = self.parameter_value.getDicted()
		except: result['parameter_value'] = None

		return result

	def __str__(self):
		return '{} - {} {}'.format(
			self.parameter.name,
			Self.product.vendor.name,
			self.product.arvicle)

	class Meta:
		ordering = ['created']
		db_table = 'catalog_parameter_to_product'


	def setValue(self, value):

		print('setValue')

		if 'text' == self.parameter.parameter_type.alias:

			print('text')

			self.value_text   = value
			self.value_search = value[:100]
			self.save()

			print("{} = {}".format(self.parameter.name, self.value_search))

		elif 'months' == self.parameter.parameter_type.alias:

			print('months')

			if 'Y' in value:                                                    # Входные данные в годах
				value = int(value.replace('Y', '').strip())*12
				self.value_text    = "{} месяцев".format(value)
				self.value_search  = self.value_text[:100]
				self.value_integer = value
				self.save()
			else:
				print('Что делать со значением [{}]?'.format(value))

			print("{} = {}".format(self.parameter.name, self.value_search))

		elif 'list' == self.parameter.parameter_type.alias:

			print('list')

			# TODO
			# TODO
			# TODO
			# TODO
			# TODO
			# TODO
			# TODO
			# TODO
			# TODO


class ParameterToCategory(models.Model):

	id        = models.CharField(max_length = 100, primary_key = True, default = uuid.uuid4, editable = False)
	parameter = models.ForeignKey(Parameter)
	category  = models.ForeignKey(Category)
	order     = models.IntegerField()
	state     = models.BooleanField(default = True)
	created   = models.DateTimeField()
	modified  = models.DateTimeField()

	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['order']    = self.order
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:    result['parameter']       = self.parameter.getDicted()
		except: result['parameter']       = None

		try:    result['category']        = self.category.getDicted()
		except: result['category']        = None

		try:    result['value_list']      = self.value_list.getDicted()
		except: result['value_list']      = None

		try:    result['parameter_value'] = self.parameter_value.getDicted()
		except: result['parameter_value'] = None

		return result

	class Meta:
		ordering = ['created']
		db_table = 'catalog_parameter_to_category'


class ParameterSynonymManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, name, updater = None, distributor = None, parameter = None):
		name = name.strip()
		try:
			parameter_synonym = self.get(
				name        = name,
				updater     = updater,
				distributor = distributor)
		except ParameterSynonym.DoesNotExist:
			parameter_synonym = ParameterSynonym(
				name        = name,
				updater     = updater,
				distributor = distributor,
				parameter   = parameter,
				created     = timezone.now(),
				modified    = timezone.now())
			parameter_synonym.save()
		return parameter_synonym


class ParameterSynonym(models.Model):

	name        = models.CharField(max_length = 1024)
	updater     = models.ForeignKey(Updater, null = True, default = None)
	distributor = models.ForeignKey(Distributor, null = True, default = None)
	parameter   = models.ForeignKey(Parameter, null = True, default = None)
	created     = models.DateTimeField()
	modified    = models.DateTimeField()

	objects     = ParameterSynonymManager()

	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:    result['updater']     = self.updater.getDicted()
		except: result['updater']     = None

		try:    result['distributor'] = self.distributor.getDicted()
		except: result['distributor'] = None

		try:    result['parameter']   = self.parameter.getDicted()
		except: result['parameter']   = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class CategorySynonymManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, name, updater = None, distributor = None, category = None):
		name = name.strip()
		try:
			categorySynonym = self.get(
				name        = name,
				updater     = updater,
				distributor = distributor)
		except CategorySynonym.DoesNotExist:
			categorySynonym = CategorySynonym(
				name        = name,
				updater     = updater,
				distributor = distributor,
				category    = category,
				created     = timezone.now(),
				modified    = timezone.now())
			categorySynonym.save()
		return categorySynonym


class CategorySynonym(models.Model):

	name        = models.CharField(max_length = 1024)
	updater     = models.ForeignKey(Updater, null = True, default = None)
	distributor = models.ForeignKey(Distributor, null = True, default = None)
	category    = models.ForeignKey(Category, null = True, default = None)
	created     = models.DateTimeField()
	modified    = models.DateTimeField()

	objects     = CategorySynonymManager()

	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:    result['updater']     = self.updater.getDicted()
		except: result['updater']     = None

		try:    result['distributor'] = self.distributor.getDicted()
		except: result['distributor'] = None

		try:    result['category']    = self.category.getDicted()
		except: result['category']    = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class VendorSynonymManager(models.Manager):

	def getAllDicted(self):
		result = []
		for o in self.all():
			result.append(o.getDicted)
		return result

	def take(self, name, updater = None, distributor = None, vendor = None):
		name = name.strip()
		try:
			vendorSynonym = self.get(
				name        = name,
				updater     = updater,
				distributor = distributor)
		except VendorSynonym.DoesNotExist:
			vendorSynonym = VendorSynonym(
				name        = name,
				updater     = updater,
				distributor = distributor,
				vendor      = vendor,
				created     = timezone.now(),
				modified    = timezone.now())
			vendorSynonym.save()
		return vendorSynonym


class VendorSynonym(models.Model):

	name        = models.CharField(max_length = 1024)
	updater     = models.ForeignKey(Updater, null = True, default = None)
	distributor = models.ForeignKey(Distributor, null = True, default = None)
	vendor      = models.ForeignKey(Vendor, null = True, default = None)
	created     = models.DateTimeField()
	modified    = models.DateTimeField()

	objects     = VendorSynonymManager()

	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:    result['updater']     = self.updater.getDicted()
		except: result['updater']     = None

		try:    result['distributor'] = self.distributor.getDicted()
		except: result['distributor'] = None

		try:    result['vendor']      = self.vendor.getDicted()
		except: result['vendor']      = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class UpdaterTask(models.Model):

	id       = models.CharField(max_length = 100, primary_key = True, default = uuid.uuid4, editable = False)
	name     = models.CharField(max_length = 1024)
	updater  = models.ForeignKey(Updater, null = True, default = None)
	subject  = models.CharField(max_length = 1024)
	created  = models.DateTimeField()
	modified = models.DateTimeField()
	complite = models.BooleanField(default = False)

	def getDicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['subject']  = self.subject
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)
		result['complite'] = self.complite

		try:    result['updater'] = self.updater.getDicted()
		except: result['updater'] = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['created']




models = {
	'connector'             : Connector,
	'distributor'           : Distributor,
	'updater'               : Updater,
	'stock'                 : Stock,
	'category'              : Category,
	'vendor'                : Vendor,
	'unit'                  : Unit,
	'pricetype'             : PriceType,
	'currency'              : Currency,
	'price'                 : Price,
	'quantity'              : Quantity,
	'product'               : Product,
	'party'                 : Party,
	'partyhystory'          : PartyHystory,
	'pricehystory'          : PriceHystory,
	'quantityhystory'       : QuantityHystory,
	'parametertype'         : ParameterType,
	'parameter'             : Parameter,
	'parametervalue'        : ParameterValue,
	'parametervaluesynonym' : ParameterValueSynonym,
	'parametertoproduct'    : ParameterToProduct,
	'parametertocategory'   : ParameterToCategory,
	'parametersynonym'      : ParameterSynonym,
	'catagorysynonym'       : CategorySynonym,
	'vendorsynonym'         : VendorSynonym,
	'updatertask'           : UpdaterTask}
