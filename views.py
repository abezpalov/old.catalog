from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader


# Каталог (главная)
def index(request):
    return HttpResponse("Hello, world.")


# Список продуктов
def products(request):

	# Импортируем
	from catalog.models import Product

	# Получаем список
	products = Product.objects.all()

	for product in products:
		product.name = product.name.replace(",", ",&shy;")

	context = {'products': products}
	return render(request, 'catalog/products.html', context)


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
	from datetime import datetime
	Updater = __import__('catalog.updaters.' + alias, fromlist=['Runner'])
	runner = Updater.Runner()
	if runner.updater.state:
		if runner.run():
			runner.updater.updated = datetime.now()
			runner.updater.save()

	context = {'update_name': runner.name, 'update_message': runner.message}
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

	# Получаем дерево категорий
	categories = []
	categories = getCategoryTree(categories)

	# Корректируем имена с учетом вложеннот
	for category in categories:
		category.name = '— ' * category.level + category.name


	context = {'categories': categories}
	return render(request, 'catalog/categories.html', context)


# Дерево категорий (используется рекурсия)
def getCategoryTree(tree, parent=None):

	# Импортируем
	from catalog.models import Category

	# Получаем список дочерних категорий
	categories = Category.objects.filter(parent=parent).order_by('order')

	# Проходим по списку категорий с рекурсивным погружением
	for category in categories:
		tree.append(category)
		tree = getCategoryTree(tree, category)

	# Возвращаем результат
	return tree


# Категория
def category(request, category_id):

	# Импортируем
	from catalog.models import Category

	# Получаем список
	category = Category.objects.get(id=category_id)
	context = {'category': category}
	return render(request, 'catalog/category.html', context)

# Список синонимов производителей
def vendorsynonyms(request, updater_selected='all', distributor_selected='all', vendor_selected='all'):

	# Импортируем
	from catalog.models import VendorSynonym, Vendor, Updater, Distributor

	# Получаем список объектов синонимов
	synonyms = VendorSynonym.objects.all().order_by('name')
	if (updater_selected != 'all'):
		synonyms = synonyms.filter(updater=updater_selected)
		updater_selected = int(updater_selected)
	if (distributor_selected != 'all'):
		synonyms = synonyms.filter(distributor=distributor_selected)
		distributor_selected = int(distributor_selected)
	if (vendor_selected != 'all' and vendor_selected != 'null'):
		synonyms = synonyms.filter(vendor=vendor_selected)
		vendor_selected = int(vendor_selected)
	if (vendor_selected == 'null'):
		synonyms = synonyms.filter(vendor=None)

	# Получаем дополнительные списки объектов
	updaters = Updater.objects.all().order_by('name')
	distributors = Distributor.objects.all().order_by('name')
	vendors = Vendor.objects.all().order_by('name')

	context = {
		'updater_selected': updater_selected,
		'distributor_selected': distributor_selected,
		'vendor_selected': vendor_selected,
		'synonyms': synonyms,
		'updaters': updaters,
		'distributors': distributors,
		'vendors': vendors,
	}
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
def categorysynonyms(request, updater_selected='all', distributor_selected='all', category_selected='all'):

	# Импортируем
	from catalog.models import CategorySynonym, Category, Updater, Distributor

	# Получаем список объектов синонимов
	synonyms = CategorySynonym.objects.all().order_by('name')
	if (updater_selected != 'all'):
		synonyms = synonyms.filter(updater=updater_selected)
		updater_selected = int(updater_selected)
	if (distributor_selected != 'all'):
		synonyms = synonyms.filter(distributor=distributor_selected)
		distributor_selected = int(distributor_selected)
	if (category_selected != 'all' and category_selected != 'null'):
		synonyms = synonyms.filter(category=category_selected)
		category_selected = int(category_selected)
	if (category_selected == 'null'):
		synonyms = synonyms.filter(category=None)

	# Получаем дополнительные списки объектов
	updaters = Updater.objects.all().order_by('name')
	distributors = Distributor.objects.all().order_by('name')
	categories = []
	categories = getCategoryTree(categories)

	# Корректируем имена категорий с учетом вложеннот
	for category in categories:
		category.name = '— ' * category.level + category.name

	context = {
		'updater_selected': updater_selected,
		'distributor_selected': distributor_selected,
		'category_selected': category_selected,
		'synonyms': synonyms,
		'updaters': updaters,
		'distributors': distributors,
		'categories': categories,
	}
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
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
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
	return HttpResponse(json.dumps(result), 'application/javascript')


