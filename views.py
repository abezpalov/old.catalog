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
	return HttpResponse("Выполнение загрузчика %s." % Updater.Update.name)
