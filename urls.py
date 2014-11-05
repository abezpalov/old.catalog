from django.conf.urls import patterns, url

from catalog import views

urlpatterns = patterns('',

	# Главная
	# ex: /catalog/
	url(r'^$', views.index, name='index'),

	# Updater
	# ex: /catalog/updaters/
	url(r'^updaters/$', views.updaters, name='updaters'),
	# ex: /catalog/updater/ocs/
	url(r'^updater/(?P<alias>[a-zA-Z0-9_-]+)/$', views.updater, name='updater'),
	# ex: /catalog/updater/ocs/run/[key/]
	url(r'^updater/(?P<alias>[a-zA-Z0-9_-]+)/run/$', views.update, name='update'),
	url(r'^updater/(?P<alias>[a-zA-Z0-9_-]+)/run/(?P<key>[a-zA-Z0-9]+)/$', views.update, name='update'),

	# Vendor
	# ex: /catalog/vendors/
	url(r'^vendors/$', views.vendors, name='vendors'),
	# ex: /catalog/vendor/fujitsu/
	url(r'^vendor/(?P<alias>[a-zA-Z0-9_-]+)/$', views.vendor, name='vendor'),

	# Category
	# ex: /catalog/categories/
	url(r'^categories/$', views.categories, name='categories'),
	# ex: /catalog/category/98/
	url(r'^category/(?P<category_id>[0-9]+)/$', views.category, name='category'),

	# Vendor Synonym
	# ex: /catalog/vendor-synonyms/
	url(r'^vendor-synonyms/$', views.vendorsynonyms, name='vendorsynonyms'),
	# ex: /catalog/vendor-synonyms/ocs/
	url(r'^vendor-synonyms/(?P<alias>[a-zA-Z0-9_-]+)/$', views.vendorsynonyms, name='vendorsynonyms'),
	# ex: /catalog/vendor-synonym/58/
	url(r'^vendor-synonym/(?P<synonym_id>[0-9]+)/$', views.vendorsynonym, name='vendorsynonym'),

	# Category Synonym
	# ex: /catalog/category-synonyms/
	url(r'^category-synonyms/$', views.categorysynonyms, name='categorysynonyms'),
	# ex: /catalog/category-synonyms/ocs/
	url(r'^category-synonyms/(?P<alias>[a-zA-Z0-9_-]+)/$', views.categorysynonyms, name='categorysynonyms'),
	# ex: /catalog/category-synonym/58/
	url(r'^category-synonym/(?P<synonym_id>[0-9]+)/$', views.categorysynonym, name='categorysynonym'),

	# AJAX
	url(r'^ajax/add/vendor/$', views.ajaxAddVendor, name='ajaxAddVendor'),
	url(r'^ajax/switch/vendor/state/$', views.ajaxSwitchVendorState, name='ajaxSwitchVendorState'),
)
