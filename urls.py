from django.conf.urls import patterns, url

from catalog import views

urlpatterns = patterns('',

	# Главная
	# ex: /catalog/
	url(r'^$', views.products, name='products'),


	# Product
	# TODO ex: /catalog/products/c/456-y/fujitsu/search/vfy-rx300/
	url(r'^products/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})/(?P<vendor>[a-zA-Z0-9_-]+)/search/(?P<search>[^\f\n\r\t\v\/]{2,})/$', views.products, name='products'),
	url(r'^products/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})/(?P<vendor>[a-zA-Z0-9_-]+)/search/(?P<search>[^\f\n\r\t\v\/]{2,})/page/(?P<page>[0-9]+)/$', views.products, name='products'),
	# TODO ex: /catalog/products/c/456-y/search/vfy-rx300/
	url(r'^products/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})/search/(?P<search>[^\f\n\r\t\v\/]{2,})/$', views.products, name='products'),
	url(r'^products/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})/search/(?P<search>[^\f\n\r\t\v\/]{2,})/page/(?P<page>[0-9]+)/$', views.products, name='products'),
	# TODO ex: /catalog/products/fujitsu/search/vfy-rx300/
	url(r'^products/(?P<vendor>[a-zA-Z0-9_-]+)/search/(?P<search>[^\f\n\r\t\v\/]+)/$', views.products, name='products'),
	url(r'^products/(?P<vendor>[a-zA-Z0-9_-]+)/search/(?P<search>[^\f\n\r\t\v\/]+)/page/(?P<page>[0-9]+)/$', views.products, name='products'),
	# TODO ex: /catalog/products/search/vfy-rx300/
	url(r'^products/search/(?P<search>[^\f\n\r\t\v\/]{2,})/$', views.products, name='products'),
	url(r'^products/search/(?P<search>[^\f\n\r\t\v\/]{2,})/page/(?P<page>[0-9]+)/$', views.products, name='products'),
	# TODO ex: /catalog/products/c/456-y/fujitsu/
	url(r'^products/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})/(?P<vendor>[a-zA-Z0-9_-]+)/$', views.products, name='products'),
	url(r'^products/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})/(?P<vendor>[a-zA-Z0-9_-]+)/page/(?P<page>[0-9]+)/$', views.products, name='products'),
	# TODO ex: /catalog/products/c/456-y/
	url(r'^products/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})/$', views.products, name='products'),
	url(r'^products/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})/page/(?P<page>[0-9]+)/$', views.products, name='products'),
	# TODO ex: /catalog/products/fujitsu/
	url(r'^products/(?P<vendor>[a-zA-Z0-9_-]+)/$', views.products, name='products'),
	url(r'^products/(?P<vendor>[a-zA-Z0-9_-]+)/page/(?P<page>[0-9]+)/$', views.products, name='products'),
	# TODO ex: /catalog/products/
	url(r'^products/$', views.products, name='products'),
	url(r'^products/page/(?P<page>[0-9]+)/$', views.products, name='products'),

	# ex: /catalog/product/125/
	url(r'^product/(?P<id>[0-9]+)/$', views.product, name='product'),
	# ex: /catalog/product/fujitsu/vfy-rx300/
	url(r'^product/(?P<vendor>[a-zA-Z0-9_-]+)/(?P<article>[^\f\n\r\t\v]+)/$', views.product, name='product'),


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
	url(r'^ajax/save-product/$', views.ajaxSaveProduct, name='ajaxSaveProduct'),

	url(r'^ajax/trash-category/$', views.ajaxTrashCategory, name='ajaxTrashCategory'),
	url(r'^ajax/trash-category-synonym/$', views.ajaxTrashCategorySynonym, name='ajaxTrashCategorySynonym'),

	url(r'^ajax/get-product/$', views.ajaxGetProduct, name='ajaxGetProduct'),

)
