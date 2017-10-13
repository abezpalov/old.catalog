from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

def manage_updaters(request):
    "Представление: управление загрузчиками."

    from catalog.models import Updater

    if request.user.has_perm('catalog.add_updater')\
    or request.user.has_perm('catalog.change_updater')\
    or request.user.has_perm('catalog.delete_updater'):

        updaters = Updater.objects.all().order_by('name')

    return render(request, 'catalog/manage_updaters.html', locals())


def manage_distributors(request):
    "Представление: управление производителеми."

    from catalog.models import Distributor

    if request.user.has_perm('catalog.add_distributor')\
    or request.user.has_perm('catalog.change_distributor')\
    or request.user.has_perm('catalog.delete_distributor'):

        distributors = Distributor.objects.all().order_by('name')

    return render(request, 'catalog/manage_distributors.html', locals())


def manage_stocks(request):
    "Представление: управление складами."

    from catalog.models import Stock

    if request.user.has_perm('catalog.add_stock')\
    or request.user.has_perm('catalog.change_stock')\
    or request.user.has_perm('catalog.delete_stock'):

        stocks = Stock.objects.all().order_by('alias')

    return render(request, 'catalog/manage_stocks.html', locals())


def manage_vendors(request):
    "Представление: список производителей."

    from catalog.models import Vendor

    vendors = Vendor.objects.all().order_by('name')

    return render(request, 'catalog/manage_vendors.html', locals())


def manage_categories(request):
    "Представление: управление категорями."

    from catalog.models import Category

    categories = []
    categories = Category.objects.get_category_tree(categories)

    for category in categories:
        category.name = '— ' * category.level + category.name

    return render(request, 'catalog/manage_categories.html', locals())


def manage_products(request, **kwargs):
    'Представление: управление продуктами'

    from django.db.models import Q

    from catalog.models import Product, Category, Vendor

    # Получаем предварительные значения параметров из строки адреса
    # и, паралельно собираем базовый URL для Pagination
    parameters_ = {}
    url = '/catalog/manage/products/'
    for parameter in kwargs.get('string', '').split('/'):
        name = parameter.split('=')[0]
        try:
            values = parameter.split('=')[1]
        except IndexError:
            values = ''
        if name:
            parameters_[name] = values
        if name != 'page':
            url = '{}{}/'.format(url, parameter)

    # Очищаем значения параметров
    parameters = {}

    # Количество элементов на странице
    try:
        parameters['items'] = int(parameters_.get('items'))
    except Exception:
        parameters['items'] = 100
    if parameters['items'] < 1:
        parameters['items'] = 100

    # Номер страницы
    parameters['page'] = fix_parameter_page(parameters_.get('page'))

    # Категории
    parameters['category'] = fix_parameter_category(parameters_.get('category', ''))
    categories = Category.objects.get_category_tree([], state = True)

    # Производитель
    parameters['vendor'] = fix_parameter_vendor(parameters_.get('vendor', ''))
    vendors = Vendor.objects.filter(state = True, double = None)

    # Строка поиска
    parameters['search'] = fix_parameter_search(parameters_.get('search', ''))

    # Готовим фильтр для отбора продуктов
    filters_ = {'double': Q(double = None),
                'vendor_double': Q(vendor__double = None)}
    filters = {}

    if parameters['category'] or parameters['vendor'] or parameters['search']:

        if parameters['category']:
            filters['category'] = Q(category = parameters['category'])

        if parameters['vendor']:
            filters['vendor'] = Q(vendor = parameters['vendor'])

        if parameters['search']:

            translation_map = {ord('o'): '0', ord('е'): 'e', ord('т'): 't', ord('у'): 'y',
                               ord('о'): 'o', ord('р'): 'p', ord('а'): 'a', ord('н'): 'h',
                               ord('к'): 'k', ord('l'): 'i', ord('х'): 'x', ord('c'): 'c',
                               ord('в'): 'b', ord('м'): 'm'}

            filters['search'] = Q()

            for search in parameters['search']:

                search_ = search.translate(translation_map)

                filters['search'] = filters['search'] & (Q(alias__icontains = search) | Q(alias__icontains = search_))

    # Фильтруем
    products = Product.objects.all()
    for key in filters_:
        products = products.filter(filters_[key])
    for key in filters:
        products = products.filter(filters[key])

    # Требуется ли разбивка на страницы
    count = products.count()
    page_max = count // parameters['items']
    if count % parameters['items']:
        page_max += 1

    if page_max > 1:
        pages = []
        dispersion = 3
        prev = False
        for n in range(1, page_max + 1):

            # Добавляем номер страницы в ссылки
            if ((parameters['page'] - n) < dispersion and (n - parameters['page']) < dispersion)\
                or ((page_max - n) < dispersion and (n - page_max) < dispersion) \
                or ((1 - n) < dispersion and (n - 1) < dispersion):
                    pages.append(n)
                    prev = True
            # Будем добавлять многоточие
            elif prev:
                pages.append(0)
                prev = False

        first = (parameters['page'] - 1) * parameters['items']
        last = parameters['page']*parameters['items']

        if parameters['page'] > 1:
            page_prev = parameters['page'] - 1
        if parameters['page'] < page_max:
            page_next = parameters['page'] + 1

        products = products[first : last]

    else:
        first = 0
        last = count

    # Нумеруем
    for n in range(len(products)):
        products[n].n = n + first + 1

    return render(request, 'catalog/manage_products.html', locals())


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


