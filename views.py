from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
import math


def distributors(request):
	"Представление: список производителей."

	from catalog.models import Distributor

	if request.user.has_perm('catalog.add_distributor')\
	or request.user.has_perm('catalog.change_distributor')\
	or request.user.has_perm('catalog.delete_distributor'):

		distributors = Distributor.objects.all().order_by('name')

	return render(request, 'catalog/distributors.html', locals())


def updaters(request):
	"Представление: список загрузчиков."

	from catalog.models import Updater

	if request.user.has_perm('catalog.add_updater')\
	or request.user.has_perm('catalog.change_updater')\
	or request.user.has_perm('catalog.delete_updater'):

		updaters = Updater.objects.all().order_by('name')

	return render(request, 'catalog/updaters.html', locals())


def stocks(request):
	"Представление: список складов."

	from catalog.models import Stock

	if request.user.has_perm('catalog.add_stock')\
	or request.user.has_perm('catalog.change_stock')\
	or request.user.has_perm('catalog.delete_stock'):

		stocks = Stock.objects.all().order_by('alias')

	return render(request, 'catalog/stocks.html', locals())


def categories(request):
	"Представление: список категорий."

	from catalog.models import Category

	categories = []
	categories = Category.objects.getCategoryTree(categories)

	for category in categories:
		category.name = '— ' * category.level + category.name

	return render(request, 'catalog/categories.html', locals())


def vendors(request):
	"Представление: список производителей."

	from catalog.models import Vendor

	vendors = Vendor.objects.all().order_by('name')

	return render(request, 'catalog/vendors.html', locals())


def vendor(request, alias):
	"Представление: производитель."

	from catalog.models import Vendor

	vendor = Vendor.objects.get(alias=alias)

	return render(request, 'catalog/vendor.html', locals())


def units(request):
	"Представление: список единиц измерения."

	from catalog.models import Unit

	units = Unit.objects.all()

	return render(request, 'catalog/units.html', locals())


def pricetypes(request):
	"Представление: список типов цен."

	from catalog.models import PriceType

	if request.user.has_perm('catalog.add_pricetype')\
	or request.user.has_perm('catalog.change_pricetype')\
	or request.user.has_perm('catalog.delete_pricetype'):

		pricetypes = PriceType.objects.all().order_by('name')

	return render(request, 'catalog/pricetypes.html', locals())


def currencies(request):
	"Представление: список валют."

	from catalog.models import Currency

	currencies = Currency.objects.all()

	return render(request, 'catalog/currencies.html', locals())


def products(request, search=None, vendor=None, category=None, childs=None, page=None):
	"Представление: список продуктов."

	from lxml import etree
	from django.db.models import Q
	from catalog.models import Product, Category, Vendor

	items_on_page = 100

	# TODO ??
	if not page:
		page = 1

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


def product(request, id = None, vendor = None, article = None):
	"Представление: продукт."

	from catalog.models import Vendor, Product

	if id:
		product = Product.objects.get(id=id)
	elif vendor and article:
		vendor = Vendor.objects.get(alias=vendor)
		product = Product.objects.get(vendor=vendor, article=article)

	return render(request, 'catalog/product.html', locals())


def parametertypes(request):
	"Представление: список типов данных параметров."

	from catalog.models import ParameterType

	parametertypes = ParameterType.objects.all().order_by('name')

	return render(request, 'catalog/parametertypes.html', locals())


def parameters(request):
	"Представление: список параметров."

	from catalog.models import Parameter, ParameterType

	parameters = Parameter.objects.all().order_by('name')
	parametertypes = ParameterType.objects.all().order_by('name')

	return render(request, 'catalog/parameters.html', locals())


def parametervalues(request):
	"Представление: список значений параметров."

	from catalog.models import ParameterValue

	parameter_values = ParameterValue.objects.all()

	return render(request, 'catalog/parametervalues.html', locals())


