from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
import math


# Список продуктов
def products(request, search=None, vendor=None, category=None, childs=None, page=None):

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
	categories = getCategoryTree(categories)

	# Корректируем имена категорий с учетом вложенноти
	for c in categories:
		c.name = '— ' * c.level + c.name

	root = etree.Element("div")
	getCategoryHTMLTree(root, None, True)
	categories_ul = etree.tostring(root)

	# Получаем список всех имеющихся производителей
	vendors = Vendor.objects.filter(state=True)

	# Получаем список категорий, из которых выводить товар
	if category and childs == 'y': # Указанная категория и все потомки
		category = Category.objects.get(id=category)
		product_categories.append(category)
		product_categories = getCategoryTree(product_categories, category)
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


# Продукт
def product(request, id=None, vendor=None, article=None):

	# Импортируем
	from catalog.models import Vendor, Product

	# Получаем объект продукта
	if id:
		product = Product.objects.get(id=id)
	elif vendor and article:
		vendor = Vendor.objects.get(alias=vendor)
		product = Product.objects.get(vendor=vendor, article=article)

	return render(request, 'catalog/product.html', locals())


# Список загрузчиков
def updaters(request):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import Updater

	# Получаем список
	updaters = Updater.objects.all().order_by('name')

	return render(request, 'catalog/updaters.html', locals())


# Загрузчик
def updater(request, alias):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import Updater

	# Получаем объект
	updater = Updater.objects.get(alias=alias)

	return render(request, 'catalog/updater.html', locals())


# Список производителей
def vendors(request):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import Vendor

	# Получаем список
	items = Vendor.objects.all().order_by('name')

	return render(request, 'catalog/vendors.html', locals())


# Производитель
def vendor(request, alias):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import Vendor

	# Получаем список
	vendor = Vendor.objects.get(alias=alias)

	return render(request, 'catalog/vendor.html', locals())


# Список поставщиков
def distributors(request):

	# Импортируем
	from catalog.models import Distributor

	# Проверяем права доступа
	if request.user.has_perm('catalog.change_distributor'):

		# Получаем список
		distributors = Distributor.objects.all().order_by('name')

	return render(request, 'catalog/distributors.html', locals())


# Поставщик
def distributor(request, alias):

	# Импортируем
	from catalog.models import Distributor

	# Проверяем права доступа
	if request.user.has_perm('catalog.change_distributor'):

		# Получаем объект
		distributor = Distributor.objects.get(alias = alias)

	return render(request, 'catalog/distributor.html', locals())


# Список складов
def stocks(request):

	# Импортируем
	from catalog.models import Stock

	# Проверяем права доступа
	if request.user.has_perm('catalog.change_stock'):

		# Получаем список
		stocks = Stock.objects.all().order_by('alias')

	return render(request, 'catalog/stocks.html', locals())


# Склад
def stock(request, alias):

	# Импортируем
	from catalog.models import Stock

	# Проверяем права доступа
	if request.user.has_perm('catalog.change_stock'):

		# Получаем список
		stock = Stock.objects.get(alias=alias)

	return render(request, 'catalog/stock.html', locals())


# Список категорий
def categories(request):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import Category

	# Получаем дерево категорий
	categories = []
	categories = getCategoryTree(categories)

	# Корректируем имена с учетом вложеннот
	for category in categories:
		category.name = '— ' * category.level + category.name


	return render(request, 'catalog/categories.html', locals())


# Дерево категорий (используется рекурсия)
def getCategoryTree(tree, parent=None):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

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