# Add Category
def ajaxAddCategory(request):

	# Импортируем
	from catalog.models import Category
	from django.db.models import Max
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
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
			level = 0
		else:
			try:
				parent = Category.objects.get(id=request.POST.get('newCategoryParent').strip())
				level = parent.level + 1
			except Category.DoesNotExist: # Указанная родительская категория не существует
				return HttpResponse(status=406)

		category = Category(name=name, alias=alias, parent=parent, level=level, order=-1, path='', created=datetime.now(), modified=datetime.now())
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
	return HttpResponse(json.dumps(result), 'application/javascript')

# Switch Vendor State
def ajaxSwitchVendorState(request):

	# Импортируем
	from catalog.models import Vendor
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# TODO Проверяем корректность вводных данных
	if not request.POST.get('id') or not request.POST.get('state'):
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
	return HttpResponse(json.dumps(result), 'application/javascript')


# Switch Category State
def ajaxSwitchCategoryState(request):

	# Импортируем
	from catalog.models import Category
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Проверяем корректность вводных данных
	if not request.POST.get('id') or not request.POST.get('state'):
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
	return HttpResponse(json.dumps(result), 'application/javascript')


# Switch Category State
def ajaxSwitchUpdaterState(request):

	# Импортируем
	from catalog.models import Updater
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Проверяем корректность вводных данных
	if not request.POST.get('id') or not request.POST.get('state'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			updater = Updater.objects.get(id=request.POST.get('id'))
			if request.POST.get('state') == 'true':
				updater.state = True;
			else:
				updater.state = False;
			updater.save();
			result = {'status': 'success', 'message': 'Статус загрузчика ' + updater.name + ' изменен на ' + str(updater.state) + '.'}
		except Updater.DoesNotExist:
			result = {'status': 'alert', 'message': 'Загрузчик с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Link Vendor Synonym
def ajaxLinkVendorSynonym(request):

	# Импортируем
	from catalog.models import VendorSynonym, Vendor
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Проверяем корректность вводных данных
	if not request.POST.get('vendor') or not request.POST.get('synonym'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			synonym = VendorSynonym.objects.get(id=request.POST.get('synonym'))
			if request.POST.get('vendor') == 'null':
				vendor = None
				synonym.vendor = None
				synonym.save()
				result = {'status': 'success', 'message': 'Синоним ' + synonym.name + ' отвязан от производителя.'}
			else:
				vendor = Vendor.objects.get(id=request.POST.get('vendor'))
				synonym.vendor = vendor
				synonym.save()
				result = {'status': 'success', 'message': 'Синоним ' + synonym.name + ' привязан к производителю ' + vendor.name + '.'}
		except VendorSynonym.DoesNotExist:
			result = {'status': 'alert', 'message': 'Синоним с идентификатором ' + request.POST.get('synonym') + ' отсутствует в базе.'}
		except Vendor.DoesNotExist:
			result = {'status': 'alert', 'message': 'Производитель с идентификатором ' + request.POST.get('vendor') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Link Vendor Same Synonym
def ajaxLinkVendorSameSynonym(request):

	# Импортируем
	from catalog.models import VendorSynonym, Vendor
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Проверяем корректность вводных данных
	if not request.POST.get('synonym'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			synonym = VendorSynonym.objects.get(id=request.POST.get('synonym'))
			try:
				vendor = Vendor.objects.get(name=synonym.name)
			except Vendor.DoesNotExist:
				name = synonym.name
				alias = name.lower()
				alias = alias.replace(' ', '-')
				vendor = Vendor(name=name, alias=alias, created=datetime.now(), modified=datetime.now())
				vendor.save()
			synonym.vendor = vendor
			synonym.save()
			result = {'status': 'success', 'message': 'Синоним ' + synonym.name + ' привязан к одноименному производителю.'}

		except VendorSynonym.DoesNotExist:
			result = {'status': 'alert', 'message': 'Синоним с идентификатором ' + request.POST.get('synonym') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Link Category Synonym
def ajaxLinkCategorySynonym(request):

	# Импортируем
	from catalog.models import CategorySynonym, Category
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	if not request.POST.get('category') or not request.POST.get('synonym'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			synonym = CategorySynonym.objects.get(id=request.POST.get('synonym'))
			if request.POST.get('category') == 'null':
				category = None
				synonym.category = None
				synonym.save()
				result = {'status': 'success', 'message': 'Синоним ' + synonym.name + ' отвязан от категории.'}
			else:
				category = Category.objects.get(id=request.POST.get('category'))
				synonym.category = category
				synonym.save()
				result = {'status': 'success', 'message': 'Синоним ' + synonym.name + ' привязан к производителю ' + category.name + '.'}
		except CategorySynonym.DoesNotExist:
			result = {'status': 'alert', 'message': 'Синоним с идентификатором ' + request.POST.get('synonym') + ' отсутствует в базе.'}
		except Category.DoesNotExist:
			result = {'status': 'alert', 'message': 'Категория с идентификатором ' + request.POST.get('category') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Save Updater
def ajaxSaveUpdater(request):

	# Импортируем
	from catalog.models import Updater
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	if not request.POST.get('id') or not request.POST.get('name') or not request.POST.get('alias') :
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			updater = Updater.objects.get(id=request.POST.get('id'))
			updater.name = request.POST.get('name')
			updater.alias = request.POST.get('alias')
			updater.login = request.POST.get('login')
			updater.password = request.POST.get('password')
			updater.save()
			result = {'status': 'success', 'message': 'Изменения загрузчика ' + updater.name + ' сохранены.'}
		except Updater.DoesNotExist:
			result = {'status': 'alert', 'message': 'Загрузчик с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Save Category
def ajaxSaveCategory(request):

	# Импортируем
	from catalog.models import Category
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	if not request.POST.get('id') or not request.POST.get('name') or not request.POST.get('alias') :
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			category = Category.objects.get(id=request.POST.get('id'))
			category.name = request.POST.get('name')
			category.alias = request.POST.get('alias')
			if request.POST.get('description'): category.description = request.POST.get('description')
			category.save()
			result = {'status': 'success', 'message': 'Изменения категории ' + category.name + ' сохранены.'}
		except Category.DoesNotExist:
			result = {'status': 'alert', 'message': 'Категория с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Save Vendor
def ajaxSaveVendor(request):

	# Импортируем
	from catalog.models import Vendor
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	if not request.POST.get('id') or not request.POST.get('name') or not request.POST.get('alias') :
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			vendor = Vendor.objects.get(id=request.POST.get('id'))
			vendor.name = request.POST.get('name')
			vendor.alias = request.POST.get('alias')
			if request.POST.get('description'): vendor.description = request.POST.get('description')
			vendor.save()
			result = {'status': 'success', 'message': 'Изменения производителя ' + vendor.name + ' сохранены.'}
		except Vendor.DoesNotExist:
			result = {'status': 'alert', 'message': 'Производитель с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Trash Category
def ajaxTrashCategory(request):

	# Импортируем
	from catalog.models import Category
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	if not request.POST.get('id'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			category = Category.objects.get(id=request.POST.get('id'))
			category.delete()
			result = {'status': 'success', 'message': 'Категория удалена.'}
		except Category.DoesNotExist:
			result = {'status': 'alert', 'message': 'Категория с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')