def products(request, **kwargs):
    "Представление: список продуктов."

    import unidecode
    from lxml import etree
    from django.db.models import Q

    from catalog.models import Product, Category, Vendor

    # Получаем предварительные значения параметров из строки адреса
    # и, паралельно собираем базовый URL для Pagination
    parameters_ = {}
    url = '/catalog/products/'
    for parameter in kwargs.get('string', '').split('/'):
        name = parameter.split('=')[0]

        try:
            values = parameter.split('=')[1]
        except IndexError:
            values = ''

        if name:
            parameters_[name] = values

        if name != 'page':
            url = '{}{}/'.format(url, parameter)

    # Очищаем значения параметров
    parameters = {}

    # Количество элементов на странице
    try:
        parameters['items'] = int(parameters_.get('items'))
    except Exception:
        parameters['items'] = 100
    if parameters['items'] < 1:
        parameters['items'] = 100

    # Номер страницы
    parameters['page'] = fix_parameter_page(parameters_.get('page'))

    # Категории
    # Дерево всех категорий (список)
    categories = Category.objects.get_category_tree([], state = True)

    # Дерево всех категорий (HTML)
    root = etree.Element("div")
    Category.objects.get_category_tree_html(root, parent = None, first = True, state = True)
    categories_tree = etree.tostring(root)

    # Список категорий для фильтра
    parameters_['categories'] = parameters_.get('categories', '').split(',')
    parameters['categories'] = []
    for category in categories:
        for id_ in parameters_['categories']:
            if id_ == None:
                parameters['categories'].append(None)
            else:
                try:
                    if category.id == int(id_):
                        parameters['categories'].append(category)
                except Exception:
                    pass

    # Производители
    # Список всех производителей
    vendors = Vendor.objects.filter(state=True)

    # Список отфильтрованных производителей
    parameters_['vendors'] = parameters_.get('vendors', '').split(',')
    parameters['vendors'] = []
    for vendor in vendors:
        for alias_ in parameters_['vendors']:
            if vendor.alias == str(alias_):
                parameters['vendors'].append(vendor)

    # Строка поиска
    parameters_['search'] = str(parameters_.get('search', ''))
    if parameters_['search']:

        translation_map = {ord('&') : 'and', ord('\'') : '', ord('(') : ' ', ord(')') : ' ',
                           ord('[') : ' ', ord(']') : ' ', ord('.') : ' ', ord(',') : ' ',
                           ord('+') : ' ', ord('/') : ' '}
        parameters_['search'] = parameters_['search'].translate(translation_map)

        parameters_['search'] = parameters_['search'].strip().lower()

    parameters['search'] = []
    for word in parameters_['search'].split(' '):
        if word:
            parameters['search'].append(word)

    parameters_['search'] = str(parameters_.get('search', ''))

    # TODO Параметры товара для фильтра

    # Готовим фильтр для отбора продуктов
    filters_ = {'state': Q(state = True),
                'double': Q(double = None),
                'vendor_state': Q(vendor__state = True),
                'vendor_double': Q(vendor__double = None)}
    filters = {}

    if parameters['categories'] or parameters['vendors'] or parameters['search']:

        if parameters['categories']:
            filters['categories'] = Q()
            for category in parameters['categories']:
                filters['categories'] = filters['categories'] | Q(category = category)

        if parameters['vendors']:
            filters['vendors'] = Q()
            for vendor in parameters['vendors']:
                filters['vendors'] = filters['vendors'] | Q(vendor = vendor)

        if parameters['search']:

            translation_map = {ord('o'): '0', ord('е'): 'e', ord('т'): 't', ord('у'): 'y',
                               ord('о'): 'o', ord('р'): 'p', ord('а'): 'a', ord('н'): 'h',
                               ord('к'): 'k', ord('l'): 'i', ord('х'): 'x', ord('c'): 'c',
                               ord('в'): 'b', ord('м'): 'm'}

            filters['search'] = Q()

            for search in parameters['search']:

                search_ = search.translate(translation_map)

                filters['search'] = filters['search'] & (Q(alias__icontains = search) | Q(alias__icontains = search_))

        # Фильтруем
        if len(filters):
            products = Product.objects.all()
            for key in filters_:
                products = products.filter(filters_[key])
            for key in filters:
                products = products.filter(filters[key])

            # Требуется ли разбивка на страницы
            count = products.count()
            page_max = count // parameters['items']
            if count % parameters['items']:
                page_max += 1

            if page_max > 1:

                pages = []
                dispersion = 3
                prev = False
                for n in range(1, page_max + 1):

                    # Добавляем номер страницы в ссылки
                    if ((parameters['page'] - n) < dispersion and (n - parameters['page']) < dispersion)\
                        or ((page_max - n) < dispersion and (n - page_max) < dispersion) \
                        or ((1 - n) < dispersion and (n - 1) < dispersion):
                            pages.append(n)
                            prev = True
                    # Будем добавлять многоточие
                    elif prev:
                        pages.append(0)
                        prev = False

                first = (parameters['page'] - 1) * parameters['items']
                last = parameters['page']*parameters['items']

                if parameters['page'] > 1:
                    page_prev = parameters['page'] - 1
                if parameters['page'] < page_max:
                    page_next = parameters['page'] + 1

                products = products[first : last]

            else:
                first = 0
                last = count

            # Нумеруем
            for n in range(len(products)):
                products[n].n = n + first + 1

            if not count:
                from anodos.models import Log
                if request.user.id:
                    user_name = '{} {}'.format(request.user.first_name, request.user.last_name)
                else:
                    user_name = 'AnonymousUser'
                Log.objects.add(subject = "catalog.views.products",
                                channel = "info",
                                title = "Not found",
                                description = '{}: {}'.format(user_name, parameters_['search']))
    else:
       products = []

    return render(request, 'catalog/products.html', locals())


