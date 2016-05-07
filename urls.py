from django.conf.urls import patterns, url
from django.contrib import admin

import catalog.views

urlpatterns = [

	url(r'^distributors/$', catalog.views.distributors),

	url(r'^updaters/$', catalog.views.updaters),

	url(r'^stocks/$', catalog.views.stocks),

	url(r'^categories/$', catalog.views.categories),

	url(r'^vendors/$', catalog.views.vendors),
	url(r'^vendor/(?P<alias>[a-zA-Z0-9_-]+)/$', catalog.views.vendor),

	url(r'^units/$', catalog.views.units),

	url(r'^pricetypes/$', catalog.views.pricetypes),

	url(r'^currencies/$', catalog.views.currencies),

	url(r'^$', catalog.views.products),
	url(r'^products(/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})){0,1}(/(?P<vendor>[a-zA-Z0-9_-]+)){0,1}(/search/(?P<search>[\S\s]+)){0,1}/page/(?P<page>[0-9]+)/$', catalog.views.products),
	url(r'^products(/c/(?P<category>[0-9]+)-(?P<childs>[yn]{1})){0,1}(/(?P<vendor>[a-zA-Z0-9_-]+)){0,1}(/search/(?P<search>[\S\s]+)){0,1}/$', catalog.views.products),
	url(r'^product/(?P<id>[0-9]+)/$', catalog.views.product),

	url(r'^parametertypes/$', catalog.views.parametertypes),

	url(r'^parameters/$', catalog.views.parameters),

	url(r'^parametervalues/$', catalog.views.parametervalues),

	url(r'^parametervaluesynonyms/$', catalog.views.parametervaluesynonyms),
	url(r'^parametervaluesynonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', catalog.views.parametervaluesynonyms),

	url(r'^parametersynonyms/$', catalog.views.parametersynonyms),
	url(r'^parametersynonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', catalog.views.parametersynonyms),

	url(r'^categorysynonyms/$', catalog.views.categorysynonyms),
	url(r'^categorysynonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<category_selected>[a-zA-Z0-9_-]+)/$', catalog.views.categorysynonyms),

	url(r'^vendorsynonyms/$', catalog.views.vendorsynonyms),
	url(r'^vendorsynonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<vendor_selected>[a-zA-Z0-9_-]+)/$', catalog.views.vendorsynonyms),

	# AJAX
	url(r'^ajax/get/(?P<model_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_get),
	url(r'^ajax/save/(?P<model_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_save),
	url(r'^ajax/switch-state/(?P<model_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_switch_state),
	url(r'^ajax/delete/(?P<model_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_delete),
	url(r'^ajax/link/(?P<model_name>[a-zA-Z0-9_-]+)/same/(?P<foreign_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_link_same_foreign),

	url(r'^ajax/get-parties/$', catalog.views.ajax_get_parties)
]
