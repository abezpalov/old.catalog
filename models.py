import uuid
from django.db import models

# Connector
class Connector(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100, unique=True)
	login = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Distributor manager
class DistributorManager(models.Manager):

	def take(self, alias, name):
		from datetime import datetime
		try:
			distributor = self.get(alias=alias)
		except Distributor.DoesNotExist:
			distributor = Distributor(alias=alias, name=name, created=datetime.now(), modified=datetime.now())
			distributor.save()
		return distributor

# Distributor
class Distributor(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100, unique=True)
	description = models.TextField()
	connector = models.ForeignKey(Connector, null=True, default=None)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = DistributorManager()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Updater manager
class UpdaterManager(models.Manager):

	def take(self, alias, name, distributor=None):
		from datetime import datetime
		try:
			updater = self.get(alias=alias)
		except Updater.DoesNotExist:
			updater = Updater(alias=alias, name=name, distributor=distributor, created=datetime.now(), modified=datetime.now(), updated=datetime.now())
			updater.save()
		return updater

# Updater
class Updater(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100, unique=True)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	login = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	updated = models.DateTimeField()
	objects = UpdaterManager()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Stock manager
class StockManager(models.Manager):

	def take(self, alias, name, delivery_time_min = 10, delivery_time_max = 20, distributor=None):
		from datetime import datetime
		try:
			stock = self.get(alias=alias)
		except Stock.DoesNotExist:
			stock = Stock(alias=alias, name=name, delivery_time_min = 10, delivery_time_max = 20, distributor=distributor, created=datetime.now(), modified=datetime.now())
			stock.save()
		return stock

# Stock
class Stock(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100, unique=True)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	delivery_time_min = models.IntegerField()
	delivery_time_max = models.IntegerField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = StockManager()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Category
class Category(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	description = models.TextField()
	parent = models.ForeignKey('self', null=True, default=None)
	level = models.IntegerField()
	order = models.IntegerField()
	path = models.CharField(max_length=100)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['order']

# Vendor manager
class VendorManager(models.Manager):

	def take(self, alias, name):
		from datetime import datetime
		try:
			vendor = self.get(alias=alias)
		except Vendor.DoesNotExist:
			vendor = Vendor(alias=alias, name=name, created=datetime.now(), modified=datetime.now())
			vendor.save()
		return vendor

# Vendor
class Vendor(models.Model):
	name = models.CharField(max_length=100, unique=True)
	alias = models.CharField(max_length=100, unique=True)
	description = models.TextField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = VendorManager()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Unit manager
class UnitManager(models.Manager):

	def take(self, alias, name):
		from datetime import datetime
		try:
			unit = self.get(alias=alias)
		except Unit.DoesNotExist:
			unit = Unit(alias=alias, name=name, created=datetime.now(), modified=datetime.now())
			unit.save()
		return unit

# Unit
class Unit(models.Model):
	name = models.CharField(max_length=100, unique=True)
	alias = models.CharField(max_length=100, unique=True)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = UnitManager()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Price Type manager
class PriceTypeManager(models.Manager):

	def take(self, alias, name):
		from datetime import datetime
		try:
			price_type = self.get(alias=alias)
		except PriceType.DoesNotExist:
			price_type = PriceType(alias=alias, name=name, created=datetime.now(), modified=datetime.now())
			price_type.save()
		return price_type

# Price Type
class PriceType(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100, unique=True)
	state = models.BooleanField(default=True)
	multiplier = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = PriceTypeManager()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Currency manager
class CurrencyManager(models.Manager):

	def take(self, alias, name, full_name, rate=1, quantity=1):
		from datetime import datetime
		try:
			currency = self.get(alias=alias)
		except Currency.DoesNotExist:
			currency = Currency(alias=alias, name=name, full_name=full_name, rate=rate, quantity=quantity, created=datetime.now(), modified=datetime.now())
			currency.save()
		return currency

# Currency
class Currency(models.Model):
	name = models.CharField(max_length=100)
	full_name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100, unique=True)
	rate = models.DecimalField(max_digits=10, decimal_places=4)
	quantity = models.DecimalField(max_digits=10, decimal_places=3)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = CurrencyManager()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Price manager
class PriceManager(models.Manager):

	def recalculate(self):

		from datetime import datetime
		from catalog.models import Currency
		from catalog.models import Product
		from catalog.models import Party
		from catalog.models import PriceType

		rp = PriceType.objects.take(alias='RP', name='Розничная цена')
		rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)


		# Получаем перечень всех продуктов
		products = Product.objects.all()

		for product in products:

			# Получаем партии продукта
			parties = Party.objects.filter(product=product)

			# Получаем цену
			if product.price:
				price = product.price
			else:
				price = Price()
				price.created = datetime.now()

			# Вычисляем розничные цены на основании входных цен
			prices = []
			for party in parties:
				if party.price and party.currency and party.price_type:
					prices.append(party.price * party.currency.rate / party.currency.quantity * party.price_type.multiplier)

			# Записываем лучшую в базу
			if len(prices):
				price.price = min(prices)
				price.price_type = rp
				price.currency = rub
			else:
				price.price = None
				price.price_type = None
				price.currency = None
			price.modified = datetime.now()
			price.save()

			# Если цена не привязана к продукту, привязываем
			if product.price is None:
				product.price = price
				product.save()

		return True

# Price
class Price(models.Model):
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=None)
	price_type = models.ForeignKey(PriceType, null=True, default=None)
	currency = models.ForeignKey(Currency, null=True, default=None)
	fixed = models.BooleanField(default=False)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = PriceManager()

	class Meta:
		ordering = ['-created']

# Quantity
class Quantity(models.Model):
	quantity = models.IntegerField(null=True, default=None)
	unit = models.ForeignKey(Unit, null=True, default=None)
	fixed = models.BooleanField(default=False)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

	class Meta:
		ordering = ['-created']

