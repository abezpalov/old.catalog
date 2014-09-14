from django.conf.urls import patterns, url

from catalog import views

urlpatterns = patterns('',
    # ex: /catalog/
    url(r'^$', views.index, name='index'),
    # ex: /catalog/updaters/
    url(r'^updaters/$', views.updaters, name='updaters'),
    # ex: /catalog/updater/ocs/
    url(r'^updater/(?P<alias>[a-zA-Z0-9_]+)/$', views.updater, name='updater'),
    # ex: /catalog/updater/ocs/run/[key/]
    url(r'^updater/(?P<alias>[a-zA-Z0-9_-]+)/run/$', views.update, name='update'),
    url(r'^updater/(?P<alias>[a-zA-Z0-9_-]+)/run/(?P<key>[a-zA-Z0-9]+)/$', views.update, name='update'),
)