def parametervaluesynonyms(request, updater_selected = 'all', distributor_selected = 'all', parameter_selected = 'all'):
	"Представление: список синонимов значений параметров."

	from catalog.models import ParameterValueSynonym, Parameter, Updater, Distributor

	if updater_selected != 'all':
		updater_selected = int(updater_selected)
	if distributor_selected != 'all':
		distributor_selected = int(distributor_selected)
	if parameter_selected != 'all':
		parameter_selected = int(parameter_selected)

	if request.user.has_perm('catalog.add_parametervaluesynonym')\
	or request.user.has_perm('catalog.change_parametervaluesynonym')\
	or request.user.has_perm('catalog.delete_parametervaluesynonym'):

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

		updaters     = Updater.objects.select_related().all()
		distributors = Distributor.objects.select_related().all()
		parameters   = Parameter.objects.select_related().all()

	return render(request, 'catalog/parametervaluesynonyms.html', locals())


def parametersynonyms(request, updater_selected = 'all', distributor_selected = 'all', parameter_selected = 'all'):
	"Представление: список синонимов параметров."

	from catalog.models import ParameterSynonym, Parameter, Updater, Distributor, ParameterType

	if updater_selected != 'all':
		updater_selected = int(updater_selected)
	if distributor_selected != 'all':
		distributor_selected = int(distributor_selected)
	if parameter_selected != 'all':
		parameter_selected = int(parameter_selected)

	if request.user.has_perm('catalog.add_parametersynonym')\
	or request.user.has_perm('catalog.change_parametersynonym')\
	or request.user.has_perm('catalog.delete_parametersynonym'):

		parametersynonyms = ParameterSynonym.objects.select_related().all().order_by('name')

		if updater_selected and updater_selected != 'all':
			parametersynonyms = parametersynonyms.select_related().filter(
				updater = updater_selected)
		if not updater_selected:
			parametersynonyms = parametersynonyms.select_related().filter(
				updater = None)

		if distributor_selected and distributor_selected != 'all':
			parametersynonyms = parametersynonyms.select_related().filter(
				distributor = distributor_selected)
		if not distributor_selected:
			parametersynonyms = parametersynonyms.select_related().filter(
				distributor = None)

		if parameter_selected and parameter_selected != 'all':
			parametersynonyms = parametersynonyms.select_related().filter(
				parameter = parameter_selected)
		if not parameter_selected:
			parametersynonyms = parametersynonyms.select_related().filter(
				parameter = None)

		updaters = Updater.objects.select_related().all()
		distributors = Distributor.objects.select_related().all()
		parameters = Parameter.objects.select_related().all()
		parametertypes = ParameterType.objects.select_related().all()

	return render(request, 'catalog/parametersynonyms.html', locals())


def categorysynonyms(request, updater_selected = 'all', distributor_selected = 'all', category_selected = 'all'):
	"Представление: список синонимов категорий."

	from catalog.models import CategorySynonym, Category, Updater, Distributor

	if updater_selected != 'all':
		updater_selected = int(updater_selected)
	if distributor_selected != 'all':
		distributor_selected = int(distributor_selected)
	if category_selected != 'all':
		category_selected = int(category_selected)

	if request.user.has_perm('catalog.add_categorysynonym')\
	or request.user.has_perm('catalog.change_categorysynonym')\
	or request.user.has_perm('catalog.delete_categorysynonym'):

		categorysynonyms = CategorySynonym.objects.select_related().all().order_by('name')
		if updater_selected and updater_selected != 'all':
			categorysynonyms = categorysynonyms.select_related().filter(updater = updater_selected)
		if not updater_selected:
			categorysynonyms = categorysynonyms.select_related().filter(updater = None)

		if distributor_selected and distributor_selected != 'all':
			categorysynonyms = categorysynonyms.select_related().filter(distributor = distributor_selected)
		if not distributor_selected:
			categorysynonyms = categorysynonyms.select_related().filter(distributor = None)

		if category_selected and category_selected != 'all':
			categorysynonyms = categorysynonyms.select_related().filter(category = category_selected)
		if not category_selected:
			categorysynonyms = categorysynonyms.select_related().filter(category = None)

		updaters = Updater.objects.select_related().all().order_by('name')
		distributors = Distributor.objects.select_related().all().order_by('name')
		categories = []
		categories = Category.objects.getCategoryTree(categories)

		for category in categories:
			category.name = '— ' * category.level + category.name

	return render(request, 'catalog/categorysynonyms.html', locals())