# Дерево категорий (используется рекурсия)
def getCategoryHTMLTree(root, parent=None, first=None):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from lxml import etree
	from catalog.models import Category

	# Получаем список дочерних категорий
	categories = Category.objects.filter(parent=parent).filter(state=True).order_by('order')

	# Проходим по списку категорий с рекурсивным погружением
	if len(categories):
		ul = etree.SubElement(root, "ul")
		ul.attrib['class'] = 'no-bullet'
		if first:
			li = etree.SubElement(ul, "li")
			i = etree.SubElement(li, "i")
			i.text = ''
			i.attrib['class'] = 'fa fa-circle-thin'
			a = etree.SubElement(li, "a")
			a.attrib['data-do'] = 'filter-items-select-category'
			a.attrib['data-id'] = ''
			a.attrib['class'] = 'tm-li-category-name'
			a.text = 'Все категории'

		for category in categories:
			li = etree.SubElement(ul, "li")

			# Если есть дочерние
			childs = Category.objects.filter(parent=category).filter(state=True).order_by('order')
			if len(childs):
				li.attrib['class'] = 'closed'
				i = etree.SubElement(li, "i")
				i.attrib['data-do'] = 'switch-li-status'
				i.attrib['data-state'] = 'closed'
				i.text = ''
				i.attrib['class'] = 'fa fa-plus-square-o'
			else:
				i = etree.SubElement(li, "i")
				i.text = ''
				i.attrib['class'] = 'fa fa-circle-thin'
			a = etree.SubElement(li, "a")
			a.attrib['data-do'] = 'filter-items-select-category'
			a.attrib['data-id'] = str(category.id)
			a.attrib['class'] = 'tm-li-category-name'
			a.text = category.name
			getCategoryHTMLTree(li, category)

	# Возвращаем результат
	return root


# Категория
def category(request, category_id):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import Category

	# Получаем список
	category = Category.objects.get(id=category_id)
	context = {'category': category}
	return render(request, 'catalog/category.html', context)

# Список синонимов производителей
def vendorsynonyms(request, updater_selected='all', distributor_selected='all', vendor_selected='all'):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

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
		'items': synonyms,
		'updaters': updaters,
		'distributors': distributors,
		'vendors': vendors,
	}
	return render(request, 'catalog/vendorsynonyms.html', context)


# Синоним производителя
def vendorsynonym(request, synonym_id):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import VendorSynonym, Vendor, Updater, Distributor

	# Получаем список
	synonym = VendorSynonym.objects.get(id=synonym_id)
	context = {'synonym': synonym}
	return render(request, 'catalog/vendorsynonym.html', context)


# Список синонимов категорий
def categorysynonyms(request, updater_selected='all', distributor_selected='all', category_selected='all'):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import CategorySynonym, Category, Updater, Distributor

	# Получаем список объектов синонимов
	items = CategorySynonym.objects.all().order_by('name')
	if (updater_selected != 'all'):
		items = items.filter(updater=updater_selected)
		updater_selected = int(updater_selected)
	if (distributor_selected != 'all'):
		items = items.filter(distributor=distributor_selected)
		distributor_selected = int(distributor_selected)
	if (category_selected != 'all' and category_selected != 'null'):
		items = items.filter(category=category_selected)
		category_selected = int(category_selected)
	if (category_selected == 'null'):
		items = items.filter(category=None)

	# Получаем дополнительные списки объектов
	updaters = Updater.objects.all().order_by('name')
	distributors = Distributor.objects.all().order_by('name')
	categories = []
	categories = getCategoryTree(categories)

	# Корректируем имена категорий с учетом вложенноти
	for category in categories:
		category.name = '— ' * category.level + category.name

	context = {
		'updater_selected': updater_selected,
		'distributor_selected': distributor_selected,
		'category_selected': category_selected,
		'items': items,
		'updaters': updaters,
		'distributors': distributors,
		'categories': categories,
	}
	return render(request, 'catalog/categorysynonyms.html', context)


# Синоним производителя
def categorysynonym(request, synonym_id):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import CategorySynonym, Category, Updater, Distributor

	# Получаем список
	synonym = CategorySynonym.objects.get(id=synonym_id)
	context = {'synonym': synonym}
	return render(request, 'catalog/categorysynonym.html', context)

# Список типов цен
def priceTypes(request):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import PriceType

	# Получаем список
	price_types = PriceType.objects.all().order_by('name')
	context = {'price_types': price_types}
	return render(request, 'catalog/pricetypes.html', context)


