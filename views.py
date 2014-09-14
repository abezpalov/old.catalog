from django.shortcuts import render

# TODO времено?
from django.http import HttpResponse
from django.template import RequestContext, loader

from catalog.models import Updater


# Каталог
def index(request):
    return HttpResponse("Hello, world.")


# Список загрузчиков
def updaters(request):
	updaters_list = Updater.objects.all()
	context = {'updaters_list': updaters_list}
	return render(request, 'catalog/updaters.html', context)


# Описание загрузчика
def updater(request, alias):
	return HttpResponse("Загрузчик %s." % alias)


# Выполнение загрузчика
def update(request, alias, key=''):
	Updater = __import__('catalog.updaters.' + alias, fromlist=['Update'])
	# TODO Добавить проверку ключа перед запуском загрузчика
	update = Updater.Update()
	context = {'update_name': update.name, 'update_message': update.message}
	return render(request, 'catalog/update.html', context)