def vendorsynonyms(request, updater_selected = 'all', distributor_selected = 'all', vendor_selected = 'all'):
	"Представление: список синонимов производителей."

	from catalog.models import VendorSynonym, Vendor, Updater, Distributor

	if updater_selected != 'all':
		updater_selected = int(updater_selected)
	if distributor_selected != 'all':
		distributor_selected = int(distributor_selected)
	if vendor_selected != 'all':
		vendor_selected = int(vendor_selected)

	if request.user.has_perm('catalog.add_vendorsynonym')\
	or request.user.has_perm('catalog.change_vendorsynonym')\
	or request.user.has_perm('catalog.delete_vendorsynonym'):

		vendorsynonyms = VendorSynonym.objects.select_related().all().order_by('name')

		if updater_selected and updater_selected != 'all':
			vendorsynonyms = vendorsynonyms.select_related().filter(updater = updater_selected)
		if not updater_selected:
			vendorsynonyms = vendorsynonyms.select_related().filter(updater = None)

		if distributor_selected and distributor_selected != 'all':
			vendorsynonyms = vendorsynonyms.select_related().filter(distributor = distributor_selected)
		if not distributor_selected:
			vendorsynonyms = vendorsynonyms.select_related().filter(distributor = None)

		if vendor_selected and vendor_selected != 'all':
			vendorsynonyms = vendorsynonyms.select_related().filter(vendor = vendor_selected)
		if not vendor_selected:
			vendorsynonyms = vendorsynonyms.select_related().filter(vendor = None)

		updaters = Updater.objects.select_related().all()
		distributors = Distributor.objects.select_related().all()
		vendors = Vendor.objects.select_related().all()

	return render(request, 'catalog/vendorsynonyms.html', locals())