def product(request, id = None, vendor = None, article = None):
    "Представление: продукт."

    from catalog.models import Vendor, Product, ParameterToProduct, ProductPhoto

    if id:
        product = Product.objects.get(id=id)
    elif vendor and article:
        vendor = Vendor.objects.get(alias=vendor)
        product = Product.objects.get(vendor=vendor, article=article)

    parameters = ParameterToProduct.objects.filter(product = product)
    photos     = ProductPhoto.objects.filter(product = product)

    return render(request, 'catalog/product.html', locals())


def parametertypes(request):
    "Представление: список типов данных параметров."

    from catalog.models import ParameterType

    parametertypes = ParameterType.objects.all().order_by('name')

    return render(request, 'catalog/parametertypes.html', locals())


def parameters(request):
    "Представление: список параметров."

    from catalog.models import Parameter, ParameterType, Unit

    parameters = Parameter.objects.all().order_by('name')
    parametertypes = ParameterType.objects.all().order_by('name')
    units = Unit.objects.all().order_by('name')

    return render(request, 'catalog/parameters.html', locals())


def parametervalues(request):
    "Представление: список значений параметров."

    from catalog.models import ParameterValue

    parameter_values = ParameterValue.objects.all()

    return render(request, 'catalog/parametervalues.html', locals())


