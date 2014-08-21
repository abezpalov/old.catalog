from django.db import models
from django.contrib import admin

# Connector
class Connector(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	login = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Distributor
class Distributor(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	description = models.TextField()
	connector = models.ForeignKey(Connector, null=True, default=None)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

class DistributorAdmin(admin.ModelAdmin):
	list_display = ('name', 'state')

# Updater
class Updater(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	login = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Stock
class Stock(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	delivery_time_min = models.IntegerField()
	delivery_time_max = models.IntegerField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Category
class Category(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	description = models.TextField()
	parent = models.ForeignKey('self', null=True, default=None)
	level = models.IntegerField()
	order = models.IntegerField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Vendor
class Vendor(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	description = models.TextField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Unit
class Unit(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Product
class Product(models.Model):
	name = models.CharField(max_length=100)
	full_name = models.CharField(max_length=500)
	article = models.CharField(max_length=100)
	vendor = models.ForeignKey(Vendor)
	category = models.ForeignKey(Category, null=True, default=None)
	unit = models.ForeignKey(Unit)
	description = models.TextField()
	duble = models.ForeignKey('self', null=True, default=None)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Price Type
class PriceType(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Currency
class Currency(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	rate = models.DecimalField(max_digits=10, decimal_places=4)
	quantity = models.IntegerField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Party
class Party(models.Model):
	product = models.ForeignKey(Product)
	stock = models.ForeignKey(Stock)
	price = models.DecimalField(max_digits=12, decimal_places=2)
	price_type = models.ForeignKey(PriceType)
	currency = models.ForeignKey(Currency)
	quantity = models.IntegerField()
	unit = models.ForeignKey(Unit)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Price
class Price(models.Model):
	product = models.ForeignKey(Product)
	price = models.DecimalField(max_digits=12, decimal_places=2)
	price_type = models.ForeignKey(PriceType)
	currency = models.ForeignKey(Currency)
	fixed = models.BooleanField(default=False)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Price Hystory
class PriceHystory(models.Model):
	product = models.ForeignKey(Product)
	price = models.DecimalField(max_digits=12, decimal_places=2)
	price_type = models.ForeignKey(PriceType)
	currency = models.ForeignKey(Currency)
	date = models.DateField()

# Quantity
class Quantity(models.Model):
	product = models.ForeignKey(Product)
	quantity = models.IntegerField()
	unit = models.ForeignKey(Unit)
	fixed = models.BooleanField(default=False)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Quantity Hystory
class QuantityHystory(models.Model):
	product = models.ForeignKey(Product)
	quantity = models.IntegerField()
	unit = models.ForeignKey(Unit)
	date = models.DateField()

# Parameter Type
class ParameterType(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	data_type = models.CharField(max_length=100)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Parameter Type to Category
class ParameterTypeToCategory(models.Model):
	parameter_type = models.ForeignKey(ParameterType)
	category = models.ForeignKey(Category)
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Parameter
class Parameter(models.Model):
	parameter_type = models.ForeignKey(ParameterType)
	product = models.ForeignKey(Product)
	value = models.TextField()
	state = models.BooleanField(default=True)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Category Synonym
class CategorySynonym(models.Model):
	name = models.CharField(max_length=100)
	updater = models.ForeignKey(Updater, null=True, default=None)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	category = models.ForeignKey(Category, null=True, default=None)
	created = models.DateTimeField()
	modified = models.DateTimeField()

# Vendor Synonym
class VendorSynonym(models.Model):
	name = models.CharField(max_length=100)
	updater = models.ForeignKey(Updater, null=True, default=None)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	vendor = models.ForeignKey(Vendor, null=True, default=None)
	created = models.DateTimeField()
	modified = models.DateTimeField()

admin.site.register(Distributor, DistributorAdmin)
