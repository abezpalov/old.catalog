from django.shortcuts import render

# TODO времено?
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world.")

def updaters(request):
    return HttpResponse("Список загрузчиков.")

def updater(request, alias):
    return HttpResponse("Загрузчик %s." % alias)

def update(request, alias):
    return HttpResponse("Выполнение загрузчика %s." % alias)