# Тип цены
def priceType(request, alias):

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Импортируем
	from catalog.models import PriceType

	# Получаем список
	price_type = Vendor.objects.get(alias=alias)
	context = {'price_type': price_type}
	return render(request, 'catalog/pricetype.html', context)


##  AJAX  ##


# Distributor


def ajaxGetDistributor(request):
	"AJAX-представление: Получение данных поставщика."

	# Импортируем
	import json
	from catalog.models import Distributor

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_distributor'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Получаем объект
	try:
		distributor = Distributor.objects.get(id = request.POST.get('distributor_id'))

		result = {
			'status':                  'success',
			'message':                 'Данные дистрибьютора получены.',
			'distributor_id':          distributor.id,
			'distributor_name':        distributor.name,
			'distributor_alias':       distributor.alias,
			'distributor_description': distributor.description,
			'distributor_state':       distributor.state}

	except Distributor.DoesNotExist:
		result = {
			'status': 'alert',
			'message': 'Ошибка: поставщик отсутствует в базе.'}

	return HttpResponse(json.dumps(result), 'application/javascript')


def ajaxSaveDistributor(request):
	"AJAX-представление: Сохранение данных поставщика."

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
		'status': 'success',
		'message': 'Поставщик {} сохранён.'.format(distributor.name)}

	return HttpResponse(json.dumps(result), 'application/javascript')


