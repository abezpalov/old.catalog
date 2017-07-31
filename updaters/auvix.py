# TODO Описсание товара с b2b
# TODO Фотографии товара с b2b

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name  = 'Auvix'
    alias = 'auvix'
    url   = {'start': 'https://b2b.auvix.ru/',
             'login': 'https://b2b.auvix.ru/?login=yes',
             'price': 'https://b2b.auvix.ru/prices/Price_AUVIX_dealer_xml.zip'}

    def __init__(self):

        super().__init__()

        self.stock   = self.take_stock('stock',   'склад', 3, 10)
        self.factory = self.take_stock('factory', 'на заказ', 20, 80)

    def run(self):

        # Авторизуемся
        self.login({'AUTH_FORM'     : 'Y',
                    'TYPE'          : 'AUTH',
                    'backurl'       : '/',
                    'USER_LOGIN'    : self.updater.login,
                    'USER_PASSWORD' : self.updater.password,
                    'Login'         : '%C2%A0',
                    'USER_REMEMBER' : 'Y'})

        # Загружаем данные
        self.data = self.load_data(self.url['price'])
        self.data = self.unpack_xml(self.data)
        if self.data is None:
            return None

        # Парсим
        self.parse(self.data)

        # Чистим партии
        Party.objects.clear(stock = self.stock,   time = self.start_time)
        Party.objects.clear(stock = self.factory, time = self.start_time)

        # Пишем результат в лог
        self.log()

    def parse(self, tree):

        import re

        currency = {
            'USD'   : self.usd,
            'Евро'  : self.eur,
            'Рубль' : self.rub}

        for group in tree.xpath('.//Группа'):

            self.reg = re.compile('\[(?P<article>[0-9A-Za-z\.\-\_ ]+)\]')

            category = self.xpath_string(group, './Наименование')

            for element in group.xpath('./Товары/Товар'):

                # Временные значения
                product_ = {}
                party_ = {}

                # Производитель
                product_['vendor'] = self.xpath_string(element, './Производитель')
                product_['vendor'] = Vendor.objects.take(product_['vendor'])

                # Продукт
                product_['name'] = self.xpath_string(element, './Наименование')
                product_['name'] = self.fix_name(product_['name'])

                product_['article'] = self.xpath_string(element, './Модель')
                product_['article_alt'] = re.search(self.reg, self.xpath_string(element, './Наименование'))
                if product_['article_alt']:
                    product_['article'] = product_['article_alt'].group('article')
                product_['article'] = self.fix_article(product_['article'])

                try:
                    product = Product.objects.take(article  = product_['article'],
                                                   vendor   = product_['vendor'],
                                                   name     = product_['name'],
                                                   category = category)
                    self.products.append(product.id)
                except ValueError as error:
                    continue

                # Партии
                party_['article'] = self.xpath_string(element, './Артикул')
                party_['article'] = self.fix_article(party_['article'])

                party_['quantity'] = self.xpath_string(element, './Количество')
                party_['quantity'] = self.fix_quantity(party_['quantity'])

                party_['currency'] = self.xpath_string(element, './Валюта')
                if party_['currency']:
                    party_['currency'] = currency[party_['currency']]
                else:
                    party_['currency'] = None

                party_['price_in'] = self.xpath_string(element, './Цена_3')
                party_['price_in'] = self.fix_price(party_['price_in'])

                party_['price_out'] = self.xpath_string(element, './Цена_1')
                party_['price_out'] = self.fix_price(party_['price_out'])

                try:
                    party = Party.objects.make(product    = product,
                                               stock      = self.stock,
                                               price      = party_['price_in'],
                                               currency   = party_['currency'],
                                               quantity   = party_['quantity'],
                                               time       = self.start_time)
                    self.parties.append(party.id)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product    = product,
                                               stock      = self.factory,
                                               price      = party_['price_in'],
                                               currency   = party_['currency'],
                                               quantity   = None,
                                               time       = self.start_time)
                    self.parties.append(party.id)
                except ValueError as error:
                    pass
