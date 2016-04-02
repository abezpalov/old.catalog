from django.contrib import admin
from catalog.models import Distributor
from catalog.models import Updater
from catalog.models import Stock
from catalog.models import Connector
from catalog.models import Category
from catalog.models import Vendor
from catalog.models import Unit
from catalog.models import Product
from catalog.models import PriceType
from catalog.models import Currency
from catalog.models import Party
from catalog.models import Price
from catalog.models import PriceHystory
from catalog.models import Quantity
from catalog.models import QuantityHystory
from catalog.models import CategorySynonym
from catalog.models import VendorSynonym

admin.site.register(Distributor)
admin.site.register(Updater)
admin.site.register(Stock)
admin.site.register(Connector)
admin.site.register(Category)
admin.site.register(Vendor)
admin.site.register(Unit)
admin.site.register(Product)
admin.site.register(PriceType)
admin.site.register(Currency)
admin.site.register(Party)
admin.site.register(Price)
admin.site.register(PriceHystory)
admin.site.register(Quantity)
admin.site.register(QuantityHystory)
admin.site.register(CategorySynonym)
admin.site.register(VendorSynonym)
