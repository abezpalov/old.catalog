from django.conf.urls import patterns, url

from catalog import views

urlpatterns = patterns('',

	# Главная
	# ex: /catalog/
	url(r'^$', views.index, name='index'),

	# Product
	# ex: /catalog/products/
	url(r'^products/$', views.products, name='products'),
	url(r'^products/(?P<category>[a-zA-Z0-9]+)/$', views.products, name='products'),
	url(r'^products/(?P<category>[a-zA-Z0-9]+)/(?P<childs>[a-z]+)/$', views.products, name='products'),
	url(r'^products/(?P<category>[a-zA-Z0-9]+)/(?P<childs>[a-z]+)/(?P<vendor>[a-zA-Z0-9_-]+)/$', views.products, name='products'),
	url(r'^products/(?P<category>[a-zA-Z0-9]+)/(?P<childs>[a-z]+)/(?P<vendor>[a-zA-Z0-9_-]+)/$', views.products, name='products'),
	url(r'^products/(?P<category>[a-zA-Z0-9]+)/(?P<childs>[a-z]+)/(?P<vendor>[a-zA-Z0-9_-]+)/(?P<search>[a-zA-Zа-яА-Я0-9 _-]+)/$', views.products, name='products'),

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
	# ex: /catalog/vendor-synonyms/1/2/none/
	url(r'^vendor-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<vendor_selected>[a-zA-Z0-9_-]+)/$', views.vendorsynonyms, name='vendorsynonyms'),
	# ex: /catalog/vendor-synonym/58/
	url(r'^vendor-synonym/(?P<synonym_id>[0-9]+)/$', views.vendorsynonym, name='vendorsynonym'),

	# Category Synonym
	# ex: /catalog/category-synonyms/
	url(r'^category-synonyms/$', views.categorysynonyms, name='categorysynonyms'),
	# ex: /catalog/category-synonyms/1/2/none/
	url(r'^category-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<category_selected>[a-zA-Z0-9_-]+)/$', views.categorysynonyms, name='categorysynonyms'),
	# ex: /catalog/category-synonym/58/
	url(r'^category-synonym/(?P<synonym_id>[0-9]+)/$', views.categorysynonym, name='categorysynonym'),

	# Price Types
	# ex: /catalog/price-types/
	url(r'^price-types/$', views.priceTypes, name='priceTypes'),
	# ex: /catalog/price-type/ddp/
	url(r'^price-type/(?P<alias>[a-zA-Z0-9_-]+)/$', views.priceType, name='priceType'),


	# AJAX
	url(r'^ajax/add-vendor/$', views.ajaxAddVendor, name='ajaxAddVendor'),
	url(r'^ajax/add-category/$', views.ajaxAddCategory, name='ajaxAddCategory'),

	url(r'^ajax/switch-vendor-state/$', views.ajaxSwitchVendorState, name='ajaxSwitchVendorState'),
	url(r'^ajax/switch-category-state/$', views.ajaxSwitchCategoryState, name='ajaxSwitchCategoryState'),
	url(r'^ajax/switch-updater-state/$', views.ajaxSwitchUpdaterState, name='ajaxSwitchUpdaterState'),
	url(r'^ajax/switch-price-type-state/$', views.ajaxSwitchPriceTypeState, name='ajaxSwitchPriceTypeState'),

	url(r'^ajax/link-vendor-synonym/$', views.ajaxLinkVendorSynonym, name='ajaxLinkVendorSynonym'),
	url(r'^ajax/link-vendor-same-synonym/$', views.ajaxLinkVendorSameSynonym, name='ajaxLinkVendorSameSynonym'),
	url(r'^ajax/link-category-synonym/$', views.ajaxLinkCategorySynonym, name='ajaxLinkCategorySynonym'),

	url(r'^ajax/save-updater/$', views.ajaxSaveUpdater, name='ajaxSaveUpdater'),
	url(r'^ajax/save-category/$', views.ajaxSaveCategory, name='ajaxSaveCategory'),
	url(r'^ajax/save-vendor/$', views.ajaxSaveVendor, name='ajaxSaveVendor'),
	url(r'^ajax/save-price-type/$', views.ajaxSavePriceType, name='ajaxSavePriceType'),

	url(r'^ajax/trash-category/$', views.ajaxTrashCategory, name='ajaxTrashCategory'),
)
