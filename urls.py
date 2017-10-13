from django.conf.urls import url
from django.contrib import admin

import catalog.views

urlpatterns = [

    url(r'^manage/updaters/$', catalog.views.manage_updaters),
    url(r'^manage/distributors/$', catalog.views.manage_distributors),
    url(r'^manage/stocks/$', catalog.views.manage_stocks),

    url(r'^manage/vendors/$', catalog.views.manage_vendors),

    url(r'^manage/categories/$', catalog.views.manage_categories),
    url(r'^manage/products/(?P<string>[\S\s]*)$', catalog.views.manage_products),

    url(r'^units/$', catalog.views.units),

    url(r'^pricetypes/$', catalog.views.pricetypes),

    url(r'^currencies/$', catalog.views.currencies),

    url(r'^$', catalog.views.products),
    url(r'^products/(?P<string>[\S\s]*)$', catalog.views.products),
#   url(r'^products(/category/(?P<category>[0-9]+)-(?P<childs>[yn]{1})){0,1}(/vendor/(?P<vendor>[a-zA-Z0-9_-]+)){0,1}(/search/(?P<search>[\S\s]+)){0,1}(/page/(?P<page>[0-9]+)){0,1}/$', catalog.views.products),
#   url(r'^products(/category/(?P<category>[0-9]+)-(?P<childs>[yn]{1})){0,1}(/vendor/(?P<vendor>[a-zA-Z0-9_-]+)){0,1}(/search/(?P<search>[\S\s]+)){0,1}/$', catalog.views.products),
    url(r'^product/(?P<id>[0-9]+)/$', catalog.views.product),

    url(r'^parametertypes/$', catalog.views.parametertypes),

    url(r'^parameters/$', catalog.views.parameters),

    url(r'^parametervalues/$', catalog.views.parametervalues),

    url(r'^parametervaluesynonyms/$', catalog.views.parametervaluesynonyms),
    url(r'^parametervaluesynonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', catalog.views.parametervaluesynonyms),

    url(r'^parametersynonyms/$', catalog.views.parametersynonyms),
    url(r'^parametersynonyms/(?P<updater_selected>[a-zA-Z0-9_-]+)/(?P<parameter_selected>[a-zA-Z0-9_-]+)/$', catalog.views.parametersynonyms),

    # AJAX
    url(r'^ajax/get/(?P<model_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_get),
    url(r'^ajax/save/(?P<model_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_save),
    url(r'^ajax/switch-state/(?P<model_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_switch_state),
    url(r'^ajax/delete/(?P<model_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_delete),
    url(r'^ajax/link/(?P<model_name>[a-zA-Z0-9_-]+)/same/(?P<foreign_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_link_same_foreign),
    url(r'^ajax/link/(?P<model_name>[a-zA-Z0-9_-]+)/$', catalog.views.ajax_link),

    url(r'^ajax/get-parties/$', catalog.views.ajax_get_parties)
]
