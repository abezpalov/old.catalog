from django.conf.urls import patterns, url

from catalog import views

urlpatterns = patterns('',


	# Connector


	# Distributor
	url(r'^distributors/$', views.distributors, name='distributors'),
	# AJAX
	url(r'^ajax/save-distributor/$', views.ajaxSaveDistributor, name='ajaxSaveDistributor'),


	# Updater TODO Refactoring
	# ex: /catalog/updaters/
	url(r'^updaters/$', views.updaters, name='updaters'),
	# ex: /catalog/updater/ocs/
	url(r'^updater/(?P<alias>[a-zA-Z0-9_-]+)/$', views.updater, name='updater'),
	# AJAX
	url(r'^ajax/get-updater/$', views.ajaxGetUpdater, name='ajaxGetUpdater'),
	url(r'^ajax/save-updater/$', views.ajaxSaveUpdater, name='ajaxSaveUpdater'),
	url(r'^ajax/switch-updater-state/$', views.ajaxSwitchUpdaterState, name='ajaxSwitchUpdaterState'),


	# Stock TODO Refactoring
	# ex: /catalog/stocks/
	url(r'^stocks/$', views.stocks, name='stocks'),
	# ex: /catalog/stock/ocs-stock-samara/
	url(r'^stock/(?P<alias>[a-zA-Z0-9_-]+)/$', views.stock, name='stock'),
	# AJAX
	url(r'^ajax/get-stock/$', views.ajaxGetStock, name='ajaxGetStock'),
	url(r'^ajax/save-stock/$', views.ajaxSaveStock, name='ajaxSaveStock'),
	url(r'^ajax/switch-stock-state/$', views.ajaxSwitchStockState, name='ajaxSwitchStockState'),


	# Category TODO Refactoring
	# ex: /catalog/categories/
	url(r'^categories/$', views.categories, name='categories'),
	# ex: /catalog/category/98/
	url(r'^category/(?P<category_id>[0-9]+)/$', views.category, name='category'),
	# AJAX
	url(r'^ajax/get-category/$', views.ajaxGetCategory, name='ajaxGetCategory'),
	url(r'^ajax/save-category/$', views.ajaxSaveCategory, name='ajaxSaveCategory'),
	url(r'^ajax/switch-category-state/$', views.ajaxSwitchCategoryState, name='ajaxSwitchCategoryState'),
	url(r'^ajax/delete-category/$', views.ajaxDeleteCategory, name='ajaxDeleteCategory'),


	# Vendor TODO Refactoring
	# ex: /catalog/vendors/
	url(r'^vendors/$', views.vendors, name='vendors'),
	# ex: /catalog/vendor/fujitsu/
	url(r'^vendor/(?P<alias>[a-zA-Z0-9_-]+)/$', views.vendor, name='vendor'),
	# AJAX
	url(r'^ajax/get-vendor/$', views.ajaxGetVendor, name='ajaxGetVendor'),
	url(r'^ajax/save-vendor/$', views.ajaxSaveVendor, name='ajaxSaveVendor'),
	url(r'^ajax/switch-vendor-state/$', views.ajaxSwitchVendorState, name='ajaxSwitchVendorState'),


	# Unit
	# TODO


	# Price Types TODO Refactoring
	# ex: /catalog/price-types/
	url(r'^price-types/$', views.priceTypes, name='priceTypes'),
	# ex: /catalog/price-type/ddp/
	url(r'^price-type/(?P<alias>[a-zA-Z0-9_-]+)/$', views.priceType, name='priceType'),
	# AJAX
	url(r'^ajax/get-price-type/$', views.ajaxGetPriceType, name='ajaxGetPriceType'),
	url(r'^ajax/save-price-type/$', views.ajaxSavePriceType, name='ajaxSavePriceType'),
	url(r'^ajax/switch-price-type-state/$', views.ajaxSwitchPriceTypeState, name='ajaxSwitchPriceTypeState'),


	# Currency TODO Refactoring
	# ex: /catalog/currencies/
	url(r'^currencies/$', views.currencies, name='currencies'),
	# AJAX
	url(r'^ajax/get-currency/$', views.ajaxGetCurrency, name='ajaxGetCurrency'),
	url(r'^ajax/save-currency/$', views.ajaxSaveCurrency, name='ajaxSaveCurrency'),
	url(r'^ajax/switch-currency-state/$', views.ajaxSwitchCurrencyState, name='ajaxSwitchCurrencyState'),


	# Price
	# TODO


	# Quantity
	# TODO


	# Product
	# ex: /catalog/ TODO Refactoring
	url(r'^$', views.products, name='products'),
	# ex: /catalog/products/c/456-y/fujitsu/search/vfy-rx300/
	url(r'^products(/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})){0,1}(/(?P<vendor>[a-zA-Z0-9_-]+)){0,1}(/search/(?P<search>[\S\s]+)){0,1}/page/(?P<page>[0-9]+)/$', views.products, name='products'),
	url(r'^products(/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})){0,1}(/(?P<vendor>[a-zA-Z0-9_-]+)){0,1}(/search/(?P<search>[\S\s]+)){0,1}/$', views.products, name='products'),
	# ex: /catalog/product/125/
	url(r'^product/(?P<id>[0-9]+)/$', views.product, name='product'),
	# ex: /catalog/product/fujitsu/vfy-rx300/
	url(r'^product/(?P<vendor>[a-zA-Z0-9_-]+)/(?P<article>[^\f\n\r\t\v]+)/$', views.product, name='product'),
	# AJAX
	url(r'^ajax/get-product/$', views.ajaxGetProduct, name='ajaxGetProduct'),
	url(r'^ajax/save-product/$', views.ajaxSaveProduct, name='ajaxSaveProduct'),


	# Party
	# AJAX
	url(r'^ajax/get-parties/$', views.ajaxGetParties, name='ajaxGetParties'),


	# Party Hystory


	# Price Hystory


	# Quantity Hystory


	# Parameter Type TODO Refactoring
	# ex: /catalog/parameter-types/
	url(r'^parameter-types/$', views.parameterTypes, name='parameterTypes'),
	# AJAX
	url(r'^ajax/get-parameter-type/$', views.ajaxGetParameterType, name='ajaxGetParameterType'),
	url(r'^ajax/save-parameter-type/$', views.ajaxSaveParameterType, name='ajaxSaveParameterType'),
	url(r'^ajax/switch-parameter-type-state/$', views.ajaxSwitchParameterTypeState, name='ajaxSwitchParameterTypeState'),


	# Parameter TODO Refactoring
	# ex: /catalog/parameters/
	url(r'^parameters/$', views.parameters, name='parameters'),
	# AJAX
	url(r'^ajax/get-parameter/$', views.ajaxGetParameter, name='ajaxGetParameter'),
	url(r'^ajax/save-parameter/$', views.ajaxSaveParameter, name='ajaxSaveParameter'),
	url(r'^ajax/switch-parameter-state/$', views.ajaxSwitchParameterState, name='ajaxSwitchParameterState'),


	# Parameter Value TODO Refactoring
	# ex: /catalog/parameter-values/
	url(r'^parameter-values/$', views.parameterValues, name='parameterValues'),
	# AJAX
	url(r'^ajax/get-parameter-value/$', views.ajaxGetParameterValue, name='ajaxGetParameterValue'),
	url(r'^ajax/save-parameter-value/$', views.ajaxSaveParameterValue, name='ajaxSaveParameterValue'),


	# Parameter Value Synonym TODO Refactoring
	# ex: /catalog/parameter-value-synonyms/
	url(r'^parameter-value-synonyms/$', views.parametervaluesynonyms, name='parametervaluesynonyms'),
	# ex: /catalog/parameter-value-synonyms/1/2/none/
	url(r'^parameter-value-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', views.parametervaluesynonyms, name='parametervaluesynonyms'),
	# AJAX
	url(r'^ajax/save-parameter-value-synonym/$', views.ajaxSaveParameterValueSynonym, name='ajaxSaveParameterValueSynonym'),


	# Parameter to Category


	# Parameter to Product


	# Parameter Synonym TODO Refactoring
	# ex: /catalog/parameter-synonyms/
	url(r'^parameter-synonyms/$', views.parametersynonyms, name='parametersynonyms'),
	# ex: /catalog/parameter-synonyms/1/2/none/
	url(r'^parameter-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', views.parametersynonyms, name='parametersynonyms'),
	# AJAX
	url(r'^ajax/save-parameter-synonym/$', views.ajaxSaveParameterSynonym, name='ajaxSaveParameterSynonym'),

	# Category Synonym TODO Refactoring
	# ex: /catalog/category-synonyms/
	url(r'^category-synonyms/$', views.categorysynonyms, name='categorysynonyms'),
	# ex: /catalog/category-synonyms/1/2/none/
	url(r'^category-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<category_selected>[a-zA-Z0-9_-]+)/$', views.categorysynonyms, name='categorysynonyms'),
	# AJAX
	url(r'^ajax/save-category-synonym/$', views.ajaxSaveCategorySynonym, name='ajaxSaveCategorySynonym'),


	# Vendor Synonym TODO Refactoring
	# ex: /catalog/vendor-synonyms/
	url(r'^vendor-synonyms/$', views.vendorsynonyms, name='vendorsynonyms'),
	# ex: /catalog/vendor-synonyms/1/2/none/
	url(r'^vendor-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<vendor_selected>[a-zA-Z0-9_-]+)/$', views.vendorsynonyms, name='vendorsynonyms'),
	# AJAX
	url(r'^ajax/save-vendor-synonym/$', views.ajaxSaveVendorSynonym, name='ajaxSaveVendorSynonym'),

	# AJAX
	url(r'^ajax/get/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajaxGet, name='ajaxGet'),
	url(r'^ajax/switch-state/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajaxSwitchState, name='ajaxSwitchState'),
	url(r'^ajax/delete/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajaxDelete, name='ajaxDelete'),


)