def parametervaluesynonyms(request, updater_selected = 'all', parameter_selected = 'all'):
    "Представление: список синонимов значений параметров."

    from catalog.models import ParameterValueSynonym, Parameter,\
            ParameterValue, Updater

    if updater_selected != 'all':
        updater_selected = int(updater_selected)
    if parameter_selected != 'all':
        parameter_selected = int(parameter_selected)

    if request.user.has_perm('catalog.add_parametervaluesynonym')\
    or request.user.has_perm('catalog.change_parametervaluesynonym')\
    or request.user.has_perm('catalog.delete_parametervaluesynonym'):

        parametervaluesynonyms = ParameterValueSynonym.objects.select_related().all()

        if updater_selected and updater_selected != 'all':
            parametervaluesynonyms = parametervaluesynonyms.select_related().filter(
                updater = updater_selected)
        if not updater_selected:
            parametervaluesynonyms = parametervaluesynonyms.select_related().filter(
                updater = None)

        if parameter_selected and parameter_selected != 'all':
            parametervaluesynonyms = parametervaluesynonyms.select_related().filter(
                parameter = parameter_selected)
        if not parameter_selected:
            parametervaluesynonyms = parametervaluesynonyms.select_related().filter(
                parameter = None)

        updaters        = Updater.objects.select_related().all()
        parameters      = Parameter.objects.select_related().all()
        parametervalues = ParameterValue.objects.select_related().all()

    return render(request, 'catalog/parametervaluesynonyms.html', locals())


def parametersynonyms(request, updater_selected = 'all', parameter_selected = 'all'):
    "Представление: список синонимов параметров."

    from catalog.models import ParameterSynonym, Parameter, Updater,\
            ParameterType, Unit

    if updater_selected != 'all':
        updater_selected = int(updater_selected)
    if parameter_selected != 'all':
        parameter_selected = int(parameter_selected)

    if request.user.has_perm('catalog.add_parametersynonym')\
    or request.user.has_perm('catalog.change_parametersynonym')\
    or request.user.has_perm('catalog.delete_parametersynonym'):

        parametersynonyms = ParameterSynonym.objects.select_related().all()

        if updater_selected and updater_selected != 'all':
            parametersynonyms = parametersynonyms.select_related().filter(
                updater = updater_selected)
        if not updater_selected:
            parametersynonyms = parametersynonyms.select_related().filter(
                updater = None)

        if parameter_selected and parameter_selected != 'all':
            parametersynonyms = parametersynonyms.select_related().filter(
                parameter = parameter_selected)
        if not parameter_selected:
            parametersynonyms = parametersynonyms.select_related().filter(
                parameter = None)

        updaters       = Updater.objects.select_related().all()
        parameters     = Parameter.objects.select_related().all()
        parametertypes = ParameterType.objects.select_related().all()
        units          = Unit.objects.select_related().all()

    return render(request, 'catalog/parametersynonyms.html', locals())


