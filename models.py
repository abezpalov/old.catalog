from django.db import models

# Connector
class Connector(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	login = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	state = models.BooleanField()

# Distributor
class Distributor(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	connector = models.ForeignKey(Connector, null=True, default=None)
	state = models.BooleanField()

# Updater
class Updater(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	login = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	state = models.BooleanField()

# Stock
class Stock(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	delivery_time_min = models.IntegerField()
	delivery_time_max = models.IntegerField()
	state = models.BooleanField()

# Category
class Category(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	parent = models.ForeignKey('self', null=True, default=None)
	level = models.IntegerField()
	order = models.IntegerField()
	state = models.BooleanField()

# Vendor
class Vendor(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	state = models.BooleanField()

# Unit
class Unit(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	state = models.BooleanField()

# Product
class Product(models.Model):
	name = models.CharField(max_length=500)
	article = models.CharField(max_length=100)
	vendor = models.ForeignKey(Vendor)
	category = models.ForeignKey(Category, null=True, default=None)
	unit = models.ForeignKey(Unit)
	duble = models.ForeignKey('self', null=True, default=None)
	state = models.BooleanField()

# Price Type
class PriceType(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	state = models.BooleanField()

# Currency
class Currency(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	rate = models.DecimalField(max_digits=8, decimal_place=4)
	quantity = models.IntegerField()
	state = models.BooleanField()

# Party
class Party(models.Model):
	product = models.ForeignKey(Product)
	stock = models.ForeignKey(Stock)
	price = models.DecimalField(max_digits=12, decimal_place=2)
	currency = models.ForeignKey(Currency)
	quantity = models.IntegerField()
	unit = models.ForeignKey(Unit)
	state = models.BooleanField()

# Price
class Price(models.Model):
	product = models.ForeignKey(Product)
	price = models.DecimalField(max_digits=12, decimal_place=2)
	currency = models.ForeignKey(Currency)
	state = models.BooleanField()

# Price Hystory
class PriceHystory(models.Model):
	product = models.ForeignKey(Product)
	price = models.DecimalField(max_digits=12, decimal_place=2)
	currency = models.ForeignKey(Currency)
	date = models.DateField()

# Quantity
class Quantity(models.Model):
	product = models.ForeignKey(Product)
	quantity = models.IntegerField()
	unit = models.ForeignKey(Unit)
	state = models.BooleanField()

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
	state = models.BooleanField()

# Parameter Type to Category
class ParameterTypeToCategory(models.Model):
	parameter_type = models.ForeignKey(ParameterType)
	category = models.ForeignKey(Category)
	state = models.BooleanField()

# Parameter
class Parameter(models.Model):
	parameter_type = models.ForeignKey(ParameterType)
	product = models.ForeignKey(Product)
	value = models.TextField()
	state = models.BooleanField()

# Category Synonym
class CategorySynonym(models.Model):
	name = models.CharField(max_length=100)
	updater = models.ForeignKey(Updater, null=True, default=None)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	category = models.ForeignKey(Category, null=True, default=None)

# Vendor Synonym
class CategorySynonym(models.Model):
	name = models.CharField(max_length=100)
	updater = models.ForeignKey(Updater, null=True, default=None)
	distributor = models.ForeignKey(Distributor, null=True, default=None)
	vendor = models.ForeignKey(Vendor, null=True, default=None)
