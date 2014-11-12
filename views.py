from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader


# Каталог (главная)
def index(request):
    return HttpResponse("Hello, world.")


# Список загрузчиков
def updaters(request):

	# Импортируем
	from catalog.models import Updater

	# Получаем список
	updaters = Updater.objects.all()
	context = {'updaters': updaters}
	return render(request, 'catalog/updaters.html', context)


# Загрузчик TODO
def updater(request, alias):

	# Импортируем
	from catalog.models import Updater

	# Получаем список
	updater = Updater.objects.get(alias=alias)
	context = {'updater': updater}
	return render(request, 'catalog/updater.html', context)


# Выполнение загрузчика
def update(request, alias, key=''):
	Updater = __import__('catalog.updaters.' + alias, fromlist=['Update'])
	update = Updater.Update()
	context = {'update_name': update.name, 'update_message': update.message}
	return render(request, 'catalog/update.html', context)


# Список производителей
def vendors(request):

	# Импортируем
	from catalog.models import Vendor

	# Получаем список
	vendors = Vendor.objects.all().order_by('name')
	context = {'vendors': vendors}
	return render(request, 'catalog/vendors.html', context)


# Производитель
def vendor(request, alias):

	# Импортируем
	from catalog.models import Vendor

	# Получаем список
	vendor = Vendor.objects.get(alias=alias)
	context = {'vendor': vendor}
	return render(request, 'catalog/vendor.html', context)


# Список категорий
def categories(request):

	# Импортируем
	from catalog.models import Category

	# Получаем список
	categories = Category.objects.all()
	context = {'categories': categories}
	return render(request, 'catalog/categories.html', context)


# Категория
def category(request, category_id):

	# Импортируем
	from catalog.models import Category

	# Получаем список
	category = Category.objects.get(id=category_id)
	context = {'category': category}
	return render(request, 'catalog/category.html', context)

# Список синонимов производителей
def vendorsynonyms(request, alias=None):

	# Импортируем
	from catalog.models import VendorSynonym, Vendor, Updater, Distributor

	# Получаем список
	synonyms = VendorSynonym.objects.all().order_by('name')
	vendors = Vendor.objects.all().order_by('name')
	context = {'synonyms': synonyms, 'vendors': vendors}
	return render(request, 'catalog/vendorsynonyms.html', context)


# Синоним производителя
def vendorsynonym(request, synonym_id):

	# Импортируем
	from catalog.models import VendorSynonym, Vendor, Updater, Distributor

	# Получаем список
	synonym = VendorSynonym.objects.get(id=synonym_id)
	context = {'synonym': synonym}
	return render(request, 'catalog/vendorsynonym.html', context)


# Список синонимов категорий
def categorysynonyms(request, alias=None):

	# Импортируем
	from catalog.models import CategorySynonym, Category, Updater, Distributor

	# Получаем список
	synonyms = CategorySynonym.objects.all().order_by('name')
	context = {'synonyms': synonyms}
	return render(request, 'catalog/categorysynonyms.html', context)


# Синоним производителя
def categorysynonym(request, synonym_id):

	# Импортируем
	from catalog.models import CategorySynonym, Category, Updater, Distributor

	# Получаем список
	synonym = CategorySynonym.objects.get(id=synonym_id)
	context = {'synonym': synonym}
	return render(request, 'catalog/categorysynonym.html', context)


##  AJAX  ##


