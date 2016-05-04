import uuid
from django.db import models
from django.utils import timezone


class DistributorManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, *args, **kwargs):

		alias = str(kwargs.get('alias', '')).strip()
		name  = str(kwargs.get('name', '')).strip()

		if not alias:
			return None

		try:
			result = self.get(alias = alias)

		except Distributor.DoesNotExist:

			if not name:
				return None

			result = Distributor(
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
	state       = models.BooleanField(default = True)
	created     = models.DateTimeField()
	modified    = models.DateTimeField()

	objects     = DistributorManager()


	def get_dicted(self):

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


class UpdaterManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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


	def get_dicted(self):

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

		try:
			result['distributor'] = self.distributor.get_dicted()
		except Exception:
			result['distributor'] = None

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class StockManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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


	def get_dicted(self):

		result = {}

		result['id']                = self.id
		result['name']              = self.name
		result['alias']             = self.alias
		result['delivery_time_min'] = self.delivery_time_min
		result['delivery_time_max'] = self.delivery_time_max
		result['state']             = self.state
		result['created']           = str(self.created)
		result['modified']          = str(self.modified)

		try:
			result['distributor'] = self.distributor.get_dicted()
		except Exception:
			result['distributor'] = None

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class CategoryManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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


	def get_dicted(self):

		result = {}

		result['id']           = self.id
		result['name']         = self.name
		result['name_search']  = self.name_search
		result['name_leveled'] = '— ' * self.level + self.name
		result['alias']        = self.alias
		result['description']  = self.description
		result['level']        = self.level
		result['order']        = self.order
		result['path']         = self.path
		result['state']        = self.state
		result['created']      = str(self.created)
		result['modified']     = str(self.modified)

		try:
			result['parent'] = self.parent.get_dicted()
		except Exception:
			result['parent'] = None

		return result


	def __str__(self):
		return self.name_search


	class Meta:
		ordering = ['order']


class VendorManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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


	def get_dicted(self):

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


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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

	name           = models.CharField(max_length = 100)
	name_short     = models.CharField(max_length = 100, null = True, default = None)
	name_short_xml = models.CharField(max_length = 100, null = True, default = None)
	alias          = models.CharField(max_length = 100, unique = True)
	state          = models.BooleanField(default = True)
	created        = models.DateTimeField()
	modified       = models.DateTimeField()

	objects  = UnitManager()


	def get_dicted(self):

		result = {}

		result['id']             = self.id
		result['name']           = self.name
		result['name_short']     = self.name_short
		result['name_short_xml'] = self.name_short_xml
		result['alias']          = self.alias
		result['state']          = self.state
		result['created']        = str(self.created)
		result['modified']       = str(self.modified)

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class PriceTypeManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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


	def get_dicted(self):

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


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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


	def get_dicted(self):

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


	def get_dicted(self):

		result = {}

		result['id']       = self.id
		result['price']    = str(self.price)
		result['fixed']    = self.fixed
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['price_type'] = self.price_type.get_dicted()
		except Exception:
			result['price_type'] = None

		try:
			result['currency'] = self.currency.get_dicted()
		except Exception:
			result['currency'] = None

		result['price_str'] = self._get_price_str()
		result['price_xml'] = self._get_price_xml()

		return result


	def _get_price_str(self):

		try:
			price    = self.price
			currency = self.currency
		except Exception:
			return ''

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', ' ')
			price = price.replace('.', ',')
			price = price + ' ' + currency.name
		else:
			return ''

		return price

	price_str = property(_get_price_str)


	def _get_price_xml(self):

		try:
			price    = self.price
			currency = self.currency
		except:
			return ''

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', '&nbsp;')
			price = price.replace('.', ',')
			price = price + '&nbsp;' + currency.name
		else:
			return '<i class="fa fa-phone"></i>'

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


	def get_dicted(self):

		result = {}

		result['id']         = self.id
		result['on_stock']   = self.on_stock
		result['on_transit'] = self.on_transit
		result['on_factory'] = self.on_factory
		result['fixed']      = self.fixed
		result['state']      = self.state
		result['created']    = str(self.created)
		result['modified']   = str(self.modified)

		try:
			result['unit'] = self.unit.get_dicted()
		except Exception:
			result['unit'] = None

		return result


	def _get_on_stock_xml(self):

		try:

			if self.on_stock == -1:
				quantity = '&infin;'
			elif self.on_stock:
				quantity = str(self.on_stock)
			elif self.on_stock is None:
				quantity = '?'
			else:
				quantity = ''
		except:
			quantity = ''

		return quantity


	def _get_on_transit_xml(self):

		try:

			if self.on_transit == -1:
				quantity = '&infin;'
			elif self.on_transit:
				quantity = str(self.on_transit)
			elif self.on_transit is None:
				quantity = '?'
			else:
				quantity = ''
				
		except Exception:
			quantity = ''

		return quantity


	def _get_on_factory_xml(self):

		try:

			if self.on_factory == -1:
				quantity = '&infin;'
			elif self.on_factory:
				quantity = str(self.on_factory)
			elif self.on_factory is None:
				quantity = '?'
			else:
				quantity = ''
		except Exception:
			quantity = ''

		return quantity


	on_stock_xml   = property(_get_on_stock_xml)
	on_transit_xml = property(_get_on_transit_xml)
	on_factory_xml = property(_get_on_factory_xml)


	class Meta:
		ordering = ['-created']


class ProductManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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


	def get_dicted(self):

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

		try:    result['vendor']   = self.vendor.get_dicted()
		except: result['vendor']   = None

		try:    result['category'] = self.category.get_dicted()
		except: result['category'] = None

		try:    result['unit']     = self.unit.get_dicted()
		except: result['unit']     = None

		try:    result['duble']    = self.duble.get_dicted()
		except: result['duble']    = None

		try:    result['price']    = self.price.get_dicted()
		except: result['price']    = None

		try:    result['quantity'] = self.quantity.get_dicted()
		except: result['quantity'] = None

		return result


	def __str__(self):
		return self.name


	# TODO Need rafactoring
	def recalculate(self):

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

		# Получаем объекты количества и цены
		if self.quantity is None:
			self.quantity = Quantity()
			self.quantity.created = timezone.now()
			self.quantity.modified = timezone.now()
			self.quantity.save()
			self.save()

		if self.price is None:
			self.price = Price()
			self.price.created = timezone.now()
			self.price.modified = timezone.now()
			self.price.save()
			self.save()

		# Вычисляем количество товара
		quantities = {
			'stock'   : [0],
			'transit' : [0],
			'factory' : [0]}

		undef = {
			'stock'   : None,
			'transit' : None,
			'factory' : None}

		prices = []
		prices_null = []

		# Проходим по всем партиям продукта
		for party in Party.objects.filter(product = self):

			if party.quantity:

				if 'stock' in party.stock.alias:
					quantities['stock'].append(party.quantity)
					undef['stock'] = False
				elif 'transit' in party.stock.alias:
					quantities['transit'].append(party.quantity)
					undef['transit'] = False
				elif 'factory' in party.stock.alias \
						or 'delivery' in party.stock.alias \
						or 'order' in party.stock.alias:
					quantities['factory'].append(party.quantity)
					undef['factory'] = False

			elif party.quantity is None:

				if 'stock' in party.stock.alias and undef['stock'] is None:
					undef['stock'] = True
				elif 'transit' in party.stock.alias and undef['transit'] is None:
					undef['transit'] = True
				elif ('factory' in party.stock.alias \
						or 'delivery' in party.stock.alias \
						or 'order' in party.stock.alias) \
						and undef['transit'] is None:
					undef['factory'] = True

			if party.quantity != 0:

				if party.price and party.currency and party.price_type:
					prices.append(party.price * party.currency.rate * party.price_type.multiplier / party.currency.quantity)

			else:

				if party.price and party.currency and party.price_type:
					prices_null.append(party.price * party.currency.rate * party.price_type.multiplier / party.currency.quantity)

		# Записываем информацию в базу
		if -1 in quantities['stock']:
			self.quantity.on_stock = -1
		elif undef['stock']:
			self.quantity.on_stock = None
		else:
			self.quantity.on_stock = sum(quantities['stock'])

		if -1 in quantities['transit']:
			self.quantity.on_transit = -1
		elif undef['transit']:
			self.quantity.on_transit = None
		else:
			self.quantity.on_transit = sum(quantities['transit'])

		if -1 in quantities['factory']:
			self.quantity.on_factory = -1
		elif undef['factory']:
			self.quantity.on_factory = None
		else:
			self.quantity.on_factory = sum(quantities['factory'])

		self.quantity.modified = timezone.now()
		self.quantity.save()

		if len(prices):
			self.price.price      = min(prices)
			self.price.price_type = rp
			self.price.currency   = rub
		elif len(prices_null):
			self.price.price      = min(prices_null)
			self.price.price_type = rp
			self.price.currency   = rub
		else:
			self.price.price      = None
			self.price.price_type = rp
			self.price.currency   = rub

		self.price.modified = timezone.now()
		self.price.save()


	def get_parameter_to_product(self, parameter_alias):

		try:
			parameter = Parameter.objects.get(alias = parameter_alias)
		except Exception:
			return None

		try:
			parameter_to_product = ParameterToProduct.objects.get(
				product = self,
				parameter = parameter)
		except Exception:
			parameter_to_product = ParameterToProduct(
				product   = self,
				parameter = parameter,
				created   = timezone.now(),
				modified  = timezone.now())
			parameter_to_product.save()

		return parameter_to_product


	class Meta:
		ordering = ['name']


class PartyManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def make(self, product, stock, article = None,
			price = None, price_type = None, currency = None,
			price_out = None, price_type_out = None, currency_out = None,
			quantity = None, unit = None, product_name = '', time = None):

		if time:
			Party.objects.filter(product = product, stock = stock, created__lt = time).delete()

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
			product_name   = product_name,
			created        = timezone.now(),
			modified       = timezone.now())
		party.save()

		print('{} {} = {}; {} on {}'.format(
			party.product.vendor.name,
			party.product.article,
			party.price_str,
			party.quantity,
			party.stock.alias))

		party.product.recalculate()

		return party


	def clear(self, stock, time = None):
		if time:
			Party.objects.filter(stock = stock, created__lt = time).delete()
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
	product_name   = models.TextField()
	state          = models.BooleanField(default = True)
	created        = models.DateTimeField()
	modified       = models.DateTimeField()

	objects        = PartyManager()


	def get_dicted(self):

		result = {}

		result['id']           = self.id
		result['article']      = self.article
		result['price']        = str(self.price)
		result['price_out']    = self.price_out
		result['quantity']     = self.description
		result['comment']      = self.comment
		result['product_name'] = self.comment
		result['state']        = self.state
		result['created']      = str(self.created)
		result['modified']     = str(self.modified)

		try:
			result['product'] = self.product.get_dicted()
		except Exception:
			result['product'] = None

		try:
			result['stock'] = self.stock.get_dicted()
		except Exception:
			result['stock'] = None

		try:
			result['price_type'] = self.price_type.get_dicted()
		except Exception:
			result['price_type'] = None

		try:
			result['currency'] = self.currency.get_dicted()
		except Exception:
			result['currency'] = None

		try:
			result['price_type_out'] = self.price_type_out.get_dicted()
		except Exception:
			result['price_type_out'] = None

		try:
			result['currency_out'] = self.currency_out.get_dicted()
		except Exception:
			result['currency_out'] = None

		try:
			result['unit'] = self.unit.get_dicted()
		except Exception:
			result['unit'] = None

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


	def get_dicted(self):

		result = {}

		result['id']        = self.id
		result['article']   = self.article
		result['price']     = str(self.price)
		result['price_out'] = self.price_out
		result['quantity']  = self.description
		result['comment']   = self.comment
		result['date']      = str(self.date)

		try:    result['product']        = self.product.get_dicted()
		except: result['product']        = None

		try:    result['stock']          = self.stock.get_dicted()
		except: result['stock']          = None

		try:    result['price_type']     = self.price_type.get_dicted()
		except: result['price_type']     = None

		try:    result['currency']       = self.currency.get_dicted()
		except: result['currency']       = None

		try:    result['price_type_out'] = self.price_type_out.get_dicted()
		except: result['price_type_out'] = None

		try:    result['currency_out']   = self.currency_out.get_dicted()
		except: result['currency_out']   = None

		try:    result['unit']           = self.unit.get_dicted()
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


	def get_dicted(self):

		result = {}

		result['id']    = self.id
		result['price'] = str(self.price)
		result['date']  = str(self.date)

		try:    result['product']    = self.product.get_dicted()
		except: result['product']    = None

		try:    result['price_type'] = self.price_type.get_dicted()
		except: result['price_type'] = None

		try:    result['currency']   = self.currency.get_dicted()
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


	def get_dicted(self):

		result = {}

		result['id']         = self.id
		result['on_stock']   = self.on_stock
		result['on_transit'] = self.on_transit
		result['on_factory'] = self.on_factory
		result['date']       = str(self.date)

		try:    result['product'] = self.product.get_dicted()
		except: result['product'] = None

		try:    result['unit']    = self.unit.get_dicted()
		except: result['unit']    = None

		return result

	class Meta:
		ordering = ['-date']


class ParameterTypeManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


class ParameterType(models.Model):

	name      = models.CharField(max_length = 100, unique = True)
	alias     = models.CharField(max_length = 100, unique = True)
	order     = models.IntegerField(default = 0)
	state     = models.BooleanField(default = True)
	created   = models.DateTimeField()
	modified  = models.DateTimeField()

	objects   = ParameterTypeManager()

	def get_dicted(self):

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

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


class Parameter(models.Model):

	name          = models.CharField(max_length = 100, unique = True)
	alias         = models.CharField(max_length = 100, unique = True)
	parametertype = models.ForeignKey(ParameterType, null = True, default = None)
	unit          = models.ForeignKey(Unit, null = True, default = None)
	order         = models.IntegerField(default = 0)
	state         = models.BooleanField(default = True)
	created       = models.DateTimeField()
	modified      = models.DateTimeField()

	objects        = ParameterManager()

	def get_dicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['alias']    = self.alias
		result['order']    = self.order
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['parametertype'] = self.parametertype.get_dicted()
		except Exception:
			result['parametertype'] = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['order', 'name']


class ParameterValueManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


class ParameterValue(models.Model):

	parameter    = models.ForeignKey(Parameter)
	value_text   = models.TextField()
	value_search = models.CharField(max_length = 100, null = True, default = None)
	order        = models.IntegerField()
	state        = models.BooleanField(default = True)
	created      = models.DateTimeField()
	modified     = models.DateTimeField()

	objects      = ParameterValueManager()

	def get_dicted(self):

		result = {}

		result['id']           = self.id
		result['parameter']    = self.parameter
		result['value_text']   = self.value_text
		result['value_search'] = self.value_search
		result['order']        = self.order
		result['state']        = self.state
		result['created']      = str(self.created)
		result['modified']     = str(self.modified)

		try:    result['parameter'] = self.parameter.get_dicted()
		except: result['parameter'] = None

		return result

	def __str__(self):
		return self.value

	class Meta:
		ordering = ['order', 'value_search']


class ParameterValueSynonymManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, name, updater = None, distributor = None, parameter = None):

		name = name.strip()

		try:
			value_synonym = self.get(
				name        = name,
				updater     = updater,
				distributor = distributor)
		except ParameterValueSynonym.DoesNotExist:
			value_synonym = ParameterValueSynonym(
				name        = name,
				updater     = updater,
				distributor = distributor,
				parameter   = parameter,
				created     = timezone.now(),
				modified    = timezone.now())
			value_synonym.save()

		return value_synonym


class ParameterValueSynonym(models.Model):

	name           = models.CharField(max_length = 1024)
	updater        = models.ForeignKey(Updater, null = True, default = None)
	distributor    = models.ForeignKey(Distributor, null = True, default = None)
	parameter      = models.ForeignKey(Parameter, null = True, default = None)
	parametervalue = models.ForeignKey(ParameterValue, null = True, default = None)
	created        = models.DateTimeField()
	modified       = models.DateTimeField()

	objects        = ParameterValueSynonymManager()

	def get_dicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:    result['updater']         = self.updater.get_dicted()
		except: result['updater']         = None

		try:    result['distributor']     = self.distributor.get_dicted()
		except: result['distributor']     = None

		try:    result['parameter']       = self.parameter.get_dicted()
		except: result['parameter']       = None

		try:    result['parameter_value'] = self.parameter_value.get_dicted()
		except: result['parameter_value'] = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class ParameterToProductManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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

	def get_dicted(self):

		result = {}

		result['id']            = self.id
		result['value_text']    = self.value_text
		result['value_search']  = self.value_search
		result['value_integer'] = self.value_integer
		result['value_decimal'] = str(self.value_decimal)
		result['state']         = self.state
		result['created']       = str(self.created)
		result['modified']      = str(self.modified)

		try:    result['parameter']       = self.parameter.get_dicted()
		except: result['parameter']       = None

		try:    result['product']         = self.product.get_dicted()
		except: result['product']         = None

		try:    result['value_list']      = self.value_list.get_dicted()
		except: result['value_list']      = None

		try:    result['parameter_value'] = self.parameter_value.get_dicted()
		except: result['parameter_value'] = None

		return result


	def __str__(self):

		return '{} {} - {}'.format(
			self.product.vendor.name,
			self.product.article,
			self.parameter.name)


	def set_value(self, value, updater = None, distributor = None):

		print('set_value: {}'.format(value))

		if self.parameter.parametertype is None:

			print('self.parameter.parametertype is None')

			return False

		if self.parameter.parametertype.alias == 'text':

			print('self.parameter.parametertype.alias == "text"')

			self.value_text   = value.strip()
			self.value_search = self.value_text[:100]
			self.save()

		elif self.parameter.parametertype.alias == 'months':

			if str(type(value)) in ("<class 'str'>", "<class 'int'>"):

				value = str(value)

				x = 1
				r = 1

				if 'год' in value or 'лет' in value or 'Y' in value:
					x = 12
					value = value.replace('Y', '')
				elif 'дней' in value:
					r = 30

				try:
					self.value_integer = int(value.strip().split(' ')[0]) * x // r
					self.save()
				except Exception:
					print('Не смог обработать значение: {}.'.format(value))
					return False

		elif self.parameter.parametertype.alias == 'list':

			print('self.parameter.parametertype.alias == "list"')

			value_synonym = ParameterValueSynonym.objects.take(
				name        = value,
				updater     = updater,
				distributor = distributor,
				parameter   = self.parameter)

			if value_synonym.parametervalue:
				self.value_list = value_synonym.parametervalue
			else:
				print('Значение не проверено: {}.'.format(value))

		else:

			print('Неизвестный тип данных!!!')
			print('Ошибка! {} = {}'.format(self, value))
			return False

		print("{} = {}".format(self, self.parameter_value_xml))


	def _get_parameter_name_xml(self):

		return self.parameter.name

	parameter_name_xml = property(_get_parameter_name_xml)


	def _get_parameter_value_xml(self):

		if self.value_text:
			value = self.value_text
		elif self.value_integer:
			value = '{:,}'.format(self.value_integer).replace(',', ' ')
		elif self.value_decimal:
			value = '{:,}'.format(self.value_decimal).replace(',', ' ').replace('.', ',')
		elif self.value_list:
			value = self.value_list.value_text
		else:
			return ''

		if self.parameter.unit:
			value = '{} {}'.format(value, self.parameter.unit.name_short_xml)

		return value

	parameter_value_xml = property(_get_parameter_value_xml)


	class Meta:
		ordering = ['created']
		db_table = 'catalog_parameter_to_product'