# Switch Distributor State
def ajaxSwitchDistributorState(request):

	# Импортируем
	from catalog.models import Distributor
	from datetime import datetime
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# Проверяем права доступа
	if not request.user.has_perm('catalog.change_distributor'):
		result = {
			'status': 'alert',
			'message': 'Ошибка 403: отказано в доступе.'}
		return HttpResponse(json.dumps(result), 'application/javascript')

	# Проверяем корректность вводных данных
	if not request.POST.get('distributor_id') or not request.POST.get('distributor_state'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			distributor = Distributor.objects.get(id=request.POST.get('distributor_id'))
			if request.POST.get('distributor_state') == 'true':
				distributor.state = True
			else:
				distributor.state = False
			distributor.save()
			result = {'status': 'success', 'message': 'Статус поставщика {} изменен на {}.'.format(distributor.name, distributor.state)}
		except Distributor.DoesNotExist:
			result = {'status': 'alert', 'message': 'Поставщик с идентификатором {} отсутствует в базе.'.format(request.POST.get('distributor_id'))}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Add Vendor
def ajaxAddVendor(request):

	# Импортируем
	import json
	import unidecode
	from datetime import datetime
	from catalog.models import Vendor

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	# Проверяем на пустую строку
	if (request.POST.get('name').strip() == ''):
		result = {'status': 'warning', 'message': 'Пожалуй, такого имени быть не может.'}
	else:
		# Добавляем производителя
		try:
			vendor = Vendor.objects.get(name=request.POST.get('name').strip())
			result = {'status': 'warning', 'message': 'Производитель ' + request.POST.get('name').strip() + ' уже существует.'}
		except Vendor.DoesNotExist:
			name = request.POST.get('name').strip()
			alias = unidecode.unidecode(name.lower())
			alias = alias.replace(' ', '-')
			alias = alias.replace('&', 'and')
			alias = alias.replace('\'', '')
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
	if (request.POST.get('name').strip() == '') or (request.POST.get('parent').strip() == ''):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:

		name = request.POST.get('name').strip()

		alias = name.lower()
		alias = alias.replace(' ', '-')

		if (request.POST.get('parent').strip() == 'null'):
			parent = None
			level = 0
		else:
			try:
				parent = Category.objects.get(id=request.POST.get('parent').strip())
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

	# Получаем дерево категорий
	categories = []
	categories = getCategoryTree(categories)

	# Проводим общую нумерацию категорий
	for order, category in enumerate(categories):
		category.order = order
		category.save()

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

	# Проверяем корректность вводных данных
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


# Switch Updater State
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


# Switch Price Type State
def ajaxSwitchPriceTypeState(request):

	# Импортируем
	from catalog.models import PriceType
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
			price_type = PriceType.objects.get(id=request.POST.get('id'))
			if request.POST.get('state') == 'true':
				price_type.state = True;
			else:
				price_type.state = False;
			price_type.save();
			result = {'status': 'success', 'message': 'Статус типа цены ' + price_type.name + ' изменен на ' + str(price_type.state) + '.'}
		except PriceType.DoesNotExist:
			result = {'status': 'alert', 'message': 'Тип цены с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Switch Stock State
def ajaxSwitchStockState(request):

	# Импортируем
	from catalog.models import Stock
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
			stock = Stock.objects.get(id=request.POST.get('id'))
			if request.POST.get('state') == 'true':
				stock.state = True;
			else:
				stock.state = False;
			stock.save();
			result = {'status': 'success', 'message': 'Статус склада ' + stock.name + ' изменен на ' + str(stock.state) + '.'}
		except Stock.DoesNotExist:
			result = {'status': 'alert', 'message': 'Склад с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

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
	import json
	import unidecode
	from datetime import datetime
	from catalog.models import VendorSynonym, Vendor

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
				name = synonym.name
				alias = unidecode.unidecode(name.lower())
				alias = alias.replace(' ', '-')
				alias = alias.replace('&', 'and')
				alias = alias.replace('\'', '')
				vendor = Vendor.objects.get(alias=alias)
			except Vendor.DoesNotExist:
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
			if request.POST.get('category') == 'null' or request.POST.get('category') == '':
				category = None
				synonym.category = None
				synonym.save()
				result = {'status': 'success', 'message': 'Синоним ' + synonym.name + ' отвязан от категории.'}
			else:
				category = Category.objects.get(id=request.POST.get('category'))
				synonym.category = category
				synonym.save()
				result = {'status': 'success', 'message': 'Синоним ' + synonym.name + ' привязан к категории ' + category.name + '.'}
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
	import json
	import unidecode
	from datetime import datetime
	from catalog.models import Vendor

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
			vendor.alias = unidecode.unidecode(vendor.alias.lower())
			vendor.alias = vendor.alias.replace(' ', '-')
			vendor.alias = vendor.alias.replace('&', 'and')
			vendor.alias = vendor.alias.replace('\'', '')
			if request.POST.get('description'): vendor.description = request.POST.get('description')
			vendor.save()
			result = {'status': 'success', 'message': 'Изменения производителя ' + vendor.name + ' сохранены.'}
		except Vendor.DoesNotExist:
			result = {'status': 'alert', 'message': 'Производитель с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Save Price Type
def ajaxSavePriceType(request):

	# Импортируем
	from catalog.models import PriceType
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
			item = PriceType.objects.get(id=request.POST.get('id'))
			item.name = request.POST.get('name')
			item.alias = request.POST.get('alias')
			item.multiplier = request.POST.get('multiplier')
			item.save()
			result = {'status': 'success', 'message': 'Изменения типа цены ' + item.name + ' сохранены.'}
		except PriceType.DoesNotExist:
			result = {'status': 'alert', 'message': 'Тип цены с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Save Product
def ajaxSaveProduct(request):

	# Импортируем
	from catalog.models import Product
	from catalog.models import Vendor
	from catalog.models import Category
	from django.utils import timezone
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	if not request.POST.get('id') or not request.POST.get('product_name') or not request.POST.get('product_article') or not request.POST.get('product_vendor_id'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			item = Product.objects.get(id=request.POST.get('id'))
			item.name = request.POST.get('product_name')
			item.article = request.POST.get('product_article')
			item.vendor = Vendor.objects.get(id=request.POST.get('product_vendor_id'))
			if 'null' == request.POST.get('product_category_id'):
				item.category = None
			else:
				item.category = Category.objects.get(id=request.POST.get('product_category_id'))
			item.description = request.POST.get('product_description')
			if request.POST.get('product_duble_id'):
				item.double = Product.objects.get(id=request.POST.get('product_duble_id'))
			if 'true' == request.POST.get('product_state'):
				item.state = True
			else:
				item.state = False
			item.edited = True
			item.modified = timezone.now()
			item.save()
			result = {
				'status': 'success',
				'message': 'Изменения продукта {} {} сохранены.'.format(item.vendor.name, item.article)}
		except Product.DoesNotExist:
			result = {
				'status': 'alert',
				'message': 'Продукт с идентификатором {} отсутствует в базе.'.format(request.POST.get('id'))}
		except Vendor.DoesNotExist:
			result = {
				'status': 'alert',
				'message': 'Производитель с идентификатором {} отсутствует в базе.'.format(request.POST.get('product_vendor_id'))}
		except Category.DoesNotExist:
			result = {
				'status': 'alert',
				'message': 'Категория с идентификатором {} отсутствует в базе.'.format(request.POST.get('product_category_id'))}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Save Stock
def ajaxSaveStock(request):

	# Импортируем
	from catalog.models import Stock
	from django.utils import timezone
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	# TODO Проверяем права доступа
	#	return HttpResponse(status=403)

	if not request.POST.get('id') or not request.POST.get('name') or not request.POST.get('alias') or not request.POST.get('state') or not request.POST.get('delivery_time_min') or not request.POST.get('delivery_time_max'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			stock       = Stock.objects.get(id=request.POST.get('id'))
			stock.name  = request.POST.get('name')
			stock.alias = request.POST.get('alias')
			if 'true' == request.POST.get('state'):
				stock.state = True
			else:
				stock.state = False
			stock.delivery_time_min = int(request.POST.get('delivery_time_min'))
			stock.delivery_time_max = int(request.POST.get('delivery_time_max'))
			stock.edited = True
			stock.modified = timezone.now()
			stock.save()
			result = {
				'status': 'success',
				'message': 'Изменения склада {} сохранены.'.format(stock.name)}
		except Stock.DoesNotExist:
			result = {
				'status': 'alert',
				'message': 'Склад с идентификатором {} отсутствует в базе.'.format(request.POST.get('id'))}

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


# Trash Category
def ajaxTrashCategorySynonym(request):

	# Импортируем
	from catalog.models import CategorySynonym
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
			item = CategorySynonym.objects.get(id=request.POST.get('id'))
			item.delete()
			result = {'status': 'success', 'message': 'Синоним категории удалён.'}
		except CategorySynonym.DoesNotExist:
			result = {'status': 'alert', 'message': 'Синоним категории с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Get Product
def ajaxGetProduct(request):

	# Импортируемa
	from catalog.models import Product
	import json

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	if not request.POST.get('id'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			product = Product.objects.get(id=request.POST.get('id'))

			if product.category: product_category_id = product.category.id
			else: product_category_id = 'null'
			if product.unit: product_unit_id = product.unit.id
			else: product_unit_id = 0
			if product.duble: product_duble_id = product.duble.id
			else: product_duble_id = ''

			result = {
				'status': 'success',
				'message': 'Данные продукта получены.',
				'product_name': product.name,
				'product_article': product.article,
				'product_vendor_id': product.vendor.id,
				'product_category_id': product_category_id,
				'product_unit_ud': product_unit_id,
				'product_description': product.description,
				'product_duble_id': product_duble_id,
				'product_state': product.state}
		except Product.DoesNotExist:
			result = {'status': 'alert', 'message': 'Продукт с идентификатором ' + request.POST.get('id') + ' отсутствует в базе.'}

	# Возвращаем ответ
	return HttpResponse(json.dumps(result), 'application/javascript')


# Get Parties
def ajaxGetParties(request):

	# Импортируем
	from catalog.models import Product, Party
	import json

	# Инициализируем переменные
	items = []

	# Проверяем тип запроса
	if (not request.is_ajax()) or (request.method != 'POST'):
		return HttpResponse(status=400)

	if not request.POST.get('id'):
		result = {'status': 'warning', 'message': 'Пожалуй, вводные данные не корректны.'}
	else:
		try:
			product = Product.objects.get(id=request.POST.get('id'))

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