def ajax_get(request, *args, **kwargs):
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
			kwargs['model_name'] : m.get_dicted()}

	except model.DoesNotExist:
		result = {
			'status'  : 'alert',
			'message' : 'Ошибка: объект отсутствует в базе.',
			'id'      : request.POST.get('id')}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_save(request, *args, **kwargs):
	"AJAX-представление: Save Object."


	import json
	from django.utils import timezone
	import catalog.models

	model = catalog.models.models[kwargs['model_name']]

	result = {
		'status' : 'success',
		'reload' : False}

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	try:
		o = model.objects.get(id = request.POST.get('id'))
		if not request.user.has_perm('catalog.change_{}'.format(kwargs['model_name'])):
			return HttpResponse(status = 403)
	except model.DoesNotExist:
		o = model()
		result['reload'] = True
		if not request.user.has_perm('catalog.add_{}'.format(kwargs['model_name'])):
			return HttpResponse(status = 403)
		o.created = timezone.now()

	for key in request.POST:

		if key == 'name':
			if request.POST.get('name', '').strip():
				o.name = request.POST.get('name').strip()
			else:
				break

			if request.POST.get('alias', '').strip():
				o.alias = fix_alias(request.POST.get('alias'), model_name = kwargs['model_name'])
			else:
				o.alias = fix_alias(request.POST.get(key))

			if request.POST.get('name_search', '').strip():
				o.name_search = request.POST.get('name_search')[:512]
			else:
				o.name_search = request.POST.get(key)[:512]

			if request.POST.get('full_name', '').strip():
				o.full_name = request.POST.get('full_name').strip()
			else:
				o.name = request.POST.get(key)[:512]

			if request.POST.get('name_short', '').strip():
				o.name_short = request.POST.get('name_short')[:100]
			else:
				o.name_short = request.POST.get(key)[:100]

			if request.POST.get('name_short_xml', '').strip():
				o.name_short_xml = request.POST.get('name_short_xml')[:100]
			else:
				o.name_short_xml = request.POST.get(key)[:100]

		elif key == 'article':
			o.article = request.POST.get('article', '').strip()[:100]

		elif key == 'description':
			o.description = request.POST.get(key, '').strip()

		elif key == 'login':
			o.login = request.POST.get(key, '').strip()

		elif key == 'password':
			o.password = request.POST.get(key, '').strip()

		elif key == 'state':
			if 'true' == request.POST.get(key, 'true'):
				o.state = True
			else:
				o.state = False

		elif key == 'delivery_time_min':
			try:
				o.delivery_time_min = int(request.POST.get(key, 0))
			except Exception:
				o.delivery_time_min = 0

		elif key == 'delivery_time_max':
			try:
				o.delivery_time_max = int(request.POST.get(key, 0))
			except Exception:
				o.delivery_time_max = 0

		elif key == 'order':
			try:
				o.order = int(request.POST.get(key, 0))
			except Exception:
				o.order = 0

		elif key == 'rate':
			try:
				o.rate = float(request.POST.get(key).strip().replace(',', '.').replace(' ', ''))
			except Exception:
				o.rate = 1.0

		elif key == 'quantity' and kwargs['model_name'] == 'currency':
			try:
				o.quantity = float(request.POST.get(key).strip().replace(',', '.').replace(' ', ''))
			except Exception:
				o.quantity = 1.0

		elif key == 'multiplier':
			try:
				o.multiplier = float(request.POST.get(key).strip().replace(',', '.').replace(' ', ''))
			except Exception:
				o.multiplier = 1.0

		elif 'connector_id' == key:
			try:
				m = catalog.models.models['connector']
				o.connector = m.objects.get(id = request.POST.get(key, ''))
			except Exception:
				o.connector = None

		elif key == 'updater_id':
			try:
				m = catalog.models.models['updater']
				o.updater = m.objects.get(id = request.POST.get(key, ''))
			except Exception:
				o.updater = None

		elif key == 'distributor_id':
			try:
				m = catalog.models.models['distributor']
				o.distributor = m.objects.get(id = request.POST.get(key, ''))
			except Exception:
				o.distributor = None

		elif key == 'vendor_id':
			try:
				m = catalog.models.models['vendor']
				o.vendor = m.objects.get(id = request.POST.get(key, ''))
			except Exception:
				o.vendor = None

		elif key == 'category_id':
			try:
				m = catalog.models.models['category']
				o.category = m.objects.get(id = request.POST.get(key, ''))
			except Exception:
				o.category = None

		elif key == 'parent_id' and kwargs['model_name'] == 'category':

			from django.db.models import Max

			old_parent = o.parent

			try:
				m = catalog.models.models[kwargs['model_name']]
				o.parent = m.objects.get(id = request.POST.get(key, ''))
			except Exception:
				o.parent = None
				o.level = 0

			else:

				childs = []
				childs = m.objects.getCategoryTree(childs, o)

				if o.parent in childs:
					o.parent = None
					o.level = 0
				else:
					o.level = o.parent.level + 1

			if o.parent != old_parent:
				result['reload'] = True

			o.order = m.objects.filter(parent = o.parent).aggregate(Max('order'))['order__max']

			if o.order is None:
				o.order = 0
			else:
				o.order += 1

			if o.parent:
				o.path = "{}{}/".format(o.parent.path, o.id)
			else:
				o.path = "/{}/".format(o.id)

		elif key == 'duble_id' and model_name == 'product':
			try:
				m = catalog.models.models[kwargs['model_name']]
				o.duble = m.objects.get(id = request.POST.get(key, ''))
			except Exception:
				o.duble = None

		elif key == 'parametertype_id':
			result['parametertype_id'] = request.POST.get(key, '')
			try:
				m = catalog.models.models['parametertype']
				o.parametertype = m.objects.get(id = request.POST.get(key, ''))
			except Exception:
				o.parametertype = None

		elif key == 'parameter_id':
			try:
				m = catalog.models.models['parameter']
				o.parameter = m.objects.get(id = request.POST.get(key, ''))
			except Exception:
				o.parameter = None

		elif key == 'parametervalue_id':
			try:
				m = catalog.models.models['parametervalue']
				o.parametervalue = m.objects.get(id = request.POST.get(key, ''))
			except Exception:
				o.parametervalue = None

	o.modified = timezone.now()
	o.save()

	result[kwargs['model_name']] = o.get_dicted()

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_switch_state(request, *args, **kwargs):
	"AJAX-представление: Switch State."

	import json
	from django.utils import timezone
	import catalog.models

	model = catalog.models.models[kwargs['model_name']]

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	if not request.user.has_perm('catalog.change_{}'.format(kwargs['model_name'])):
		return HttpResponse(status=403)

	try:
		o = model.objects.get(id = request.POST.get('id'))
	except Exception:
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
		o.modified = timezone.now()
		o.save()

		result = {
			'status'             : 'success',
			kwargs['model_name'] : o.get_dicted()}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_delete(request, *args, **kwargs):
	"AJAX-представление: Delete Object."

	import json
	import catalog.models

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status = 400)

	if not request.user.has_perm('catalog.delete_{}'.format(kwargs['model_name'])):
		return HttpResponse(status = 403)

	model = catalog.models.models[kwargs['model_name']]

	try:
		m = model.objects.get(id = request.POST.get('id'))
	except Exception:
		result = {
			'status'  : 'alert',
			'message' : 'Ошибка: объект отсутствует в базе.',
			'id'      : request.POST.get('id')}
	else:
		m.delete()
		result = {
			'status' : 'success',
			'id'     : request.POST.get('id')}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_link_same_foreign(request, *args, **kwargs):
	"AJAX-представление: Link Model to Same Foreign."

	import json
	from django.utils import timezone
	import catalog.models

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	if not request.user.has_perm('catalog.change_{}'.format(kwargs['model_name']))\
	or not request.user.has_perm('catalog.add_{}'.format(kwargs['model_name'])):
		return HttpResponse(status = 403)

	model   = catalog.models.models[kwargs['model_name']]
	foreign = catalog.models.models[kwargs['foreign_name']]

	try:
		o = model.objects.get(id = request.POST.get('id'))
	except Exception:
		result = {
			'status': 'alert',
			'message': 'Ошибка: объект отсутствует в базе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	name = o.name

	alias = fix_alias(name)

	try:
		f = foreign.objects.get(alias = alias)
	except Exception:
		f = foreign()
		f.name = name
		f.alias = alias
		f.created = timezone.now()
		f.modified = timezone.now()
		f.save()

	if kwargs['foreign_name'] == 'vendor':
		o.vendor   = f
	elif kwargs['foreign_name'] == 'category':
		o.category = f
	elif kwargs['foreign_name'] == 'parameter':
		o.parameter = f
	elif kwargs['foreign_name'] == 'parametervalue':
		o.parametervalue = f

	o.modified = timezone.now()
	o.save()

	result = {
		'status'               : 'success',
		kwargs['model_name']   : o.get_dicted(),
		kwargs['foreign_name'] : foreign.objects.get_all_dicted()
	}

	return HttpResponse(json.dumps(result), 'application/javascript')


# TODO Need refactoring
def ajax_get_parties(request):
	"AJAX-представление: Get Parties."

	from catalog.models import Product, Party
	import json

	items = []

	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	if request.POST.get('product_id'):
		try:
			product = Product.objects.get(id = request.POST.get('product_id'))

			parties = Party.objects.filter(product=product)

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
						item['quantity'] = "{}&nbsp;{}".format(party.quantity, party.unit.name_short_xml)
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
						item['quantity'] = "{}&nbsp;{}".format(party.quantity, party.unit.name_short_xml)
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

	result = json.dumps(result)

	return HttpResponse(result, 'application/javascript')


def fix_alias(alias, model_name = None):

	import unidecode

	if model_name == 'currency':
		alias = alias.upper()
	else:
		alias = alias.lower()

	alias = unidecode.unidecode(alias)

	alias = alias.replace(' ', '-')
	alias = alias.replace('&', 'and')
	alias = alias.replace('\'', '')
	alias = alias.replace('(', '')
	alias = alias.replace(')', '')

	alias = alias.strip()[:100]

	return alias
