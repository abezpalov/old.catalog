from django.conf.urls import patterns, url

from catalog import views

urlpatterns = patterns('',

	url(r'^distributors/$', views.distributors, name='distributors'),

	url(r'^updaters/$', views.updaters, name='updaters'),

	url(r'^stocks/$', views.stocks, name='stocks'),

	url(r'^categories/$', views.categories, name='categories'),

	url(r'^vendors/$', views.vendors, name='vendors'),
	url(r'^vendor/(?P<alias>[a-zA-Z0-9_-]+)/$', views.vendor, name='vendor'),

	url(r'^pricetypes/$', views.pricetypes, name='pricetypes'),

	url(r'^currencies/$', views.currencies, name='currencies'),

	url(r'^$', views.products, name='products'),
	url(r'^products(/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})){0,1}(/(?P<vendor>[a-zA-Z0-9_-]+)){0,1}(/search/(?P<search>[\S\s]+)){0,1}/page/(?P<page>[0-9]+)/$', views.products, name='products'),
	url(r'^products(/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})){0,1}(/(?P<vendor>[a-zA-Z0-9_-]+)){0,1}(/search/(?P<search>[\S\s]+)){0,1}/$', views.products, name='products'),
	url(r'^product/(?P<id>[0-9]+)/$', views.product, name='product'),

	url(r'^parametertypes/$', views.parametertypes, name='parametertypes'),

	url(r'^parameters/$', views.parameters, name='parameters'),

	url(r'^parametervalues/$', views.parametervalues, name='parametervalues'),

	url(r'^parametervaluesynonyms/$', views.parametervaluesynonyms, name='parametervalue_synonyms'),
	url(r'^parametervaluesynonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', views.parametervaluesynonyms, name='parametervaluesynonyms'),

	url(r'^parametersynonyms/$', views.parametersynonyms, name='parameter_synonyms'),
	url(r'^parametersynonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', views.parametersynonyms, name='parametersynonyms'),

	url(r'^categorysynonyms/$', views.categorysynonyms, name='category_synonyms'),
	url(r'^categorysynonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<category_selected>[a-zA-Z0-9_-]+)/$', views.categorysynonyms, name='categorysynonyms'),

	url(r'^vendorsynonyms/$', views.vendorsynonyms, name='vendor_synonyms'),
	url(r'^vendorsynonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<distributor_selected>[a-zA-Z0-9_-]+)/(?P<vendor_selected>[a-zA-Z0-9_-]+)/$', views.vendorsynonyms, name='vendorsynonyms'),


	# AJAX
	url(r'^ajax/get/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajax_get, name='ajax_get'),
	url(r'^ajax/save/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajax_save, name='ajax_save'),
	url(r'^ajax/switch-state/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajax_switch_state, name='ajax_switch_state'),
	url(r'^ajax/delete/(?P<model_name>[a-zA-Z0-9_-]+)/$', views.ajax_delete, name='ajax_delete'),
	url(r'^ajax/link/(?P<model_name>[a-zA-Z0-9_-]+)/same/(?P<foreign_name>[a-zA-Z0-9_-]+)/$', views.ajax_link_same_foreign, name='ajax_link_same_foreign'),

	url(r'^ajax/get-parties/$', views.ajax_get_parties, name='ajax_get_parties'),
)
