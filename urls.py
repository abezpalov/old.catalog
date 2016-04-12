from django.conf.urls import patterns, url

from catalog import views

urlpatterns = patterns('',


	# Connector


	# Distributor
	url(r'^distributors/$', views.distributors, name='distributors'),


	# Updater
	url(r'^updaters/$', views.updaters, name='updaters'),


	# Stock TODO Refactoring
	url(r'^stocks/$', views.stocks, name='stocks'),


	# Category TODO Refactoring
	url(r'^categories/$', views.categories, name='categories'),
	url(r'^category/(?P<category_id>[0-9]+)/$', views.category, name='category'),
	# AJAX
	url(r'^ajax/save/category/$', views.ajaxSaveCategory, name='ajaxSaveCategory'),


	# Vendor TODO Refactoring
	url(r'^vendors/$', views.vendors, name='vendors'),
	url(r'^vendor/(?P<alias>[a-zA-Z0-9_-]+)/$', views.vendor, name='vendor'),
	# AJAX
	url(r'^ajax/save/vendor/$', views.ajaxSaveVendor, name='ajaxSaveVendor'),


	# Unit
	# TODO


	# Price Types TODO Refactoring
	url(r'^price-types/$', views.priceTypes, name='priceTypes'),
	# AJAX
	url(r'^ajax/save/pricetype/$', views.ajaxSavePriceType, name='ajaxSavePriceType'),


	# Currency TODO Refactoring
	url(r'^currencies/$', views.currencies, name='currencies'),
	# AJAX
	url(r'^ajax/save/currency/$', views.ajaxSaveCurrency, name='ajaxSaveCurrency'),


	# Price


	# Quantity


	# Product
	# ex: /catalog/ TODO Refactoring
	url(r'^$', views.products, name='products'),
	url(r'^products(/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})){0,1}(/(?P<vendor>[a-zA-Z0-9_-]+)){0,1}(/search/(?P<search>[\S\s]+)){0,1}/page/(?P<page>[0-9]+)/$', views.products, name='products'),
	url(r'^products(/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})){0,1}(/(?P<vendor>[a-zA-Z0-9_-]+)){0,1}(/search/(?P<search>[\S\s]+)){0,1}/$', views.products, name='products'),
	url(r'^product/(?P<id>[0-9]+)/$', views.product, name='product'),
	# AJAX
	url(r'^ajax/save/product/$', views.ajaxSaveProduct, name='ajaxSaveProduct'),


	# Party
	# AJAX
	url(r'^ajax/get-parties/$', views.ajaxGetParties, name='ajaxGetParties'),


	# Party Hystory


	# Price Hystory


	# Quantity Hystory


	# Parameter Type TODO Refactoring
	url(r'^parameter-types/$', views.parameterTypes, name='parameterTypes'),
	# AJAX
	url(r'^ajax/save/parameter-type/$', views.ajaxSaveParameterType, name='ajaxSaveParameterType'),


	# Parameter TODO Refactoring
	url(r'^parameters/$', views.parameters, name='parameters'),
	# AJAX
	url(r'^ajax/save/parameter/$', views.ajaxSaveParameter, name='ajaxSaveParameter'),


	# Parameter Value TODO Refactoring
	url(r'^parameter-values/$', views.parameterValues, name='parameterValues'),
	# AJAX
	url(r'^ajax/save/parameter-value/$', views.ajaxSaveParameterValue, name='ajaxSaveParameterValue'),


	# Parameter Value Synonym TODO Refactoring
	url(r'^parameter-value-synonyms/$', views.parametervaluesynonyms, name='parametervaluesynonyms'),
	url(r'^parameter-value-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', views.parametervaluesynonyms, name='parametervaluesynonyms'),
	# AJAX
	url(r'^ajax/save/parameter-value-synonym/$', views.ajaxSaveParameterValueSynonym, name='ajaxSaveParameterValueSynonym'),


	# Parameter to Category


	# Parameter to Product


	# Parameter Synonym TODO Refactoring
	url(r'^parameter-synonyms/$', views.parametersynonyms, name='parametersynonyms'),
	url(r'^parameter-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', views.parametersynonyms, name='parametersynonyms'),
	# AJAX
	url(r'^ajax/save/parameter-synonym/$', views.ajaxSaveParameterSynonym, name='ajaxSaveParameterSynonym'),

	# Category Synonym TODO Refactoring
	url(r'^category-synonyms/$', views.categorysynonyms, name='categorysynonyms'),
	url(r'^category-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<category_selected>[a-zA-Z0-9_-]+)/$', views.categorysynonyms, name='categorysynonyms'),
	# AJAX
	url(r'^ajax/save/category-synonym/$', views.ajaxSaveCategorySynonym, name='ajaxSaveCategorySynonym'),


	# Vendor Synonym TODO Refactoring
	url(r'^vendor-synonyms/$', views.vendorsynonyms, name='vendorsynonyms'),
	url(r'^vendor-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<vendor_selected>[a-zA-Z0-9_-]+)/$', views.vendorsynonyms, name='vendorsynonyms'),
	# AJAX
	url(r'^ajax/save/vendor-synonym/$', views.ajaxSaveVendorSynonym, name='ajaxSaveVendorSynonym'),

	# AJAX
	url(r'^ajax/get/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajaxGet, name='ajaxGet'),
	url(r'^ajax/save/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajaxSave, name='ajaxSave'),
	url(r'^ajax/switch-state/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajaxSwitchState, name='ajaxSwitchState'),
	url(r'^ajax/delete/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajaxDelete, name='ajaxDelete'),


)
