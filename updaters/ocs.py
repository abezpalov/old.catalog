""" Updater.OCS
    API поставщика работает только с разрешёнными IP-адресами.
"""

import catalog.runner
from catalog.models import *

class Runner(catalog.runner.Runner):

    name = 'OCS'
    alias = 'ocs'

    url = 'https://b2bservice.ocs.ru/b2bJSON.asmx/'

    def __init__(self):

        super().__init__()

        self.stocks = {'Самара': self.take_stock('stock-samara', 'склад в Самаре', 1, 3),
                       'Саратов': self.take_stock('stock-saratov', 'склад в Саратове', 3, 10),
                       'Оренбург': self.take_stock('stock-orenburg', 'склад в Оренбурге', 3, 10),
                       'Казань': self.take_stock('stock-kazan', 'склад в Казани', 3, 10),
                       'Уфа': self.take_stock('stock-ufa', 'склад в Уфе', 3, 10),
                       'Нижний Новгород': self.take_stock('stock-nizhniy-novgorod', 'склад в Нижнем Новгороде', 3, 10),
                       'В пути': self.take_stock('transit', 'в пути', 10, 60),
                       'Транзит из ЦО': self.take_stock('transit-from-moskow', 'транзит со склада в Москве', 5, 20),
                       'ЦО (Москва)': self.take_stock('stock-moskow', 'склад в Москве', 3, 10),
                       'ЦО (СПб)': self.take_stock('stock-spb', 'склад в Санкт-Петербурге', 3, 10)}

    def run(self):

        import requests
        import json
        from django.utils import timezone

        categories = {}
        locations = []

        currencies = {'RUR': self.rub, 'RUB': self.rub, 'EUR': self.eur, 'USD': self.usd}

        # Получаем категории
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        payload = json.dumps({'Login': self.updater.login, 'Token': self.updater.password})
        try:
            r = requests.post(self.url + 'GetCatalog',
                              data = payload,
                              headers = headers,
                              verify = False,
                              timeout = 100.0)
        except requests.exceptions.Timeout:
            raise(ValueError('Ошибка! Превышен интервал ожидания загрузки категорий.'))
            return False

        for c in json.loads(r.text)['d']['Categories']:
            if c['ParentCategoryID']:
                categories[c['CategoryID']] = "{} | {}".format(
                    categories[c['ParentCategoryID']],
                    c['CategoryName'])
            else:
                categories[c['CategoryID']] = c['CategoryName']

        # Получаем локации
        payload = json.dumps({'Login': self.updater.login,
                              'Token': self.updater.password,
                              'Availability': 1,
                              'ShipmentCity': 'Самара'})
        try:
            r = requests.post(self.url + 'GetLocations',
                              data    = payload,
                              headers = headers,
                              verify  = False,
                              timeout = 100.0)
        except requests.exceptions.Timeout:
            raise(ValueError('Ошибка! Превышен интервал ожидания загрузки локаций.'))
            return False

        for l in json.loads(r.text)['d']['LocationList']:
            locations.append(l['Location'])

        # Получаем продукты
        payload = json.dumps({'Login': self.updater.login,
                              'Token': self.updater.password,
                              'Availability': 0,
                              'ShipmentCity': 'Самара',
                              'CategoryIDList': None,
                              'ItemIDList': None,
                              'LocationList': locations,
                              'DisplayMissing': 1})

        try:
            r = requests.post(self.url + 'GetProductAvailability',
                              data = payload,
                              headers = headers,
                              verify = False,
                              timeout = 100.0)
        except requests.exceptions.Timeout:
            raise(ValueError('Ошибка! Превышен интервал ожидания загрузки товаров.'))
            return False

        # Проходим по элементам списка продуктов
        for p in json.loads(r.text)['d']['Products']:

            product_ = {}
            party_ = {}

            # Продукт
            product_['article'] = self.fix_article(p['PartNumber'])
            product_['name'] = self.fix_name(p['ItemName'])
            try:
                product_['category'] = categories[p['CategoryID']]
            except KeyError:
                product_['category'] = self.fix_name(p['CategoryID'])
            product_['vendor'] = self.fix_name(p['Producer'])
            product_['vendor'] = Vendor.objects.take(product_['vendor'])

            try:
                product = Product.objects.take(article = product_['article'],
                                               vendor = product_['vendor'],
                                               name = product_['name'],
                                               category = product_['category'],
                                               test = self.test)
                self.products.append(product.id)
            except ValueError as error:
                continue

            # Партии
            party_['price'] = self.fix_price(p['Price'])

            try:
                party_['currency'] = currencies[p['Currency']]
            except KeyError:
                party_['currency'] = currencies['EUR']

            for l in p['Locations']:

                party_['stock'] = self.stocks[l['Location']]                
                party_['quantity'] = l['Quantity']

                try:
                    party = Party.objects.make(product = product,
                                               stock = party_['stock'],
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = party_['quantity'],
                                               time = self.start_time,
                                               test = self.test)
                    self.parties.append(party.id)
                except ValueError as error:
                    pass

        # Чистим партии
        for key in self.stocks:
            Party.objects.clear(stock = self.stocks[key], time = self.start_time)

        self.log()
