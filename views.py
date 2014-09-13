from django.shortcuts import render

# TODO времено?
from django.http import HttpResponse
from django.template import RequestContext, loader

from catalog.models import Updater

def index(request):
    return HttpResponse("Hello, world.")

def updaters(request):
	updaters_list = Updater.objects.all()
	context = {'updaters_list': updaters_list}
	return render(request, 'catalog/updaters.html', context)

def updater(request, alias):
	return HttpResponse("Загрузчик %s." % alias)

def update(request, alias):
	Updater = __import__('catalog.updaters.' + alias, fromlist=['Update'])
	update = Updater.Update()
	context = {'update_name': update.name, 'update_message': update.message}
	return render(request, 'catalog/update.html', context)
