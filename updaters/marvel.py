""" Updater.Marvel
    API поставщика имеет странные ограничения на время между запросами.
"""

import time

import catalog.runner
from catalog.models import *
from anodos.models import Log


class Runner(catalog.runner.Runner):

    name  = 'Marvel'
    alias = 'marvel'

    url = 'https://b2b.marvel.ru/Api/'


    def __init__(self):

        super().__init__()

        self.stock_msk = self.take_stock('stock-msk', 'склад в Москве', 3, 10)
        self.stock_spb = self.take_stock('stock-spb', 'склад в Санкт-Петербурге', 3, 10)

        # Дополнительные переменные
        # TODO ??
        self.key = ''
        self.task = {'categories': 'GetCatalogCategories',
                     'catalog': 'GetFullStock',
                     'parameters': 'GetItems',
                     'photos': 'GetItemPhotos'}
        self.request_format = {'xml': '0', 'json': '1'}
        self.cookies = None
        self.categories = {}
        self.currencies = {'RUB': self.rub,
                           'RUR': self.rub,
                           'USD': self.usd,
                           'EUR': self.eur,
                           '': None}
        self.stocks = {'msk' : self.stock_msk, 'spb' : self.stock_spb}

    def run(self):

        # Проверяем наличие параметров авторизации
        if not self.updater.login or not self.updater.password:
            raise(ValueError('Ошибка: Проверьте параметры авторизации. Кажется их нет.'))

        # Загружаем и парсим категирии
        data = self.get_data('categories', 'json')
        self.parse_categories(data)

        # Загружаем и парсим каталог
        data = self.get_data('catalog', 'json')
        self.parse_catalog(data)

        # Чистим партии
        Party.objects.clear(stock = self.stock_msk, time = self.start_time)
        Party.objects.clear(stock = self.stock_spb, time = self.start_time)

        self.log()

    def get_data(self, task, request_format, pack_status = None, articles = None):

        import requests

        # Создаем сессию
        s = requests.Session()

        # Собираем URL
        if not pack_status is None:
            url = '{url}{task}?user={login}&password={password}&secretKey={key}&packStatus={pack_status}&responseFormat={request_format}'.format(
                url            = self.url,
                task           = self.task[task],
                login          = self.updater.login,
                password       = self.updater.password,
                key            = None,
                pack_status    = pack_status,
                request_format = self.request_format[request_format])
        else:
            url = '{url}{task}?user={login}&password={password}&secretKey={key}&responseFormat={request_format}'.format(
                url            = self.url,
                task           = self.task[task],
                login          = self.updater.login,
                password       = self.updater.password,
                key            = None,
                request_format = self.request_format[request_format])

        if articles:

            # Готовим начало
            url = '{url}{mid}'.format(
                url = url,
                mid = '&getExtendedItemInfo=1&items={"WareItem": [')

            # Добавляем артикулы
            for article in articles:
                url = '{url}{mid}{article}{end}'.format(
                    url     = url,
                    mid     = '{"ItemId": "',
                    article = article,
                    end     = '"},')

            # Удаляем лишнюю запятую
            url = url[0 : len(url) - 1]

            # Добавляем конец
            url = '{url}{end}'.format(
                url = url,
                end = ']}')

        # Выполняем запрос
        try:
            r = s.post(url, cookies = self.cookies, verify = False, timeout = 300)
        except Exception:
            print('Нет соединения')
            return False
        else:

            # Обрабатываем ответ
            if 'json' == request_format:

                import json

                try:
                    data = json.loads(r.text)
                except Exception:
                    return False

                if data['Header']['Key']: self.key = data['Header']['Key']
                if data['Header']['Code'] != 0:

                    if data['Header']['Message']:
                        Log.objects.add(
                        subject     = "catalog.updater.{}".format(self.updater.alias),
                        channel     = "error",
                        title       = "?",
                        description = data['Header']['Message'])
                    else:
                        Log.objects.add(
                        subject     = "catalog.updater.{}".format(self.updater.alias),
                        channel     = "error",
                        title       = "?",
                        description = "Невнятный ответ сервера")

                    raise(ValueError('Ошибка! Данные не получены.'))

                    return False
                else:
                    return data['Body']
            else:
                raise(ValueError('Ошибка: используется неподдерживаемый формат.'))

    def parse_categories(self, data):

        for category in data['Categories']:
            self.parse_category(category)

    # Используется рекурсия
    def parse_category(self, category):

        category_id = category['CategoryID']
        parent_id = category['ParentCategoryId']

        # Имя
        category_name = category['CategoryName']
        if parent_id:
            category_name = "{} | {}".format(self.categories[parent_id], category_name)

        # Добавляем в словарь
        self.categories[category_id] = category_name

        # Проходим рекурсивно по подкатегориям
        for sub_category in category['SubCategories']:
            self.parse_category(sub_category)

    def parse_catalog(self, data):

        # Проходим по категориям
        for item in data['CategoryItem']:

            product_ = {}
            party_ = {}

            # Продукт
            product_['article'] = item['WareArticle']
            product_['name'] = item['WareFullName']

            try:
                product_['category'] = self.categories[item['CategoryId']]
            except KeyError:
                product_['category'] = None

            product_['vendor'] = item['WareVendor']
            product_['vendor'] = self.fix_name(product_['vendor'])
            product_['vendor'] = Vendor.objects.take(product_['vendor'])

            try:
                product = Product.objects.take(article = product_['article'],
                                               vendor = product_['vendor'],
                                               name = product_['name'],
                                               category = product_['category'])
                self.products.append(product)
            except ValueError as error:
                continue
            except TypeError:
                print(product_)

            party_['price'] = item['WarePrice']
            party_['price'] = self.fix_price(party_['price'])

            party_['currency'] = self.currencies[item['WarePriceCurrency']]

            party_['quantity_msk'] = item['AvailableForShippingInMSKCount']
            party_['quantity_msk'] = self.fix_quantity(party_['quantity_msk'])

            party_['quantity_spb'] = item['AvailableForShippingInSPBCount']
            party_['quantity_spb'] = self.fix_quantity(party_['quantity_spb'])

            try:
                party = Party.objects.make(product = product,
                                           stock = self.stock_msk,
                                           price = party_['price'],
                                           currency = party_['currency'],
                                           quantity = party_['quantity_msk'],
                                           time = self.start_time)
                self.parties.append(party)
            except ValueError as error:
                pass

            try:
                party = Party.objects.make(product = product,
                                           stock = self.stock_spb,
                                           price = party_['price'],
                                           currency = party_['currency'],
                                           quantity = party_['quantity_spb'],
                                           time = self.start_time)
                self.parties.append(party)
            except ValueError as error:
                pass

    def parse_parameters(self, data, products):

        for pr in data['CategoryItem']:

            try:
                product = products[pr['WareArticle']]
                ps = data['CategoryItem'][0]['ExtendedInfo']['Parameter']

            except Exception:
                print('Error?')
                continue

            else:

                for p in ps:

                    name  = p['ParameterName']
                    value = p['ParameterValue']
#                    print('\t{} = {}'.format(name, value))

                    parameter_synonym = self.take_parametersynonym(name)

                    parameter = parameter_synonym.parameter

                    if parameter:
#                        print('Распознан параметр: {} = {}.'.format(parameter.name, value))
                        parameter_to_product = ParameterToProduct.objects.take(
                            parameter = parameter,
                            product   = product)
                        parameter_to_product.set_value(
                            value = value,
                            updater = self.updater)

        return True


    def parse_photos(self, data, products):

        for pr in data['Photo']:

            product = products[pr['BigImage']['WareArticle']]
            source  = pr['BigImage']['URL']

            photo = ProductPhoto.objects.load(product = product, source = source)