class ParameterToCategory(models.Model):

	id        = models.CharField(max_length = 100, primary_key = True, default = uuid.uuid4, editable = False)
	parameter = models.ForeignKey(Parameter)
	category  = models.ForeignKey(Category)
	order     = models.IntegerField()
	state     = models.BooleanField(default = True)
	created   = models.DateTimeField()
	modified  = models.DateTimeField()

	def get_dicted(self):

		result = {}

		result['id']       = self.id
		result['order']    = self.order
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:    result['parameter']       = self.parameter.get_dicted()
		except: result['parameter']       = None

		try:    result['category']        = self.category.get_dicted()
		except: result['category']        = None

		try:    result['value_list']      = self.value_list.get_dicted()
		except: result['value_list']      = None

		try:    result['parameter_value'] = self.parameter_value.get_dicted()
		except: result['parameter_value'] = None

		return result

	class Meta:
		ordering = ['created']
		db_table = 'catalog_parameter_to_category'


class ParameterSynonymManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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

	def get_dicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['updater'] = self.updater.get_dicted()
		except Exception:
			result['updater']     = None

		try:
			result['distributor'] = self.distributor.get_dicted()
		except Exception:
			result['distributor'] = None

		try:
			result['parameter'] = self.parameter.get_dicted()
		except Exception:
			result['parameter'] = None

		return result


	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class CategorySynonymManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
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

	def get_dicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['updater'] = self.updater.get_dicted()
		except Exception:
			result['updater']     = None

		try:
			result['distributor'] = self.distributor.get_dicted()
		except Exception:
			result['distributor'] = None

		try:
			result['category'] = self.category.get_dicted()
		except Exception:
			result['category'] = None

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class VendorSynonymManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, name, updater = None, distributor = None, vendor = None):
		name = str(name).strip()
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


	def get_dicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['updater'] = self.updater.get_dicted()
		except Exception:
			result['updater'] = None

		try:
			result['distributor'] = self.distributor.get_dicted()
		except Exception:
			result['distributor'] = None

		try:
			result['vendor'] = self.vendor.get_dicted()
		except Exception:
			result['vendor'] = None

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class UpdaterTaskManager(models.Manager):


	def take(self, name, subject, updater = None, complite = False):

		name    = str(name).strip()
		subject = str(subject).strip()

		try:
			task = self.get(
				name    = name,
				subject = subject,
				updater = updater)

		except UpdaterTask.DoesNotExist:
			task = UpdaterTask(
				name     = name,
				subject  = subject,
				updater  = updater,
				complite = complite,
				created  = timezone.now(),
				modified = timezone.now())
			task.save()

		return task


class UpdaterTask(models.Model):

	id       = models.CharField(max_length = 100, primary_key = True, default = uuid.uuid4, editable = False)
	name     = models.CharField(max_length = 1024)
	subject  = models.CharField(max_length = 1024)
	updater  = models.ForeignKey(Updater, null = True, default = None)
	created  = models.DateTimeField()
	modified = models.DateTimeField()
	complite = models.BooleanField(default = False)

	objects     = UpdaterTaskManager()


	def get_dicted(self):

		result = {}

		result['id']       = self.id
		result['name']     = self.name
		result['subject']  = self.subject
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)
		result['complite'] = self.complite

		try:
			result['updater'] = self.updater.get_dicted()
		except Exception:
			result['updater'] = None

		return result


	def __str__(self):
		return "{} {}: {}".format(self.updater, self.name, self.subject)


	class Meta:
		ordering = ['created']


models = {
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
	'categorysynonym'       : CategorySynonym,
	'vendorsynonym'         : VendorSynonym,
	'updatertask'           : UpdaterTask}
