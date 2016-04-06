from django.conf.urls import patterns, url

from catalog import views

urlpatterns = patterns('',


	# Connector
	# TODO


	# Distributor
	# ex: /catalog/distributors/
	url(r'^distributors/$', views.distributors, name='distributors'),
	# ex: /catalog/distributor/ocs/
	url(r'^distributor/(?P<alias>[a-zA-Z0-9_-]+)/$', views.distributor, name='distributor'),
	# AJAX
	url(r'^ajax/get-distributor/$', views.ajaxGetDistributor, name='ajaxGetDistributor'),
	url(r'^ajax/save-distributor/$', views.ajaxSaveDistributor, name='ajaxSaveDistributor'),
	url(r'^ajax/switch-distributor-state/$', views.ajaxSwitchDistributorState, name='ajaxSwitchDistributorState'),


	# Updater
	# ex: /catalog/updaters/
	url(r'^updaters/$', views.updaters, name='updaters'),
	# ex: /catalog/updater/ocs/
	url(r'^updater/(?P<alias>[a-zA-Z0-9_-]+)/$', views.updater, name='updater'),
	# AJAX
	url(r'^ajax/get-updater/$', views.ajaxGetUpdater, name='ajaxGetUpdater'),
	url(r'^ajax/save-updater/$', views.ajaxSaveUpdater, name='ajaxSaveUpdater'),
	url(r'^ajax/switch-updater-state/$', views.ajaxSwitchUpdaterState, name='ajaxSwitchUpdaterState'),


	# Stock
	# ex: /catalog/stocks/
	url(r'^stocks/$', views.stocks, name='stocks'),
	# ex: /catalog/stock/ocs-stock-samara/
	url(r'^stock/(?P<alias>[a-zA-Z0-9_-]+)/$', views.stock, name='stock'),
	# AJAX
	url(r'^ajax/get-stock/$', views.ajaxGetStock, name='ajaxGetStock'),
	url(r'^ajax/save-stock/$', views.ajaxSaveStock, name='ajaxSaveStock'),
	url(r'^ajax/switch-stock-state/$', views.ajaxSwitchStockState, name='ajaxSwitchStockState'),


	# Category
	# ex: /catalog/categories/
	url(r'^categories/$', views.categories, name='categories'),
	# ex: /catalog/category/98/
	url(r'^category/(?P<category_id>[0-9]+)/$', views.category, name='category'),
	# AJAX
	url(r'^ajax/get-category/$', views.ajaxGetCategory, name='ajaxGetCategory'),
	url(r'^ajax/save-category/$', views.ajaxSaveCategory, name='ajaxSaveCategory'),
	url(r'^ajax/switch-category-state/$', views.ajaxSwitchCategoryState, name='ajaxSwitchCategoryState'),
	url(r'^ajax/delete-category/$', views.ajaxDeleteCategory, name='ajaxDeleteCategory'),


	# Vendor
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


	# Price Types
	# ex: /catalog/price-types/
	url(r'^price-types/$', views.priceTypes, name='priceTypes'),
	# ex: /catalog/price-type/ddp/
	url(r'^price-type/(?P<alias>[a-zA-Z0-9_-]+)/$', views.priceType, name='priceType'),
	# AJAX
	url(r'^ajax/get-price-type/$', views.ajaxGetPriceType, name='ajaxGetPriceType'),
	url(r'^ajax/save-price-type/$', views.ajaxSavePriceType, name='ajaxSavePriceType'),
	url(r'^ajax/switch-price-type-state/$', views.ajaxSwitchPriceTypeState, name='ajaxSwitchPriceTypeState'),


	# Currency
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
	# ex: /catalog/
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
	# TODO


	# Price Hystory
	# TODO


	# Quantity Hystory
	# TODO


	# Parameter Type
	# ex: /catalog/parameter-types/
	url(r'^parameter-types/$', views.parameterTypes, name='parameterTypes'),
	# ex: /catalog/parameter-type/text/
	url(r'^parameter-type/(?P<alias>[a-zA-Z0-9_-]+)/$', views.parameterType, name='parameterType'),
	# AJAX
	url(r'^ajax/get-parameter-type/$', views.ajaxGetParameterType, name='ajaxGetParameterType'),
	url(r'^ajax/save-parameter-type/$', views.ajaxSaveParameterType, name='ajaxSaveParameterType'),
	url(r'^ajax/switch-parameter-type-state/$', views.ajaxSwitchParameterTypeState, name='ajaxSwitchParameterTypeState'),


	# Parameter
	# ex: /catalog/parameters/
	url(r'^parameters/$', views.parameters, name='parameters'),
	# ex: /catalog/parameter/massa/
	url(r'^parameter/(?P<alias>[a-zA-Z0-9_-]+)/$', views.parameter, name='parameter'),
	# AJAX
	url(r'^ajax/get-parameter/$', views.ajaxGetParameter, name='ajaxGetParameter'),
	url(r'^ajax/save-parameter/$', views.ajaxSaveParameter, name='ajaxSaveParameter'),
	url(r'^ajax/switch-parameter-state/$', views.ajaxSwitchParameterState, name='ajaxSwitchParameterState'),


	# Parameter to Category
	# TODO


	# Parameter to Product
	# TODO


	# Parameter Synonym
	# TODO
	# ex: /catalog/parameter-synonyms/
	url(r'^parameter-synonyms/$', views.parametersynonyms, name='parametersynonyms'),
	# ex: /catalog/parameter-synonyms/1/2/none/
	url(r'^parameter-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', views.parametersynonyms, name='parametersynonyms'),
	# AJAX
	url(r'^ajax/get-parameter-synonym/$', views.ajaxGetParameterSynonym, name='ajaxGetParameterSynonym'),
	url(r'^ajax/save-parameter-synonym/$', views.ajaxSaveParameterSynonym, name='ajaxSaveParameterSynonym'),
	url(r'^ajax/delete-parameter-synonym/$', views.ajaxDeleteParameterSynonym, name='ajaxDeleteParameterSynonym'),
	url(r'^ajax/link-parameter-synonym-same-parameter/$', views.ajaxLinkParameterSynonymSameParameter, name='ajaxLinkParameterSynonymSameParameter'),

	# Category Synonym
	# ex: /catalog/category-synonyms/
	url(r'^category-synonyms/$', views.categorysynonyms, name='categorysynonyms'),
	# ex: /catalog/category-synonyms/1/2/none/
	url(r'^category-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<category_selected>[a-zA-Z0-9_-]+)/$', views.categorysynonyms, name='categorysynonyms'),
	# AJAX
	url(r'^ajax/get-category-synonym/$', views.ajaxGetCategorySynonym, name='ajaxGetCategorySynonym'),
	url(r'^ajax/save-category-synonym/$', views.ajaxSaveCategorySynonym, name='ajaxSaveCategorySynonym'),
	url(r'^ajax/delete-category-synonym/$', views.ajaxDeleteCategorySynonym, name='ajaxDeleteCategorySynonym'),


	# Vendor Synonym
	# ex: /catalog/vendor-synonyms/
	url(r'^vendor-synonyms/$', views.vendorsynonyms, name='vendorsynonyms'),
	# ex: /catalog/vendor-synonyms/1/2/none/
	url(r'^vendor-synonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<vendor_selected>[a-zA-Z0-9_-]+)/$', views.vendorsynonyms, name='vendorsynonyms'),
	# AJAX
	url(r'^ajax/get-vendor-synonym/$', views.ajaxGetVendorSynonym, name='ajaxGetVendorSynonym'),
	url(r'^ajax/save-vendor-synonym/$', views.ajaxSaveVendorSynonym, name='ajaxSaveVendorSynonym'),
	url(r'^ajax/delete-vendor-synonym/$', views.ajaxDeleteVendorSynonym, name='ajaxDeleteVendorSynonym'),
	url(r'^ajax/link-vendor-synonym-same-vendor/$', views.ajaxLinkVendorSynonymSameVendor, name='ajaxLinkVendorSynonymSameVendor'),
)