# Product manager
class ProductManager(models.Manager):

	def take(self, article, vendor, name, category = None, unit = None):

		from datetime import datetime

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
			product = self.get(article=article, vendor=vendor)
			if not product.category and category:
				product.category = category
				product.modified = datetime.now()
				product.save()
		except Product.DoesNotExist:
			product = Product(name=name[:500], full_name = name, article=article, vendor=vendor, category=category, unit=unit, created = datetime.now(), modified = datetime.now())
			product.save()

		return product

	def fixNames(self):
		from datetime import datetime
		products = self.all()
		for product in products:
			product.name = product.name.replace("\u00AD", '')
			product.modified = datetime.now()
			product.save()
		return True

# Product
class Product(models.Model):
	name = models.CharField(max_length=500)
	full_name = models.TextField()
	article = models.CharField(max_length=100)
	vendor = models.ForeignKey(Vendor)
	category = models.ForeignKey(Category, null=True, default=None)
	unit = models.ForeignKey(Unit, null=True, default=None)
	description = models.TextField()
	duble = models.ForeignKey('self', null=True, default=None)
	edited = models.BooleanField(default=False)
	state = models.BooleanField(default=True)
	price = models.ForeignKey(Price, null=True, default=None)
	quantity = models.ForeignKey(Quantity, null=True, default=None)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = ProductManager()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Party manager
class PartyManager(models.Manager):

	def make(self, product, stock, price, price_type, currency, quantity, unit):
		from datetime import datetime
		party = Party(product=product, stock=stock, price=price, price_type=price_type, currency=currency, quantity=quantity, unit=unit, created=datetime.now(), modified=datetime.now())
		party.save()
		return party

	def clear(self, stock):
		Party.objects.filter(stock=stock).delete()
		return True

# Party
class Party(models.Model):
	id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
	product = models.ForeignKey(Product)
	stock = models.ForeignKey(Stock)
	article = models.CharField(max_length=100, null=True, default=None) # Артикул поставщика
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=None)
	price_type = models.ForeignKey(PriceType, null=True, default=None)
	currency = models.ForeignKey(Currency, null=True, default=None)
	quantity = models.IntegerField(null=True, default=None)
	unit = models.ForeignKey(Unit, null=True, default=None)
	comment = models.TextField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = PartyManager()

	class Meta:
		ordering = ['-created']

# Party Hystory
class PartyHystory(models.Model):
	id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
	product = models.ForeignKey(Product)
	stock = models.ForeignKey(Stock)
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=None)
	price_type = models.ForeignKey(PriceType, null=True, default=None)
	currency = models.ForeignKey(Currency, null=True, default=None)
	quantity = models.IntegerField(null=True, default=None)
	unit = models.ForeignKey(Unit, null=True, default=None)
	comment = models.TextField()
	date = models.DateField()

	class Meta:
		ordering = ['-date']

# Price Hystory
class PriceHystory(models.Model):
	id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
	product = models.ForeignKey(Product)
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=None)
	price_type = models.ForeignKey(PriceType, null=True, default=None)
	currency = models.ForeignKey(Currency, null=True, default=None)
	date = models.DateField()

	class Meta:
		ordering = ['-date']

# Quantity Hystory
class QuantityHystory(models.Model):
	id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
	product = models.ForeignKey(Product)
	quantity = models.IntegerField(null=True, default=None)
	unit = models.ForeignKey(Unit, null=True, default=None)
	date = models.DateField()

	class Meta:
		ordering = ['-date']

# Parameter Type
class ParameterType(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	data_type = models.CharField(max_length=100)
	order = models.IntegerField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Parameter Type to Category
class ParameterTypeToCategory(models.Model):
	parameter_type = models.ForeignKey(ParameterType)
	category = models.ForeignKey(Category)
	order = models.IntegerField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

	class Meta:
		ordering = ['created']

# Parameter
class Parameter(models.Model):
	parameter_type = models.ForeignKey(ParameterType)
	product = models.ForeignKey(Product)
	value = models.TextField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

	class Meta:
		ordering = ['created']

# Category Synonym manager
class CategorySynonymManager(models.Manager):

	def take(self, name, updater=None, distributor=None, category=None):
		from datetime import datetime
		try:
			categorySynonym = self.get(name=name, updater=updater, distributor=distributor)
		except CategorySynonym.DoesNotExist:
			categorySynonym = CategorySynonym(name=name, updater=updater, distributor=distributor, category=category, created=datetime.now(), modified=datetime.now())
			categorySynonym.save()
		return categorySynonym

# Category Synonym
class CategorySynonym(models.Model):
	name = models.CharField(max_length=1024)
	updater = models.ForeignKey(Updater, null=True, default=None)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	category = models.ForeignKey(Category, null=True, default=None)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = CategorySynonymManager()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']

# Vendor Synonym manager
class VendorSynonymManager(models.Manager):

	def take(self, name, updater=None, distributor=None, vendor=None):
		from datetime import datetime
		try:
			vendorSynonym = self.get(name=name, updater=updater, distributor=distributor)
		except VendorSynonym.DoesNotExist:
			vendorSynonym = VendorSynonym(name=name, updater=updater, distributor=distributor, vendor=vendor, created=datetime.now(), modified=datetime.now())
			vendorSynonym.save()
		return vendorSynonym

# Vendor Synonym
class VendorSynonym(models.Model):
	name = models.CharField(max_length=1024)
	updater = models.ForeignKey(Updater, null=True, default=None)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	vendor = models.ForeignKey(Vendor, null=True, default=None)
	created = models.DateTimeField()
	modified = models.DateTimeField()
	objects = VendorSynonymManager()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']