# Add Vendor
def ajaxAddVendor(request):

	# Импортируем
	from catalog.models import Vendor
	from datetime import datetime
	from django.utils import simplejson

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST') :
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Проверяем на пустую строку
	if (request.POST.get('new_vendor').strip() == ''):
		result = {'status': 'warning', 'message': 'Пожалуй, такого имени быть не может.'}
	else:
		# Добавляем производителя
		try:
			vendor = Vendor.objects.get(name=request.POST.get('new_vendor').strip())
			result = {'status': 'warning', 'message': 'Производитель ' + request.POST.get('new_vendor').strip() + ' уже существует.'}
		except Vendor.DoesNotExist:
			name = request.POST.get('new_vendor').strip()
			alias = name.lower()
			alias = alias.replace(' ', '-')
			vendor = Vendor(name=name, alias=alias, created=datetime.now(), modified=datetime.now())
			vendor.save()
			result = {'status': 'success', 'message': 'Производитель ' + name + ' добавлен.', 'vendorId': vendor.id, 'vendorName': vendor.name, 'vendorAlias': vendor.alias}

	# Возвращаем ответ
	return HttpResponse(simplejson.dumps(result), 'application/javascript')


# TODO Add Category
def ajaxAddCategory(request):

	# Импортируем
	from catalog.models import Category
	from django.db.models import Max # TODO test
	from datetime import datetime
	from django.utils import simplejson

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST') :
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Проверяем на пустые значения
	if (request.POST.get('newCategoryName').strip() == '') or (request.POST.get('newCategoryParent').strip() == ''):
		result = {'status': 'warning', 'message': 'Пожалуй, такого имени быть не может.'}
	else:

		name = request.POST.get('newCategoryName').strip()

		alias = name.lower()
		alias = alias.replace(' ', '-')

		if (request.POST.get('newCategoryParent').strip() == 'null'):
			parent = None
			level = 1
		else:
			try:
				parent = Category.objects.get(id=request.POST.get('newCategoryParent').strip())
				level = parent.level + 1
			except Category.DoesNotExist:
				return HttpResponse(status=418)

		category = Category(name=name, alias=alias, parent=parent, level=level, order=0, path='', created=datetime.now(), modified=datetime.now())
		category.save()

		if (parent == None):
			category.path = '/' + str(category.id) + '/'
		else:
			category.path = parent.path + str(category.id) + '/'

		category.order = Category.objects.filter(parent=category.parent).aggregate(Max('order'))['order__max'] + 1

		category.save()

		if (parent == None):
			parentId = 'none'
		else:
			parentId = parent.id

		result = {'status': 'success', 'message': 'Категория ' + name + ' добавлена.', 'categoryId': category.id, 'categoryName': category.name, 'categoryAlias': category.alias, 'parentId': parentId}

	# Возвращаем ответ
	return HttpResponse(simplejson.dumps(result), 'application/javascript')

# Switch Vendor State
def ajaxSwitchVendorState(request):

	# Импортируем
	from catalog.models import Vendor
	from datetime import datetime
	from django.utils import simplejson

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# TODO Проверяем корректность вводных данных
	if (request.POST.get('id') == '') or (request.POST.get('state') == ''):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			vendor = Vendor.objects.get(id=request.POST.get('id'))
			if request.POST.get('state') == 'true':
				vendor.state = True;
			else:
				vendor.state = False;
			vendor.save();
			result = {'status': 'success', 'message': 'Статус производителя ' + vendor.name + ' изменен на ' + str(vendor.state) + '.'}
		except Vendor.DoesNotExist:
			result = {'status': 'alert', 'message': 'Производитель с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(simplejson.dumps(result), 'application/javascript')


# Switch Category State
def ajaxSwitchCategoryState(request):

	# Импортируем
	from catalog.models import Category
	from datetime import datetime
	from django.utils import simplejson

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# TODO Проверяем корректность вводных данных
	if (request.POST.get('id') == '') or (request.POST.get('state') == ''):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			category = Category.objects.get(id=request.POST.get('id'))
			if request.POST.get('state') == 'true':
				category.state = True;
			else:
				category.state = False;
			category.save();
			result = {'status': 'success', 'message': 'Статус категории ' + category.name + ' изменен на ' + str(category.state) + '.'}
		except Category.DoesNotExist:
			result = {'status': 'alert', 'message': 'Категория с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(simplejson.dumps(result), 'application/javascript')
