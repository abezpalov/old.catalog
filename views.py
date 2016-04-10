from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
import math


# Connector TODO


# Distributor


def distributors(request):
	"Представление: список производителей."

	# Импортируем
	from catalog.models import Distributor

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_distributor')\
	or request.user.has_perm('catalog.change_distributor')\
	or request.user.has_perm('catalog.delete_distributor'):

		# Получаем список
		distributors = Distributor.objects.all().order_by('name')

	return render(request, 'catalog/distributors.html', locals())


def ajaxSaveDistributor(request):
	"AJAX-представление: Save Distributor."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import Distributor

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	# Проверяем права доступа
	try:
		distributor = Distributor.objects.get(id = request.POST.get('distributor_id'))
		if not request.user.has_perm('catalog.change_distributor'):
			return HttpResponse(status = 403)
	except Distributor.DoesNotExist:
		distributor = Distributor()
		if not request.user.has_perm('catalog.add_distributor'):
			return HttpResponse(status = 403)
		distributor.created = timezone.now()

	# name
	if not request.POST.get('distributor_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование поставщика.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	distributor.name   = request.POST.get('distributor_name').strip()[:100]

	# alias
	if request.POST.get('distributor_alias').strip():
		distributor.alias = unidecode.unidecode(request.POST.get('distributor_alias')).strip()[:100]
	else:
		distributor.alias = unidecode.unidecode(request.POST.get('distributor_name')).strip()[:100]

	# description
	if request.POST.get('distributor_description').strip():
		distributor.description = request.POST.get('distributor_description').strip()
	else:
		distributor.description = ''

	# state
	if request.POST.get('distributor_state') == 'true':
		distributor.state = True
	else:
		distributor.state = False

	# modified
	distributor.modified = timezone.now()

	# Сохраняем
	distributor.save()

	# Возвращаем ответ
	result = {
		'status'      : 'success',
		'distributor' : distributor.getDicted(),
		'message'     : 'Поставщик {} сохранён.'.format(distributor.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


# Updater


def updaters(request):
	"Представление: список загрузчиков."

	# Импортируем
	from catalog.models import Updater

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_updater')\
	or request.user.has_perm('catalog.change_updater')\
	or request.user.has_perm('catalog.delete_updater'):

		# Получаем список
		updaters = Updater.objects.all().order_by('name')

	return render(request, 'catalog/updaters.html', locals())


def updater(request, alias):
	"Представление: загрузчик."

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_updater')\
	or request.user.has_perm('catalog.change_updater')\
	or request.user.has_perm('catalog.delete_updater'):

		# Импортируем
		from catalog.models import Updater

		# Получаем объект
		updater = Updater.objects.get(alias=alias)

	return render(request, 'catalog/updater.html', locals())


def ajaxGetUpdater(request):
	"AJAX-представление: Get Updater."

	# Импортируем
	import json
	from catalog.models import Updater

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_updater'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		updater = Updater.objects.get(id = request.POST.get('updater_id'))

		result = {
			'status':           'success',
			'message':          'Данные загрузчика получены.',
			'updater_id':       updater.id,
			'updater_name':     updater.name,
			'updater_alias':    updater.alias,
			'updater_login':    updater.login,
			'updater_password': updater.password,
			'updater_state':    updater.state}

	except Updater.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: загрузчик отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveUpdater(request):
	"AJAX-представление: Save Updater."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import Updater

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	# Проверяем права доступа
	try:
		updater = Updater.objects.get(id = request.POST.get('updater_id'))
		if not request.user.has_perm('catalog.change_updater'):
			return HttpResponse(status = 403)
	except Updater.DoesNotExist:
		updater = Updater()
		if not request.user.has_perm('catalog.add_updater'):
			return HttpResponse(status = 403)
		updater.created = timezone.now()

	# name
	if not request.POST.get('updater_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование загрузчика.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	updater.name   = request.POST.get('updater_name').strip()[:100]

	# alias
	if request.POST.get('updater_alias').strip():
		updater.alias = unidecode.unidecode(request.POST.get('updater_alias')).strip()[:100]
	else:
		updater.alias = unidecode.unidecode(request.POST.get('updater_name')).strip()[:100]

	# login
	if request.POST.get('updater_login').strip():
		updater.login = request.POST.get('updater_login').strip()
	else:
		updater.login = ''

	# password
	if request.POST.get('updater_password').strip():
		updater.password = request.POST.get('updater_password').strip()
	else:
		updater.password = ''

	# state
	if request.POST.get('updater_state') == 'true':
		updater.state = True
	else:
		updater.state = False

	# modified
	updater.modified = timezone.now()

	# Сохраняем
	updater.save()

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Загрузчик {} сохранён.'.format(updater.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSwitchUpdaterState(request):
	"AJAX-представление: Switch Updater State."

	# Импортируем
	import json
	from datetime import datetime
	from catalog.models import Updater

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_updater'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Проверяем корректность вводных данных
	if not request.POST.get('updater_id') or not request.POST.get('updater_state'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			updater = Updater.objects.get(id=request.POST.get('updater_id'))
			if request.POST.get('updater_state') == 'true':
				updater.state = True
			else:
				updater.state = False
			updater.save()
			result = {'status': 'success', 'message': 'Статус загрузчика {} изменен на {}.'.format(updater.name, updater.state)}
		except Updater.DoesNotExist:
			result = {'status': 'alert', 'message': 'Загрузчик с идентификатором {} отсутствует в базе.'.format(request.POST.get('updater_id'))}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Stock


def stocks(request):
	"Представление: список складов."

	# Импортируем
	from catalog.models import Stock

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_stock')\
	or request.user.has_perm('catalog.change_stock')\
	or request.user.has_perm('catalog.delete_stock'):

		# Получаем список
		stocks = Stock.objects.all().order_by('alias')

	return render(request, 'catalog/stocks.html', locals())


def stock(request, alias):
	"Представление: склад."

	# Импортируем
	from catalog.models import Stock

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_stock')\
	or request.user.has_perm('catalog.change_stock')\
	or request.user.has_perm('catalog.delete_stock'):

		# Получаем список
		stock = Stock.objects.get(alias=alias)

	return render(request, 'catalog/stock.html', locals())


def ajaxGetStock(request):
	"AJAX-представление: Get Stock."

	# Импортируем
	import json
	from catalog.models import Stock

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_stock'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		stock = Stock.objects.get(id = request.POST.get('stock_id'))

		result = {
			'status':                  'success',
			'message':                 'Данные загрузчика получены.',
			'stock_id':                stock.id,
			'stock_name':              stock.name,
			'stock_alias':             stock.alias,
			'stock_delivery_time_min': stock.delivery_time_min,
			'stock_delivery_time_max': stock.delivery_time_max,
			'stock_state':             stock.state}

	except Stock.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: склад отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveStock(request):
	"AJAX-представление: Save Stock."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import Stock

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	# Проверяем права доступа
	try:
		stock = Stock.objects.get(id = request.POST.get('stock_id'))
		if not request.user.has_perm('catalog.change_stock'):
			return HttpResponse(status = 403)
	except Stock.DoesNotExist:
		stock = Stock()
		if not request.user.has_perm('catalog.add_stock'):
			return HttpResponse(status = 403)
		stock.created = timezone.now()

	# name
	if not request.POST.get('stock_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование склада.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	stock.name   = request.POST.get('stock_name').strip()[:100]

	# alias
	if request.POST.get('stock_alias').strip():
		stock.alias = unidecode.unidecode(request.POST.get('stock_alias')).strip()[:100]
	else:
		stock.alias = unidecode.unidecode(request.POST.get('stock_name')).strip()[:100]

	# delivery_time_min
	if request.POST.get('stock_delivery_time_min').strip():
		stock.delivery_time_min = request.POST.get('stock_delivery_time_min').strip()
	else:
		stock.delivery_time_min = ''

	# delivery_time_max
	if request.POST.get('stock_delivery_time_max').strip():
		stock.delivery_time_max = request.POST.get('stock_delivery_time_max').strip()
	else:
		stock.delivery_time_max = ''

	# state
	if request.POST.get('stock_state') == 'true':
		stock.state = True
	else:
		stock.state = False

	# modified
	stock.modified = timezone.now()

	# Сохраняем
	stock.save()

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Склад {} сохранён.'.format(stock.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSwitchStockState(request):
	"AJAX-представление: Switch Stock State."

	# Импортируем
	import json
	from datetime import datetime
	from catalog.models import Stock

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_stock'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Проверяем корректность вводных данных
	if not request.POST.get('stock_id') or not request.POST.get('stock_state'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			stock = Stock.objects.get(id=request.POST.get('stock_id'))
			if request.POST.get('stock_state') == 'true':
				stock.state = True
			else:
				stock.state = False
			stock.save()
			result = {'status': 'success', 'message': 'Статус склада {} изменен на {}.'.format(stock.name, stock.state)}
		except Stock.DoesNotExist:
			result = {'status': 'alert', 'message': 'Склад с идентификатором {} отсутствует в базе.'.format(request.POST.get('stock_id'))}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Category


def categories(request):
	"Представление: список категорий."

	# Импортируем
	from catalog.models import Category

	# Получаем дерево категорий
	categories = []
	categories = Category.objects.getCategoryTree(categories)

	# Корректируем имена с учетом вложеннот
	for category in categories:
		category.name = '— ' * category.level + category.name

	return render(request, 'catalog/categories.html', locals())


def category(request, category_id):
	"Представление: категория."

	# Импортируем
	from catalog.models import Category

	# Получаем объект
	category = Category.objects.get(id = category_id)

	return render(request, 'catalog/category.html', locals())


def ajaxGetCategory(request):
	"AJAX-представление: Get Category."

	# Импортируем
	import json
	from catalog.models import Category

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_category'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		c = Category.objects.get(id = request.POST.get('category_id'))

		category           = {}
		category['id']     = c.id
		category['name']   = c.name
		category['alias']  = c.alias
		category['parent'] = {}
		if c.parent:
			category['parent']['id']   = c.parent.id
			category['parent']['name'] = c.parent.name
		else:
			category['parent']['id']   = None
			category['parent']['name'] = None
		category['description'] = c.description
		category['state']       = c.state

		result = {
			'status':   'success',
			'message':  'Данные загрузчика получены.',
			'category': category}

	except Category.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: категория отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveCategory(request):
	"AJAX-представление: Save Category."

	# Импортируем
	import json
	import unidecode
	from django.db.models import Max
	from django.utils import timezone
	from catalog.models import Category

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	# Проверяем права доступа
	try:
		category = Category.objects.get(id = request.POST.get('category_id'))
		if not request.user.has_perm('catalog.change_category'):
			return HttpResponse(status = 403)
		else:
			# Получаем дерево дочерних категорий
			childs = []
			childs = Category.objects.getCategoryTree(childs, category)
	except Category.DoesNotExist:
		category = Category()
		if not request.user.has_perm('catalog.add_category'):
			return HttpResponse(status = 403)
		else:
			childs = []
			category.created = timezone.now()

	# name
	if not request.POST.get('category_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование категории.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	category.name   = request.POST.get('category_name').strip()[:100]

	# alias
	if request.POST.get('category_alias').strip():
		category.alias = unidecode.unidecode(request.POST.get('category_alias')).strip()[:100]
	else:
		category.alias = unidecode.unidecode(request.POST.get('category_name')).strip()[:100]

	# description
	if request.POST.get('category_description').strip():
		category.description = request.POST.get('category_description').strip()
	else:
		category.description = ''

	# parent, level
	try:
		category.parent = Category.objects.get(id = request.POST.get('category_parent_id'))
		category.level = category.parent.level + 1
		if category.parent in childs:
			result = {
				'status': 'alert',
				'message': 'Ошибка: попытка переноса категории в саму себя.'}
			return HttpResponse(json.dumps(result), 'application/javascript')
	except Category.DoesNotExist:
		category.parent = None
		category.level = 0

	# order
	category.order = Category.objects.filter(parent=category.parent).aggregate(Max('order'))['order__max']
	if category.order is None:
		category.order = 0
	else:
		category.order += 1

	# path
	if category.parent:
		category.path = "{}{}/".format(category.parent.path, category.id)
	else:
		category.path = "/{}/".format(category.id)

	# state
	if request.POST.get('category_state') == 'true':
		category.state = True
	else:
		category.state = False

	# modified
	category.modified = timezone.now()

	# Сохраняем
	category.save()

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Категория {} сохранена.'.format(category.name)}

	# Проводим общую нумерацию категорий
	categories = []
	categories = Category.objects.getCategoryTree(categories)
	for order, category in enumerate(categories):
		category.order = order
		category.save()

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxDeleteCategory(request):
	"AJAX-представление: Delete Category."

	# Импортируем
	import json
	from catalog.models import Category

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.delete_category'):
		return HttpResponse(status = 403)

	# Получаем категорию
	try:
		category = Category.objects.get(id = request.POST.get('category_id'))
		category.delete()
		result = {'status': 'success', 'message': 'Категория удалена.'}
	except Category.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: категория отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSwitchCategoryState(request):
	"AJAX-представление: Switch Category State."

	# Импортируем
	import json
	from datetime import datetime
	from catalog.models import Category

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_category'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Проверяем корректность вводных данных
	if not request.POST.get('category_id') or not request.POST.get('category_state'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			category = Category.objects.get(id=request.POST.get('category_id'))
			if request.POST.get('category_state') == 'true':
				category.state = True
			else:
				category.state = False
			category.save()
			result = {'status': 'success', 'message': 'Статус категории {} изменен на {}.'.format(category.name, category.state)}
		except Category.DoesNotExist:
			result = {'status': 'alert', 'message': 'Категория с идентификатором {} отсутствует в базе.'.format(request.POST.get('category_id'))}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Vendor


def vendors(request):
	"Представление: список производителей."

	# Импортируем
	from catalog.models import Vendor

	# Получаем список
	vendors = Vendor.objects.all().order_by('name')

	return render(request, 'catalog/vendors.html', locals())


def vendor(request, alias):
	"Представление: производитель."

	# Импортируем
	from catalog.models import Vendor

	# Получаем объект
	vendor = Vendor.objects.get(alias=alias)

	return render(request, 'catalog/vendor.html', locals())


def ajaxGetVendor(request):
	"AJAX-представление: Get Vendor."

	# Импортируем
	import json
	from catalog.models import Vendor

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_vendor'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		vendor = Vendor.objects.get(id = request.POST.get('vendor_id'))

		result = {
			'status':             'success',
			'message':            'Данные производителя получены.',
			'vendor_id':          vendor.id,
			'vendor_name':        vendor.name,
			'vendor_alias':       vendor.alias,
			'vendor_description': vendor.description,
			'vendor_state':       vendor.state}

	except Vendor.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: производитель отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveVendor(request):
	"AJAX-представление: Save Vendor."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import Vendor

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	# Проверяем права доступа
	try:
		vendor = Vendor.objects.get(id = request.POST.get('vendor_id'))
		if not request.user.has_perm('catalog.change_vendor'):
			return HttpResponse(status = 403)
	except Vendor.DoesNotExist:
		vendor = Vendor()
		if not request.user.has_perm('catalog.add_vendor'):
			return HttpResponse(status = 403)
		vendor.created = timezone.now()

	# name
	if not request.POST.get('vendor_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование производителя.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	vendor.name = request.POST.get('vendor_name').strip()[:100]

	# alias
	if request.POST.get('vendor_alias').strip():
		vendor.alias = unidecode.unidecode(request.POST.get('vendor_alias')).lower().strip()[:100]
	else:
		vendor.alias = unidecode.unidecode(request.POST.get('vendor_name')).lower().strip()[:100]

	# description
	if request.POST.get('vendor_description').strip():
		vendor.description = request.POST.get('vendor_description').strip()
	else:
		vendor.description = ''

	# state
	if request.POST.get('vendor_state') == 'true':
		vendor.state = True
	else:
		vendor.state = False

	# modified
	vendor.modified = timezone.now()

	# Сохраняем
	try:
		vendor.save()
	except:
		result = {
			'status': 'alert',
			'message': 'Ошибка: вероятно, производитель уже есть в базе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
		

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Производитель {} сохранён.'.format(vendor.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSwitchVendorState(request):
	"AJAX-представление: Switch Vendor State."

	# Импортируем
	import json
	from datetime import datetime
	from catalog.models import Vendor

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_vendor'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Проверяем корректность вводных данных
	if not request.POST.get('vendor_id') or not request.POST.get('vendor_state'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			vendor = Vendor.objects.get(id = request.POST.get('vendor_id'))
			if request.POST.get('vendor_state') == 'true':
				vendor.state = True
			else:
				vendor.state = False
			vendor.save()
			result = {'status': 'success', 'message': 'Статус производителя {} изменен на {}.'.format(vendor.name, vendor.state)}
		except Vendor.DoesNotExist:
			result = {'status': 'alert', 'message': 'Производитель с идентификатором {} отсутствует в базе.'.format(request.POST.get('vendor_id'))}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Unit


# TODO


# Price Types


def priceTypes(request):
	"Представление: список типов цен."

	# Импортируем
	from catalog.models import PriceType

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_pricetype')\
	or request.user.has_perm('catalog.change_pricetype')\
	or request.user.has_perm('catalog.delete_pricetype'):

		# Получаем список
		price_types = PriceType.objects.all().order_by('name')

	return render(request, 'catalog/pricetypes.html', locals())


def priceType(request, alias):
	"Представление: тип цены."

	# Импортируем
	from catalog.models import PriceType

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_pricetype')\
	or request.user.has_perm('catalog.change_pricetype')\
	or request.user.has_perm('catalog.delete_pricetype'):

		# Получаем объект
		price_type = Vendor.objects.get(alias=alias)

	return render(request, 'catalog/pricetype.html', locals())


def ajaxGetPriceType(request):
	"AJAX-представление: Get Price Type."

	# Импортируем
	import json
	from catalog.models import PriceType

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_pricetype'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		price_type = PriceType.objects.get(id = request.POST.get('price_type_id'))

		result = {
			'status':                'success',
			'message':               'Данные типа цены получены.',
			'price_type_id':         price_type.id,
			'price_type_name':       price_type.name,
			'price_type_alias':      price_type.alias,
			'price_type_multiplier': str(price_type.multiplier),
			'price_type_state':      price_type.state}

	except PriceType.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: тип цены отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSavePriceType(request):
	"AJAX-представление: Save Price Type."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import PriceType

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	try:
		price_type = PriceType.objects.get(id = request.POST.get('price_type_id'))
		if not request.user.has_perm('catalog.change_pricetype'):
			return HttpResponse(status = 403)
	except PriceType.DoesNotExist:
		price_type = PriceType()
		if not request.user.has_perm('catalog.add_pricetype'):
			return HttpResponse(status = 403)
		price_type.created = timezone.now()

	# name
	if not request.POST.get('price_type_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование типа цены.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	price_type.name   = request.POST.get('price_type_name').strip()[:100]

	# alias
	if request.POST.get('price_type_alias').strip():
		price_type.alias = unidecode.unidecode(request.POST.get('price_type_alias')).strip()[:100]
	else:
		price_type.alias = unidecode.unidecode(request.POST.get('price_type_name')).strip()[:100]

	# multiplier
	try:
		multiplier = request.POST.get('price_type_multiplier').strip()
		multiplier = multiplier.replace(',', '.')
		multiplier = multiplier.replace(' ', '')
		price_type.multiplier = float(multiplier)
	except:
		result = {
			'status': 'alert',
			'message': 'Ошибка: недопустимое значение множителя.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# state
	if request.POST.get('price_type_state') == 'true':
		price_type.state = True
	else:
		price_type.state = False

	# modified
	price_type.modified = timezone.now()

	# Сохраняем
	price_type.save()

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Тип цены {} сохранён.'.format(price_type.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSwitchPriceTypeState(request):
	"AJAX-представление: Switch Price Type State."

	# Импортируем
	import json
	from datetime import datetime
	from catalog.models import PriceType

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_pricetype'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Проверяем корректность вводных данных
	if not request.POST.get('price_type_id') or not request.POST.get('price_type_state'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			price_type = PriceType.objects.get(id=request.POST.get('price_type_id'))
			if request.POST.get('price_type_state') == 'true':
				price_type.state = True
			else:
				price_type.state = False
			price_type.save()
			result = {'status': 'success', 'message': 'Статус типа цены {} изменен на {}.'.format(price_type.name, price_type.state)}
		except PriceType.DoesNotExist:
			result = {'status': 'alert', 'message': 'Тип цены с идентификатором {} отсутствует в базе.'.format(request.POST.get('price_type_id'))}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Currency


def currencies(request):
	"Представление: список валют."

	# Импортируем
	from catalog.models import Currency

	# Получаем список
	currencies = Currency.objects.all()

	return render(request, 'catalog/currencies.html', locals())


def currency(request, alias):
	"Представление: тип цены."

	# Импортируем
	from catalog.models import Currency

	# Получаем объект
	currency = Currency.objects.get(alias=alias)

	return render(request, 'catalog/currency.html', locals())


def ajaxGetCurrency(request):
	"AJAX-представление: Get Currency."

	# Импортируем
	import json
	from catalog.models import Currency

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_currency')\
	or not request.user.has_perm('catalog.delete_currency'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		c = Currency.objects.get(id = request.POST.get('currency_id'))

		currency              = {}
		currency['id']        = c.id
		currency['name']      = c.name
		currency['full_name'] = c.full_name
		currency['alias']     = c.alias
		currency['rate']      = str(c.rate)
		currency['quantity']  = str(c.quantity)
		currency['state']     = c.state

		result = {
			'status':   'success',
			'message':  'Данные валюты получены.',
			'currency': currency}

	except Currency.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: валюта отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveCurrency(request):
	"AJAX-представление: Save Currency."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import Currency

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	try:
		currency = Currency.objects.get(id = request.POST.get('currency_id'))
		if not request.user.has_perm('catalog.change_currency'):
			return HttpResponse(status = 403)
	except Currency.DoesNotExist:
		currency = Currency()
		if not request.user.has_perm('catalog.add_currency'):
			return HttpResponse(status = 403)
		currency.created = timezone.now()

	# name
	if not request.POST.get('currency_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	currency.name   = request.POST.get('currency_name').strip()[:100]

	# full name
	if not request.POST.get('currency_full_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует полное наименование.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	currency.full_name   = request.POST.get('currency_full_name').strip()[:100]

	# alias
	if request.POST.get('currency_alias').strip():
		currency.alias = unidecode.unidecode(request.POST.get('currency_alias')).strip()[:100]
	else:
		currency.alias = unidecode.unidecode(request.POST.get('currency_full_name')).strip()[:100]

	# rate
	try:
		rate = request.POST.get('currency_rate').strip()
		rate = rate.replace(',', '.')
		rate = rate.replace(' ', '')
		currency.rate = float(rate)
	except:
		result = {
			'status': 'alert',
			'message': 'Ошибка: недопустимое значение курса валюты.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# quantity
	try:
		quantity = request.POST.get('currency_quantity').strip()
		quantity = quantity.replace(',', '.')
		quantity = quantity.replace(' ', '')
		currency.quantity = float(quantity)
	except:
		result = {
			'status': 'alert',
			'message': 'Ошибка: недопустимое значение количества валюты.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# state
	if request.POST.get('currency_state') == 'true':
		currency.state = True
	else:
		currency.state = False

	# modified
	currency.modified = timezone.now()

	# Сохраняем
	currency.save()

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Валюта {} сохранена.'.format(currency.full_name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSwitchCurrencyState(request):
	"AJAX-представление: Switch Currency State."

	# Импортируем
	import json
	from datetime import datetime
	from catalog.models import Currency

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_currency'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Проверяем корректность вводных данных
	if not request.POST.get('currency_id') or not request.POST.get('currency_state'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			currency = Currency.objects.get(id = request.POST.get('currency_id'))
			if request.POST.get('currency_state') == 'true':
				currency.state = True
			else:
				currency.state = False
			currency.save()
			result = {'status': 'success', 'message': 'Статус валюты {} изменен на {}.'.format(currency.name, currency.state)}
		except Currency.DoesNotExist:
			result = {'status': 'alert', 'message': 'Валюта с идентификатором {} отсутствует в базе.'.format(request.POST.get('currency_id'))}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Price


# TODO


# Quantity


# TODO


# Product


def products(request, search=None, vendor=None, category=None, childs=None, page=None):
	"Представление: список продуктов."

	# Импортируем
	from lxml import etree
	from django.db.models import Q
	from catalog.models import Product
	from catalog.models import Category
	from catalog.models import Vendor

	# Инициализируем переменные
	items_on_page = 100
	if not page: page = 1
	page = int(page)

	categories = []
	product_categories = []
	products = []
	pages = []

	# Получаем список всех имеющихся категорий
	categories = Category.objects.getCategoryTree(categories)

	# Корректируем имена категорий с учетом вложенноти
	for c in categories:
		c.name = '— ' * c.level + c.name

	root = etree.Element("div")
	Category.objects.getCategoryHTMLTree(root, None, True)
	categories_ul = etree.tostring(root)

	# Получаем список всех имеющихся производителей
	vendors = Vendor.objects.filter(state=True)

	# Получаем список категорий, из которых выводить товар
	if category and childs == 'y': # Указанная категория и все потомки
		category = Category.objects.get(id=category)
		product_categories.append(category)
		product_categories = Category.objects.getCategoryTree(product_categories, category)
	elif category and childs == 'n': # Только указанная категория
		category = Category.objects.get(id=category)
		product_categories.append(category)
	else: # Все категории
		category = None
		product_categories = categories
		product_categories.append(None)

	# Получаем объект производителя, чей товар необходимо показать
	if vendor: vendor = Vendor.objects.get(alias=vendor)

	# TODO Разбиваем строку поиска на слова
	if search:
		words = search.split(' ')

	# Получаем список продуктов, которые необходимо показать
	# Если есть параметры запроса
	if search or category or vendor:
		for product_category in product_categories:
			if search and vendor:
				for n, word in enumerate(words):
					if not n:
						new_products = Product.objects.filter(Q(article__icontains=word) | Q(name__icontains=word)).filter(vendor=vendor).filter(category=product_category).filter(state=True)
					else:
						new_products = new_products.filter(Q(article__icontains=word) | Q(name__icontains=word)).filter(vendor=vendor).filter(category=product_category).filter(state=True)
			elif search:
				for n, word in enumerate(words):
					if not n:
						new_products = Product.objects.filter(Q(article__icontains=word) | Q(name__icontains=word)).filter(category=product_category).filter(state=True)
					else:
						new_products = new_products.filter(Q(article__icontains=word) | Q(name__icontains=word)).filter(category=product_category).filter(state=True)
			elif vendor:
				new_products = Product.objects.filter(vendor=vendor).filter(category=product_category).filter(state=True)
			else:
				new_products = Product.objects.filter(category=product_category).filter(state=True)
			products.extend(new_products)
	else:
		# TODO Что показывать когда нечего показывать?
		think = True

	# Нумеруем элементы списка
	for n, product in enumerate(products):
		product.n = n + 1

	# Разбиваем на страницы
	if len(products) > items_on_page:

		# Формируем базовый URL
		url = '/catalog/products/'
		if category: url = "{}c/{}-{}/".format(url, category.id, childs)
		if vendor:   url = "{}{}/".format(url, vendor.alias)
		if search:   url = "{}search/{}/".format(url, search)

		# Формируем список номеров страниц для ссылок
		page_max = len(products) // items_on_page
		if len(products) % items_on_page:
			page_max += 1

		for n in range(1, page_max + 1):
			if n < 4 or n-3 < page < n+3 or n > page_max - 3:
				pages.append(n)
			elif (n == 4 or n == page_max - 4) and pages[len(pages)-1]:
				pages.append(0)

		# TODO Вторая версия пейджинга


		# Определяем номера предыдущих и последующих страниц
		page_prev = page - 1
		if page == page_max:
			page_next = 0
		else:
			page_next = page + 1

		products = products[(page - 1) * items_on_page : page * items_on_page]

	return render(request, 'catalog/products.html', locals())


def product(request, id=None, vendor=None, article=None):
	"Представление: продукт."

	# Импортируем
	from catalog.models import Vendor, Product

	# Получаем объект продукта
	if id:
		product = Product.objects.get(id=id)
	elif vendor and article:
		vendor = Vendor.objects.get(alias=vendor)
		product = Product.objects.get(vendor=vendor, article=article)

	return render(request, 'catalog/product.html', locals())


def ajaxGetProduct(request):
	"AJAX-представление: Get Product."

	# Импортируемa
	import json
	from catalog.models import Product

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_distributor'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		product = Product.objects.get(id = request.POST.get('product_id'))

		if product.category: product_category_id = product.category.id
		else: product_category_id = '0'
		if product.unit: product_unit_id = product.unit.id
		else: product_unit_id = '0'
		if product.duble: product_duble_id = product.duble.id
		else: product_duble_id = ''

		result = {
			'status':              'success',
			'message':             'Данные продукта получены.',
			'product_id':          product.id,
			'product_name':        product.name,
			'product_article':     product.article,
			'product_vendor_id':   product.vendor.id,
			'product_category_id': product_category_id,
			'product_unit_id':     product_unit_id,
			'product_description': product.description,
			'product_duble_id':    product_duble_id,
			'product_state':       product.state}

	except Product.DoesNotExist:
		result = {
			'status':  'alert',
			'message': 'Ошибка: товар отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveProduct(request):
	"AJAX-представление: Save Product."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import Product, Vendor, Category

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	try:
		product = Product.objects.get(id = request.POST.get('product_id'))
		if not request.user.has_perm('catalog.change_product'):
			return HttpResponse(status = 403)
	except Product.DoesNotExist:
		product = Product()
		if not request.user.has_perm('catalog.add_product'):
			return HttpResponse(status = 403)
		product.created = timezone.now()

	# name
	if not request.POST.get('product_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	product.name      = request.POST.get('product_name').strip()[:500]
	product.full_name = request.POST.get('product_name').strip()

	# article
	if not request.POST.get('product_article').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует артикул.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	product.article = request.POST.get('product_article').strip()[:100]

	# vendor
	try:
		product.vendor = Vendor.objects.get(id = request.POST.get('product_vendor_id'))
	except Vendor.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: неверный производитель.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# category
	try:
		product.category = Category.objects.get(id = request.POST.get('product_category_id'))
	except Category.DoesNotExist:
		product.category = None

	# description
	if request.POST.get('product_description').strip():
		product.description = request.POST.get('product_description').strip()
	else:
		product.description = ''

	# duble
	try:
		product.duble = Product.objects.get(id = request.POST.get('product_duble_id'))
	except:
		product.duble = None

	# state
	if request.POST.get('product_state') == 'true':
		product.state = True
	else:
		product.state = False

	# edited
	product.edited = True

	# modified
	product.modified = timezone.now()

	# Сохраняем
	product.save()

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Продукт {} {} сохранён.'.format(product.vendor.name, product.article)}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Party


def ajaxGetParties(request):
	"AJAX-представление: Get Parties."

	# Импортируем
	from catalog.models import Product, Party
	import json

	# Инициализируем переменные
	items = []

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	if not request.POST.get('product_id'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			product = Product.objects.get(id = request.POST.get('product_id'))

			parties = Party.objects.filter(product=product)

			# TODO Проверяем права доступа
			if request.user.id:

				access = True

				for party in parties:

					item = {}
					item['id']                = str(party.id)
					item['stock']             = str(party.stock.name)
					item['delivery_time_min'] = str(party.stock.delivery_time_min)
					item['delivery_time_max'] = str(party.stock.delivery_time_max)
					item['price']             = str(party.price_str)
					item['price_out']         = str(party.price_out_str)
					if -1 == party.quantity:
						item['quantity'] = 'неограничено'
					elif 0 == party.quantity:
						item['quantity'] = '0'
					elif party.quantity is None:
						item['quantity'] = 'неизвестно'
					else:
						item['quantity'] = "{}&nbsp;{}".format(party.quantity, party.unit.name)
					items.append(item)

			else:

				access = False

				for party in parties:

					item = {}
					item['id']                = str(party.id)
					item['delivery_time_min'] = str(party.stock.delivery_time_min)
					item['delivery_time_max'] = str(party.stock.delivery_time_max)
					item['price_out']         = str(party.price_out_str)
					if -1 == party.quantity:
						item['quantity'] = 'неограничено'
					elif 0 == party.quantity:
						item['quantity'] = '0'
					elif party.quantity is None:
						item['quantity'] = 'неизвестно'
					else:
						item['quantity'] = "{}&nbsp;{}".format(party.quantity, party.unit.name)
					items.append(item)

			item = {}

			item['product_id']      = product.id
			item['product_article'] = product.article
			item['product_name']    = product.name
			item['vendor_name']     = product.vendor.name

			result = {
				'status': 'success',
				'message': 'Данные партий получены. Количество партий {}'.format(len(parties)),
				'len': len(parties),
				'items': items,
				'product': item,
				'access': access}
		except Product.DoesNotExist:
			result = {
				'status': 'alert',
				'message': 'Продукт с идентификатором {} отсутствует в базе.'.format(request.POST.get('id'))}

	# Переводим результат в формат JSON
	result = json.dumps(result)

	# Возвращаем ответ
	return HttpResponse(result, 'application/javascript')


# Party Hystory


# TODO


# Price Hystory


# TODO


# Quantity Hystory


# TODO


# Quantity Hystory


# TODO


# Parameter Type


# TODO


def parameterTypes(request):
	"Представление: список типов данных параметров."

	# Импортируем
	from catalog.models import ParameterType

	# Получаем список
	parameter_types = ParameterType.objects.all().order_by('name')

	return render(request, 'catalog/parametertypes.html', locals())


def parameterType(request, alias):
	"Представление: тип данных параметров."

	# Импортируем
	from catalog.models import ParameterType

	# Получаем объект
	parameter_type = ParameterType.objects.get(alias=alias)

	return render(request, 'catalog/parametertype.html', locals())


def ajaxGetParameterType(request):
	"AJAX-представление: Get Parameter Type."

	# Импортируем
	import json
	from catalog.models import ParameterType

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_parameter_type'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		parameter_type = ParameterType.objects.get(id = request.POST.get('parameter_type_id'))

	except ParameterType.DoesNotExist:
		result = {
			'status'  : 'alert',
			'message' : 'Ошибка: параметр отсутствует в базе.'}

	else:

		parameter_type = {
			'id'             : parameter_type.id,
			'name'           : parameter_type.name,
			'alias'          : parameter_type.alias,
			'state'          : parameter_type.state}

		result = {
			'status'         : 'success',
			'message'        : 'Данные параметра получены.',
			'parameter_type' : parameter_type}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveParameterType(request):
	"AJAX-представление: Save Parameter Type."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import ParameterType

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	# Проверяем права доступа
	try:
		parameter_type = ParameterType.objects.get(
			id = request.POST.get('parameter_type_id'))
		if not request.user.has_perm('catalog.change_parametertype'):
			return HttpResponse(status = 403)
	except ParameterType.DoesNotExist:
		parameter_type = ParameterType()
		if not request.user.has_perm('catalog.add_parametertype'):
			return HttpResponse(status = 403)
		parameter_type.created = timezone.now()

	# name
	if not request.POST.get('parameter_type_name').strip():
		result = {
			'status'  : 'alert',
			'message' : 'Ошибка: отсутствует наименование типа данных параметра.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	parameter_type.name = request.POST.get('parameter_type_name').strip()[:100]

	# alias
	if request.POST.get('parameter_type_alias').strip():
		parameter_type.alias = unidecode.unidecode(
			request.POST.get('parameter_type_alias')).lower().strip()[:100]
	else:
		parameter_type.alias = unidecode.unidecode(
			request.POST.get('parameter_type_name')).lower().strip()[:100]

	# state
	if request.POST.get('parameter_type_state') == 'true':
		parameter_type.state = True
	else:
		parameter_type.state = False

	# modified
	parameter_type.modified = timezone.now()

	# Сохраняем
	try:
		parameter_type.save()
	except:
		result = {
			'status': 'alert',
			'message': 'Ошибка: вероятно, тип данных параметров уже есть в базе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Тип данных параметров {} сохранён.'.format(parameter_type.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSwitchParameterTypeState(request):
	"AJAX-представление: Switch Parameter Type State."

	import json
	from datetime import datetime
	from catalog.models import ParameterType

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	if not request.user.has_perm('catalog.change_parametertype'):
		return HttpResponse(status=403)

	if request.POST.get('id') and request.POST.get('state'):
		try:
			parameter_type = ParameterType.objects.get(
				id = request.POST.get('id'))
			if request.POST.get('state') == 'true':
				parameter_type.state = True
			else:
				parameter_type.state = False
			parameter_type.save()
			result = {
				'status'  : 'success',
				'message' : 'Статус параметра {} изменен на {}.'.format(
					parameter_type.name,
					parameter_type.state)}
		except ParameterType.DoesNotExist:
			result = {
				'status'  : 'alert',
				'message' : 'Объект с идентификатором {} отсутствует в базе.'.format(
					request.POST.get('id'))}

	return HttpResponse(json.dumps(result), 'application/javascript')


# Parameter


def parameters(request):
	"Представление: список параметров."

	# Импортируем
	from catalog.models import Parameter, ParameterType

	# Получаем список
	parameters = Parameter.objects.all().order_by('name')
	parameter_types = ParameterType.objects.all().order_by('name')

	return render(request, 'catalog/parameters.html', locals())


def ajaxGetParameter(request):
	"AJAX-представление: Get Parameter."

	# Импортируем
	import json
	from catalog.models import Parameter

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_parameter'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		parameter = Parameter.objects.get(id = request.POST.get('parameter_id'))

	except Parameter.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: параметр отсутствует в базе.'}

	else:

		if parameter.parameter_type:
			parameter_type = {
				'id'    : parameter.parameter_type.id,
				'alias' : parameter.parameter_type.alias,
				'name'  : parameter.parameter_type.name}

		else:
			parameter_type = {
				'id' : 0}

		parameter = {
			'id'             : parameter.id,
			'name'           : parameter.name,
			'alias'          : parameter.alias,
			'parameter_type' : parameter_type,
			'order'          : parameter.order,
			'state'          : parameter.state}

		result = {
			'status'    : 'success',
			'message'   : 'Данные параметра получены.',
			'parameter' : parameter}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveParameter(request):
	"AJAX-представление: Save Parameter."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import Parameter, ParameterType

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	# Проверяем права доступа
	try:
		parameter = Parameter.objects.get(id = request.POST.get('parameter_id'))
		if not request.user.has_perm('catalog.change_parameter'):
			return HttpResponse(status = 403)
	except Parameter.DoesNotExist:
		parameter = Parameter()
		if not request.user.has_perm('catalog.add_parameter'):
			return HttpResponse(status = 403)
		parameter.created = timezone.now()

	# name
	if not request.POST.get('parameter_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование параметра.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	parameter.name = request.POST.get('parameter_name').strip()[:100]

	# alias
	if request.POST.get('parameter_alias').strip():
		parameter.alias = unidecode.unidecode(
			request.POST.get('parameter_alias')).lower().strip()[:100]
	else:
		parameter.alias = unidecode.unidecode(
			request.POST.get('parameter_name')).lower().strip()[:100]

	# parameter type
	try:
		parameter.parameter_type = ParameterType.objects.get(
			id = request.POST.get('parameter_parameter_type_id').strip())
	except AttributeError:
		parameter.parameter_type = None
	except ParameterType.DoesNotExist:
		parameter.parameter_type = None

	# order
	try:
		parameter.order = int(request.POST.get('parameter_order').strip())
	except ValueError:
		parameter.order = 0

	# state
	if request.POST.get('parameter_state') == 'true':
		parameter.state = True
	else:
		parameter.state = False

	# modified
	parameter.modified = timezone.now()

	# Сохраняем
	try:
		parameter.save()
	except:
		result = {
			'status': 'alert',
			'message': 'Ошибка: вероятно, параметр уже есть в базе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Параметр {} сохранён.'.format(parameter.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSwitchParameterState(request):
	"AJAX-представление: Switch Parameter State."

	import json
	from datetime import datetime
	from catalog.models import Parameter

	model = Parameter
	model_name = 'parameter'

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)


	if not request.user.has_perm('catalog.change_{}'.format(model_name)):
		return HttpResponse(status=403)

	# Получаем объект
	try:
		o = model.objects.get(id = request.POST.get('id'))

	except model.DoesNotExist:
		result = {
			'status'  : 'alert',
			'message' : 'Объект с идентификатором {} отсутствует в базе.'.format(
				request.POST.get('id'))}
		return HttpResponse(json.dumps(result), 'application/javascript')

	else:
		if request.POST.get('state') == 'true':
			o.state = True
		else:
			o.state = False
		o.save()

		result = {'status' : 'success'}

	return HttpResponse(json.dumps(result), 'application/javascript')


# Parameter Value


def parameterValues(request):
	"Представление: список значений параметров."

	# Импортируем
	from catalog.models import ParameterValue

	# Получаем список
	parameter_values = ParameterValue.objects.all()

	return render(request, 'catalog/parameter-values.html', locals())


def ajaxGetParameterValue(request):
	"AJAX-представление: Get Parameter Value."

	# Импортируем
	import json
	from catalog.models import ParameterValue, Parameter

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_parametervalue'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		parameter_value = ParameterValue.objects.get(
			id = request.POST.get('parameter_value_id'))

	except ParameterValue.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: значение параметра отсутствует в базе.'}

	else:

		parameter_value = {
			'id'             : parameter_value.id,
			'value_text'     : parameter_value.value_text,
			'value_search'   : parameter_value.value_search,
			'order'          : parameter_value.order,
			'state'          : parameter_value.state,
			'parameter'      : {
				'id'             : parameter_value.parameter.id,
				'name'           : parameter_value.parameter.name,
				'alias'          : parameter_value.parameter.alias,
				'parameter_type' : parameter_value.parameter_type,
				'order'          : parameter_value.parameter.order,
				'state'          : parameter_value.parameter.state}}

		result = {
			'status'          : 'success',
			'message'         : 'Данные значения параметра получены.',
			'parameter_value' : parameter_value}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveParameterValue(request):
	"AJAX-представление: Save Parameter Value."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import ParameterValue

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	# Проверяем права доступа
	try:
		parameter_value = ParameterValue.objects.get(
			id = request.POST.get('parameter_value_id'))
		if not request.user.has_perm('catalog.change_parametervalue'):
			return HttpResponse(status = 403)
	except ParameterValue.DoesNotExist:
		parameter_value = ParameterValue()
		if not request.user.has_perm('catalog.add_parametervalue'):
			return HttpResponse(status = 403)
		parameter_value.created = timezone.now()

	#parameter
	try:
		parameter_value.parameter = Parameter.objects.get(
			id = request.POST.get('parameter_value_parameter'))
	except:
		result = {
			'status'  : 'alert',
			'message' : 'Ошибка: не выбран параметр.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# value text
	parameter_value.value_text   = request.POST.get('parameter_value_value_text').strip()

	# value search
	parameter_value.value_search = request.POST.get('parameter_value_valuetext').strip()[:100]

	# order
	try:
		parameter_value.order = int(request.POST.get('parameter_value_order').strip())
	except ValueError:
		parameter_value.order = 0

	# state
	if request.POST.get('parameter_value_state') == 'true':
		parameter_value.state = True
	else:
		parameter_value.state = False

	# modified
	parameter_value.modified = timezone.now()

	# Сохраняем
	try:
		parameter_value.save()
	except:
		result = {
			'status'  : 'alert',
			'message' : 'Неизвестная ошибка.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Значение {} параметра {} сохранёно.'.format(
				parameter_value.value_text,
				parameter_value.parameter.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


# Parameter Value Synonym


def parametervaluesynonyms(request, updater_selected = 'all', distributor_selected = 'all', parameter_selected = 'all'):
	"Представление: список синонимов значений параметров."

	# Импортируем
	from catalog.models import ParameterValueSynonym, Parameter, Updater, Distributor

	# Преобразуем типы данных
	if updater_selected     != 'all': updater_selected     = int(updater_selected)
	if distributor_selected != 'all': distributor_selected = int(distributor_selected)
	if parameter_selected   != 'all': parameter_selected   = int(parameter_selected)

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_parametervaluesynonym')\
	or request.user.has_perm('catalog.change_parametervaluesynonym')\
	or request.user.has_perm('catalog.delete_parametervaluesynonym'):

		# Получаем список объектов синонимов
		parameter_value_synonyms = ParameterValueSynonym.objects.select_related().all()

		if updater_selected and updater_selected != 'all':
			parameter_value_synonyms = parameter_value_synonyms.select_related().filter(
				updater = updater_selected)
		if not updater_selected:
			parameter_value_synonyms = parameter_value_synonyms.select_related().filter(
				updater = None)

		if distributor_selected and distributor_selected != 'all':
			parameter_value_synonyms = parameter_value_synonyms.select_related().filter(
				distributor = distributor_selected)
		if not distributor_selected:
			parameter_value_synonyms = parameter_value_synonyms.select_related().filter(
				distributor = None)

		if parameter_selected and parameter_selected != 'all':
			parameter_value_synonyms = parameter_value_synonyms.select_related().filter(
				parameter = parameter_selected)
		if not parameter_selected:
			parameter_value_synonyms = parameter_value_synonyms.select_related().filter(
				parameter = None)

		# Получаем дополнительные списки объектов
		updaters     = Updater.objects.select_related().all()
		distributors = Distributor.objects.select_related().all()
		parameters   = Parameter.objects.select_related().all()

	return render(request, 'catalog/parametervaluesynonyms.html', locals())


def ajaxSaveParameterValueSynonym(request):
	"AJAX-представление: Save Parameter Value Synonym."

	# Импортируем
	import json
	from django.utils import timezone
	from catalog.models import ParameterValueSynonym, Updater, Distributor, Parameter, ParameterValue

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	try:
		parameter_value_synonym = ParameterValueSynonym.objects.get(
			id = request.POST.get('parameter_value_synonym_id'))
		if not request.user.has_perm('catalog.change_parametervaluesynonym'):
			return HttpResponse(status = 403)
	except ParameterValueSynonym.DoesNotExist:
		parameter_value_synonym = ParameterValueSynonym()
		if not request.user.has_perm('catalog.add_parametervaluesynonym'):
			return HttpResponse(status = 403)
		parameter_value_synonym.created = timezone.now()

	# name
	if not request.POST.get('parameter_value_synonym_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	parameter_synonym.name = request.POST.get('parameter_synonym_name').strip()[:1024]

	# updater
	try:
		parameter_value_synonym.updater = Updater.objects.get(
			id = request.POST.get('parameter_value_synonym_updater_id'))
	except Updater.DoesNotExist:
		parameter_value_synonym.updater = None

	# distributor
	try:
		parameter_value_synonym.distributor = Distributor.objects.get(
			id = request.POST.get('parameter_value_synonym_distributor_id'))
	except Distributor.DoesNotExist:
		parameter_value_synonym.distributor = None

	# parameter
	try:
		parameter_value_synonym.parameter = Parameter.objects.get(
			id = request.POST.get('parameter_value_synonym_parameter_id'))
	except Parameter.DoesNotExist:
		parameter_value_synonym.parameter = None

	# parameter value
	try:
		parameter_value_synonym.parameter_value = ParameterValue.objects.get(
			id = request.POST.get('parameter_value_synonym_parameter_value_id'))
	except ParameterValue.DoesNotExist:
		parameter_value_synonym.parameter_value = None

	# modified
	parameter_value_synonym.modified = timezone.now()

	# Сохраняем
	parameter_value_synonym.save()

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Синоним {} сохранён.'.format(parameter_value_synonym.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxLinkParameterValueSynonymSameParameterValue(request):
	"AJAX-представление: Link Parameter Synonym same Parameter Value."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import ParameterSynonym, ParameterValue

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_parametervaluesynonym')\
	or not request.user.has_perm('catalog.add_parametervalue'):
		return HttpResponse(status = 403)

	# Получаем объект синонима
	try:
		parameter_value_synonym = ParameterValueSynonym.objects.get(
			id = request.POST.get('parameter_value_synonym_id'))
	except ParameterValueSynonym.DoesNotExist:
		result = {
			'status'  : 'alert',
			'message' : 'Ошибка: синоним отсутствует в базе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# name
	name = parameter_value_synonym.name

	# alias
	alias = unidecode.unidecode(name.lower())
	alias = alias.replace(' ', '-')
	alias = alias.replace('&', 'and')
	alias = alias.replace('\'', '')

	# parameter value
	try:
		parameter_value = ParameterValue.objects.get(alias = alias)
	except ParameterValue.DoesNotExist:
		parameter_value = ParameterValue()
		parameter_value.name = name
		parameter_value.alias = alias
		parameter_value.created = timezone.now()
		parameter_value.modified = timezone.now()
		parameter_value.save()

	parameter_value_synonym.parameter_value = parameter_value
	parameter_value_synonym.modified = timezone.now()
	parameter_value_synonym.save()

	parameter_values = []
	vs = ParameterValue.objects.all()
	for v in vs:
		parameter_value = {
			'id'   : v.id,
			'name' : v.name}
		parameter_values.append(parameter_value)

	parameter_value = {
		'id'   : parameter_value_synonym.parameter_value.id,
		'name' : parameter_value_synonym.parameter_value.name}

	result = {
		'status'  : 'success',
		'message' : 'Синоним {} привязан к одноименному производителю {}.'.format(
			parameter_value_synonym.name,
			parameter_value_synonym.parameter.name),
		'parameter_value'  : parameter_value,
		'parameter_values' : parameter_values}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Parameter to Category


# TODO


# Parameter to Product


# TODO


# Parameter Synonym


def parametersynonyms(request, updater_selected = 'all', distributor_selected = 'all', parameter_selected = 'all'):
	"Представление: список синонимов параметров."

	# Импортируем
	from catalog.models import ParameterSynonym, Parameter, Updater, Distributor

	# Преобразуем типы данных
	if updater_selected != 'all':
		updater_selected = int(updater_selected)
	if distributor_selected != 'all':
		distributor_selected = int(distributor_selected)
	if parameter_selected != 'all':
		parameter_selected = int(parameter_selected)

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_parametersynonym')\
	or request.user.has_perm('catalog.change_parametersynonym')\
	or request.user.has_perm('catalog.delete_parametersynonym'):

		# Получаем список объектов синонимов
		parameter_synonyms = ParameterSynonym.objects.select_related().all().order_by('name')

		if updater_selected and updater_selected != 'all':
			parameter_synonyms = parameter_synonyms.select_related().filter(
				updater = updater_selected)
		if not updater_selected:
			parameter_synonyms = parameter_synonyms.select_related().filter(
				updater = None)

		if distributor_selected and distributor_selected != 'all':
			parameter_synonyms = parameter_synonyms.select_related().filter(
				distributor = distributor_selected)
		if not distributor_selected:
			parameter_synonyms = parameter_synonyms.select_related().filter(
				distributor = None)

		if parameter_selected and parameter_selected != 'all':
			parameter_synonyms = parameter_synonyms.select_related().filter(
				parameter = parameter_selected)
		if not parameter_selected:
			parameter_synonyms = parameter_synonyms.select_related().filter(
				parameter = None)

		# Получаем дополнительные списки объектов
		updaters = Updater.objects.select_related().all().order_by('name')
		distributors = Distributor.objects.select_related().all().order_by('name')
		parameters = Parameter.objects.select_related().all().order_by('name')

	return render(request, 'catalog/parametersynonyms.html', locals())


def ajaxGetParameterSynonym(request):
	"AJAX-представление: Get Parameter Synonym."

	# Импортируем
	import json
	from catalog.models import ParameterSynonym, Updater, Distributor, Parameter

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_parametersynonym')\
	or not request.user.has_perm('catalog.delete_parametersynonym'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		s = ParameterSynonym.objects.get(
			id = request.POST.get('parameter_synonym_id'))

		parameter_synonym         = {}
		parameter_synonym['id']   = s.id
		parameter_synonym['name'] = s.name

		if s.updater:
			parameter_synonym['updater']          = {}
			parameter_synonym['updater']['id']    = s.updater.id
			parameter_synonym['updater']['name']  = s.updater.alias
			parameter_synonym['updater']['alias'] = s.updater.name
		else:
			parameter_synonym['updater']          = {}
			parameter_synonym['updater']['id']    = 0
			parameter_synonym['updater']['name']  = ''
			parameter_synonym['updater']['alias'] = ''

		if s.distributor:
			parameter_synonym['distributor']          = {}
			parameter_synonym['distributor']['id']    = s.distributor.id
			parameter_synonym['distributor']['name']  = s.distributor.name
			parameter_synonym['distributor']['alias'] = s.distributor.alias
		else:
			parameter_synonym['distributor']          = {}
			parameter_synonym['distributor']['id']    = 0
			parameter_synonym['distributor']['name']  = ''
			parameter_synonym['distributor']['alias'] = ''

		if s.parameter:
			parameter_synonym['parameter']          = {}
			parameter_synonym['parameter']['id']    = s.parameter.id
			parameter_synonym['parameter']['name']  = s.parameter.name
			parameter_synonym['parameter']['alias'] = s.parameter.alias
		else:
			parameter_synonym['parameter']          = {}
			parameter_synonym['parameter']['id']    = 0
			parameter_synonym['parameter']['name']  = ''
			parameter_synonym['parameter']['alias'] = ''

		result = {
			'status'            : 'success',
			'message'           : 'Данные синонима получены.',
			'parameter_synonym' : parameter_synonym}

	except ParameterSynonym.DoesNotExist:
		result = {
			'status'  : 'alert',
			'message' : 'Ошибка: синоним отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveParameterSynonym(request):
	"AJAX-представление: Save Parameter Synonym."

	# Импортируем
	import json
	from django.utils import timezone
	from catalog.models import ParameterSynonym, Updater, Distributor, Parameter

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	try:
		parameter_synonym = ParameterSynonym.objects.get(
			id = request.POST.get('parameter_synonym_id'))
		if not request.user.has_perm('catalog.change_parametersynonym'):
			return HttpResponse(status = 403)
	except ParameterSynonym.DoesNotExist:
		parameter_synonym = ParameterSynonym()
		if not request.user.has_perm('catalog.add_parametersynonym'):
			return HttpResponse(status = 403)
		parameter_synonym.created = timezone.now()

	# name
	if not request.POST.get('parameter_synonym_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	parameter_synonym.name = request.POST.get('parameter_synonym_name').strip()[:1024]

	# updater
	try:
		parameter_synonym.updater = Updater.objects.get(
			id = request.POST.get('parameter_synonym_updater_id'))
	except Updater.DoesNotExist:
		parameter_synonym.updater = None

	# distributor
	try:
		parameter_synonym.distributor = Distributor.objects.get(
			id = request.POST.get('parameter_synonym_distributor_id'))
	except Distributor.DoesNotExist:
		parameter_synonym.distributor = None

	# parameter
	try:
		parameter_synonym.parameter = Parameter.objects.get(
			id = request.POST.get('parameter_synonym_parameter_id'))
	except Parameter.DoesNotExist:
		parameter_synonym.parameter = None

	# modified
	parameter_synonym.modified = timezone.now()

	# Сохраняем
	parameter_synonym.save()

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Синоним {} сохранён.'.format(parameter_synonym.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxLinkParameterSynonymSameParameter(request):
	"AJAX-представление: Link Parameter Synonym same Parameter."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import ParameterSynonym, Parameter

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_parametersynonym')\
	or not request.user.has_perm('catalog.add_parameter'):
		return HttpResponse(status = 403)

	# Получаем объект синонима
	try:
		parameter_synonym = ParameterSynonym.objects.get(
			id = request.POST.get('parameter_synonym_id'))
	except ParameterSynonym.DoesNotExist:
		result = {
			'status'  : 'alert',
			'message' : 'Ошибка: синоним отсутствует в базе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# name
	name = parameter_synonym.name

	# alias
	alias = unidecode.unidecode(name.lower())
	alias = alias.replace(' ', '-')
	alias = alias.replace('&', 'and')
	alias = alias.replace('\'', '')

	# parameter
	try:
		parameter = Parameter.objects.get(alias = alias)
	except Parameter.DoesNotExist:
		parameter = Parameter()
		parameter.name = name
		parameter.alias = alias
		parameter.created = timezone.now()
		parameter.modified = timezone.now()
		parameter.save()

	parameter_synonym.parameter = parameter
	parameter_synonym.modified = timezone.now()
	parameter_synonym.save()

	parameters = []
	vs = Parameter.objects.all()
	for v in vs:
		parameter = {
			'id'   : v.id,
			'name' : v.name}
		parameters.append(parameter)

	parameter = {
		'id'   : parameter_synonym.parameter.id,
		'name' : parameter_synonym.parameter.name}

	result = {
		'status'  : 'success',
		'message' : 'Синоним {} привязан к одноименному производителю {}.'.format(
			parameter_synonym.name,
			parameter_synonym.parameter.name),
		'parameter'  : parameter,
		'parameters' : parameters}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Category Synonym


def categorysynonyms(request, updater_selected = 'all', distributor_selected = 'all', category_selected = 'all'):
	"Представление: список синонимов категорий."

	# Импортируем
	from catalog.models import CategorySynonym, Category, Updater, Distributor

	# Преобразуем типы данных
	if updater_selected != 'all':
		updater_selected = int(updater_selected)
	if distributor_selected != 'all':
		distributor_selected = int(distributor_selected)
	if category_selected != 'all':
		category_selected = int(category_selected)

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_categorysynonym')\
	or request.user.has_perm('catalog.change_categorysynonym')\
	or request.user.has_perm('catalog.delete_categorysynonym'):

		# Получаем список объектов синонимов
		category_synonyms = CategorySynonym.objects.select_related().all().order_by('name')
		if updater_selected and updater_selected != 'all':
			category_synonyms = category_synonyms.select_related().filter(updater = updater_selected)
		if not updater_selected:
			category_synonyms = category_synonyms.select_related().filter(updater = None)

		if distributor_selected and distributor_selected != 'all':
			category_synonyms = category_synonyms.select_related().filter(distributor = distributor_selected)
		if not distributor_selected:
			category_synonyms = category_synonyms.select_related().filter(distributor = None)

		if category_selected and category_selected != 'all':
			category_synonyms = category_synonyms.select_related().filter(category = category_selected)
		if not category_selected:
			category_synonyms = category_synonyms.select_related().filter(category = None)

		# Получаем дополнительные списки объектов
		updaters = Updater.objects.select_related().all().order_by('name')
		distributors = Distributor.objects.select_related().all().order_by('name')
		categories = []
		categories = Category.objects.getCategoryTree(categories)

		# Корректируем имена категорий с учетом вложенноти
		for category in categories:
			category.name = '— ' * category.level + category.name

	return render(request, 'catalog/categorysynonyms.html', locals())


def ajaxGetCategorySynonym(request):
	"AJAX-представление: Get Category Synonym."

	# Импортируем
	import json
	from catalog.models import CategorySynonym, Updater, Distributor, Category

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_categorysynonym')\
	or not request.user.has_perm('catalog.delete_categorysynonym'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		s = CategorySynonym.objects.get(
			id = request.POST.get('category_synonym_id'))

		category_synonym              = {}
		category_synonym['id']        = s.id
		category_synonym['name']      = s.name

		if s.updater:
			category_synonym['updater']          = {}
			category_synonym['updater']['id']    = s.updater.id
			category_synonym['updater']['name']  = s.updater.alias
			category_synonym['updater']['alias'] = s.updater.name
		else:
			category_synonym['updater']          = {}
			category_synonym['updater']['id']    = 0
			category_synonym['updater']['name']  = ''
			category_synonym['updater']['alias'] = ''

		if s.distributor:
			category_synonym['distributor']          = {}
			category_synonym['distributor']['id']    = s.distributor.id
			category_synonym['distributor']['name']  = s.distributor.name
			category_synonym['distributor']['alias'] = s.distributor.alias
		else:
			category_synonym['distributor']          = {}
			category_synonym['distributor']['id']    = 0
			category_synonym['distributor']['name']  = ''
			category_synonym['distributor']['alias'] = ''

		if s.category:
			category_synonym['category']          = {}
			category_synonym['category']['id']    = s.category.id
			category_synonym['category']['name']  = s.category.name
			category_synonym['category']['alias'] = s.category.alias
		else:
			category_synonym['category']          = {}
			category_synonym['category']['id']    = 0
			category_synonym['category']['name']  = ''
			category_synonym['category']['alias'] = ''

		result = {
			'status':   'success',
			'message':  'Данные синонима категории получены.',
			'category_synonym': category_synonym}

	except CategorySynonym.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: синоним категории отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveCategorySynonym(request):
	"AJAX-представление: Save Category Synonym."

	# Импортируем
	import json
	from django.utils import timezone
	from catalog.models import CategorySynonym, Updater, Distributor, Category

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	try:
		category_synonym = CategorySynonym.objects.get(
			id = request.POST.get('category_synonym_id'))
		if not request.user.has_perm('catalog.change_categorysynonym'):
			return HttpResponse(status = 403)
	except CategorySynonym.DoesNotExist:
		category_synonym = CategorySynonym()
		if not request.user.has_perm('catalog.add_categorysynonym'):
			return HttpResponse(status = 403)
		category_synonym.created = timezone.now()

	# name
	if not request.POST.get('category_synonym_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	category_synonym.name = request.POST.get('category_synonym_name').strip()[:1024]

	# updater
	try:
		category_synonym.updater = Updater.objects.get(
			id = request.POST.get('category_synonym_updater_id'))
	except Updater.DoesNotExist:
		category_synonym.updater = None

	# distributor
	try:
		category_synonym.distributor = Distributor.objects.get(
			id = request.POST.get('category_synonym_distributor_id'))
	except Distributor.DoesNotExist:
		category_synonym.distributor = None

	# category
	try:
		category_synonym.category = Category.objects.get(
			id = request.POST.get('category_synonym_category_id'))
	except Category.DoesNotExist:
		category_synonym.category = None

	# modified
	category_synonym.modified = timezone.now()

	# Сохраняем
	category_synonym.save()

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Синоним категории {} сохранён.'.format(category_synonym.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


# Vendor Synonym


def vendorsynonyms(request, updater_selected = 'all', distributor_selected = 'all', vendor_selected = 'all'):
	"Представление: список синонимов производителей."

	# Импортируем
	from catalog.models import VendorSynonym, Vendor, Updater, Distributor

	# Преобразуем типы данных
	if updater_selected != 'all':
		updater_selected = int(updater_selected)
	if distributor_selected != 'all':
		distributor_selected = int(distributor_selected)
	if vendor_selected != 'all':
		vendor_selected = int(vendor_selected)

	# Проверяем права доступа
	if request.user.has_perm('catalog.add_vendorsynonym')\
	or request.user.has_perm('catalog.change_vendorsynonym')\
	or request.user.has_perm('catalog.delete_vendorsynonym'):

		# Получаем список объектов синонимов
		vendor_synonyms = VendorSynonym.objects.select_related().all().order_by('name')

		if updater_selected and updater_selected != 'all':
			vendor_synonyms = vendor_synonyms.select_related().filter(updater = updater_selected)
		if not updater_selected:
			vendor_synonyms = vendor_synonyms.select_related().filter(updater = None)

		if distributor_selected and distributor_selected != 'all':
			vendor_synonyms = vendor_synonyms.select_related().filter(distributor = distributor_selected)
		if not distributor_selected:
			vendor_synonyms = vendor_synonyms.select_related().filter(distributor = None)

		if vendor_selected and vendor_selected != 'all':
			vendor_synonyms = vendor_synonyms.select_related().filter(vendor = vendor_selected)
		if not vendor_selected:
			vendor_synonyms = vendor_synonyms.select_related().filter(vendor = None)

		# Получаем дополнительные списки объектов
		updaters = Updater.objects.select_related().all().order_by('name')
		distributors = Distributor.objects.select_related().all().order_by('name')
		vendors = Vendor.objects.select_related().all().order_by('name')

	return render(request, 'catalog/vendorsynonyms.html', locals())


def ajaxSaveVendorSynonym(request):
	"AJAX-представление: Save Vendor Synonym."

	# Импортируем
	import json
	from django.utils import timezone
	from catalog.models import VendorSynonym, Updater, Distributor, Vendor

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	try:
		vendor_synonym = VendorSynonym.objects.get(
			id = request.POST.get('vendor_synonym_id'))
		if not request.user.has_perm('catalog.change_vendorsynonym'):
			return HttpResponse(status = 403)
	except VendorSynonym.DoesNotExist:
		vendor_synonym = VendorSynonym()
		if not request.user.has_perm('catalog.add_vendorsynonym'):
			return HttpResponse(status = 403)
		vendor_synonym.created = timezone.now()

	# name
	if not request.POST.get('vendor_synonym_name').strip():
		result = {
			'status': 'alert',
			'message': 'Ошибка: отсутствует наименование.'}
		return HttpResponse(json.dumps(result), 'application/javascript')
	vendor_synonym.name = request.POST.get('vendor_synonym_name').strip()[:1024]

	# updater
	try:
		vendor_synonym.updater = Updater.objects.get(
			id = request.POST.get('vendor_synonym_updater_id'))
	except Updater.DoesNotExist:
		vendor_synonym.updater = None

	# distributor
	try:
		vendor_synonym.distributor = Distributor.objects.get(
			id = request.POST.get('vendor_synonym_distributor_id'))
	except Distributor.DoesNotExist:
		vendor_synonym.distributor = None

	# vendor
	try:
		vendor_synonym.vendor = Vendor.objects.get(
			id = request.POST.get('vendor_synonym_vendor_id'))
	except Vendor.DoesNotExist:
		vendor_synonym.vendor = None

	# modified
	vendor_synonym.modified = timezone.now()

	# Сохраняем
	vendor_synonym.save()

	# Возвращаем ответ
	result = {
		'status': 'success',
		'message': 'Синоним производителя {} сохранён.'.format(vendor_synonym.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxLinkVendorSynonymSameVendor(request):
	"AJAX-представление: Link Vendor Synonym same Vendor."

	# Импортируем
	import json
	import unidecode
	from django.utils import timezone
	from catalog.models import VendorSynonym, Vendor

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_vendorsynonym')\
	or not request.user.has_perm('catalog.add_vendor'):
		return HttpResponse(status = 403)

	# Получаем объект синонима
	try:
		vendor_synonym = VendorSynonym.objects.get(
			id = request.POST.get('vendor_synonym_id'))
	except VendorSynonym.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: синоним производителя отсутствует в базе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# name
	name = vendor_synonym.name

	# alias
	alias = unidecode.unidecode(name.lower())
	alias = alias.replace(' ', '-')
	alias = alias.replace('&', 'and')
	alias = alias.replace('\'', '')

	# vendor
	try:
		vendor = Vendor.objects.get(alias = alias)
	except Vendor.DoesNotExist:
		vendor = Vendor()
		vendor.name = name
		vendor.alias = alias
		vendor.created = timezone.now()
		vendor.modified = timezone.now()
		vendor.save()

	vendor_synonym.vendor = vendor
	vendor_synonym.modified = timezone.now()
	vendor_synonym.save()

	vendors = []
	vs = Vendor.objects.all()
	for v in vs:
		vendor = {
			'id'   : v.id,
			'name' : v.name}
		vendors.append(vendor)

	vendor = {
		'id'   : vendor_synonym.vendor.id,
		'name' : vendor_synonym.vendor.name}

	result = {
		'status'  : 'success',
		'message' : 'Синоним {} привязан к одноименному производителю {}.'.format(vendor_synonym.name, vendor_synonym.vendor.name),
		'vendor'  : vendor,
		'vendors' : vendors
		}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxGet(request, *args, **kwargs):
	"AJAX-представление: Get Object."

	import json
	import catalog.models

	model = catalog.models.models[kwargs['model_name']]

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	if not request.user.has_perm('catalog.change_{}'.format(kwargs['model_name']))\
	or not request.user.has_perm('catalog.delete_{}'.format(kwargs['model_name'])):
		return HttpResponse(status = 403)

	try:
		m = model.objects.get(id = request.POST.get('id'))

		result = {
			'status'             : 'success',
			kwargs['model_name'] : m.getDicted()}

	except model.DoesNotExist:
		result = {
			'status'  : 'alert',
			'message' : 'Ошибка: объект отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSave(request, *args, **kwargs):
	"AJAX-представление: Save Object."

	pass


def ajaxSwitchState(request, *args, **kwargs):
	"AJAX-представление: Switch State."

	import json
	from datetime import datetime
	import catalog.models

	model = catalog.models.models[kwargs['model_name']]

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	if not request.user.has_perm('catalog.change_{}'.format(kwargs['model_name'])):
		return HttpResponse(status=403)

	try:
		o = model.objects.get(id = request.POST.get('id'))
	except model.DoesNotExist:
		result = {
			'status'  : 'alert',
			'message' : 'Объект с идентификатором {} отсутствует в базе.'.format(
				request.POST.get('id'))}
		return HttpResponse(json.dumps(result), 'application/javascript')
	else:
		if 'true' == request.POST.get('state'):
			o.state = True
		else:
			o.state = False
		o.save()

		result = {
			'status'             : 'success',
			kwargs['model_name'] : o.getDicted()}

	return HttpResponse(json.dumps(result), 'application/javascript')

def ajaxDelete(request, *args, **kwargs):
	"AJAX-представление: Delete Object."

	import json
	import catalog.models

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	if not request.user.has_perm('catalog.delete_{}'.format(model_name)):
		return HttpResponse(status = 403)

	model = catalog.models.models[model_name]

	try:
		m = model.objects.get(id = request.POST.get('id'))
	except model.DoesNotExist:
		result = {
			'status'  : 'alert',
			'message' : 'Ошибка: объект отсутствует в базе.'}
	else:
		m.delete()
		result = {
			'status' : 'success'}
	finally:
		return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxLinkSame(request, *args, **kwargs):
	"AJAX-представление: Link Model to Same Foreign."

	import json
	import unidecode
	import catalog.models

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	if not request.user.has_perm('catalog.change_{}'.format(model_name))\
	or not request.user.has_perm('catalog.add_{}'.format(foreign_name)):
		return HttpResponse(status = 403)

	model   = catalog.models.models[model_name]
	foreign = catalog.models.models[foreign_name]

	try:
		o = model.objects.get(id = request.POST.get('id'))
	except model.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: объект отсутствует в базе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	name = o.name

	alias = unidecode.unidecode(name.lower())
	alias = alias.replace(' ', '-')
	alias = alias.replace('&', 'and')
	alias = alias.replace('\'', '')

	try:
		f = foreign.objects.get(alias = alias)
	except foreign.DoesNotExist:
		f = foreign()
		f.name = name
		f.alias = alias
		f.created = timezone.now()
		f.modified = timezone.now()
		f.save()

	if   'vendor'         == foreign_name: o.vendor   = f
	elif 'category'       == foreign_name: o.category = f
	elif 'parameter'      == foreign_name: o.parameter = f
	elif 'parametervalue' == foreign_name: o.parameter_value = f

	o.modified = timezone.now()
	o.save()

	result = {
		'status' : 'success',
		'o'      : o.getDicted(),
		'fs'     : foreign.objects.getAllDicted()
	}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')