def ajax_get(request, *args, **kwargs):
    "AJAX-представление: Get Object."

    import json
    import catalog.models

    model_name = kwargs.get('model_name', '')

    model = catalog.models.models[model_name]

    if (not request.is_ajax()) or (request.method != 'POST'):
        return HttpResponse(status=400)

    open_models = ['product', 'vendor', 'category']

    if not model_name in open_models:
        if not request.user.has_perm('catalog.change_{}'.format(kwargs['model_name']))\
        or not request.user.has_perm('catalog.delete_{}'.format(kwargs['model_name'])):
            return HttpResponse(status = 403)

    try:
        m = model.objects.get(id = request.POST.get('id'))

        result = {
            'status': 'success',
            kwargs['model_name']: m.get_dicted()}

    except model.DoesNotExist:
        result = {
            'status': 'alert',
            'message': 'Ошибка: объект отсутствует в базе.',
            'id': request.POST.get('id')}

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

        elif key == 'updater_id':
            try:
                m = catalog.models.models['updater']
                o.updater = m.objects.get(id = request.POST.get(key, ''))
            except Exception:
                o.updater = None

        elif key == 'unit_id':
            try:
                m = catalog.models.models['unit']
                o.unit = m.objects.get(id = request.POST.get(key, ''))
            except Exception:
                o.unit = None

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

            old_category = o.category

            try:
                m = catalog.models.models['category']
                o.category = m.objects.get(id = request.POST.get(key, ''))
            except Exception:
                o.category = None

            if o.category != old_category:
                result['reload'] = True

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

        elif key == 'duble_id' and kwargs['model_name'] == 'product':
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


def ajax_link(request, *args, **kwargs):
    "AJAX-представление: Link Model."

    import json
    from django.utils import timezone
    import catalog.models

    if (not request.is_ajax()) or (request.method != 'POST'):
        return HttpResponse(status=400)

    if not request.user.has_perm('catalog.change_{}'.format(kwargs['model_name']))\
    or not request.user.has_perm('catalog.add_{}'.format(kwargs['model_name'])):
        return HttpResponse(status = 403)

    model = catalog.models.models[kwargs['model_name']]

    # Получаем исходный объект
    try:
        o = model.objects.get(id = request.POST.get('id'))
    except Exception:
        result = {'status': 'alert',
                  'message': 'Ошибка: объект отсутствует в базе.'}
        return HttpResponse(json.dumps(result), 'application/javascript')

    # Определяем имя
    name = request.POST.get('name', '')

    # Получаем объект ссылки
    double = model.objects.take(name, get_doubles = False)

    # Переименовываем или,
    # при необходимости, привязываем объект
    if o.id == double.id:
        o.double = None
        o.state = True
        o.name = name
        o.save()
    else:
        o.double = double
        o.state = False
        o.save()
        double.name = name
        double.save()

    # TODO Прописать алгоритм, что делать с товаром

    result = {
        'status'               : 'success',
        kwargs['model_name']   : o.get_dicted()
    }

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
        if kwargs['foreign_name'] == 'parametervalue':
            f.order = 0
            f.parameter = o.parameter

        f.save()

    if kwargs['foreign_name'] == 'vendor':
        o.vendor = f
#    elif kwargs['foreign_name'] == 'category':
#        o.category = f
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

    import json

    from catalog.models import Product, Party

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
    alias = alias.replace('.', '')
    alias = alias.strip()[:100]
    return alias

def fix_parameter_page(page):

    try:
        page = int(page)
    except Exception:
        page = 1
    if page < 1:
        page = 1
    return page


def fix_parameter_category(category):

    from catalog.models import Category
    try:
        category = int(category)
    except Exception:
        category = None
    if category:
        category = Category.objects.get(id = category)
    return category


def fix_parameter_vendor(vendor):

    from catalog.models import Vendor
    try:
        vendor = str(vendor)
    except Exception:
        vendor = None
    if vendor:
        vendor = Vendor.objects.get(alias = vendor)
    return vendor


def fix_parameter_search(string):

    string = str(string)
    if string:
        translation_map = {ord('&') : 'and', ord('\'') : '', ord('(') : ' ', ord(')') : ' ',
                           ord('[') : ' ', ord(']') : ' ', ord('.') : ' ', ord(',') : ' ',
                           ord('+') : ' ', ord('/') : ' '}
        string = string.translate(translation_map)
        string = string.strip().lower()
    words = []
    for word in string.split(' '):
        if word:
            words.append(word)
    return words
