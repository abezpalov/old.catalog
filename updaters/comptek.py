# TODO Описание и фотографии товара с сайте

import time

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name = 'Comptek'
    alias = 'comptek'
    url = {'start'    : 'http://comptek.ru/',
           'login'    : 'http://comptek.ru/personal/auth.xhtml',
           'price'    : 'http://comptek.ru/',
           'filter'   : 'catalog/',
           'unfilter' : 'item/',
           'base'     : 'http://comptek.ru'}

    def __init__(self):

        super().__init__()

        self.stock    = self.take_stock('stock', 'склад', 3, 10)
        self.transit  = self.take_stock('transit', 'транзит', 10, 60)
        self.on_order = self.take_stock('on-order', 'на заказ', 40, 80)

    def run(self):

        # Авторизуемся
        self.login({'login'    : self.updater.login,
                    'password' : self.updater.password})

        # Заходим на начальную страницу
        tree = self.load_html(self.url['price'])

        # Проходим по всем ссылкам
        urls = []

        # Добавляем ссылки с начальной страницы в очередь
        for url in tree.xpath('//a/@href'):
            if 'http' not in url and 'mailto:' not in url:
                url = self.url['base'] + url
            if not url in urls:
                urls.append(url)

        i = 0
        while i < len(urls):

            # Проверяем, является ли ссылка на список товаров
            if self.url['filter'] in urls[i] and self.url['unfilter'] not in urls[i]:

                # Определяем производителя
                vendor = Vendor.objects.take(self.fix_name(urls[i].split('/')[4]))

                # Загружаем страницу
                tree = self.load_html(urls[i])

                # Добавляем ссылки в очередь
                for url in tree.xpath('//a/@href'):
                    if 'http' not in url and 'mailto:' not in url:
                        url = self.url['base'] + url
                    if not url in urls:
                        urls.append(url)

                # Если производитель известен, парсим товары
                if vendor:
                    self.parse(tree, vendor)

                # Ждем, чтобы не получить отбой сервера
                time.sleep(1)

            i += 1

        # Чистим партии
        Party.objects.clear(stock = self.stock, time = self.start_time)
        Party.objects.clear(stock = self.transit, time = self.start_time)
        Party.objects.clear(stock = self.on_order, time = self.start_time)

        self.log()

    def parse(self, tree, vendor):


        # Номера строк и столбцов
        num = {
            'product_article': 0,
            'product_name':    1,
            'stock':           3,
            'transit':         4,
            'price':           5}

        table = tree.xpath('//table[@class="list-table"]//tr')

        # Проходим по строкам таблицы
        for trn, tr in enumerate(table):

            if trn:

                # Временные значения
                product_ = {}
                party_ = {}

                product_['article'] = self.xpath_string(tr, './td[@class="art"]')
                product_['article'] = self.fix_article(product_['article'])

                product_['name'] = self.xpath_string(tr, './td[@class="prod-name"]/a')
                product_['name'] = self.fix_name(product_['name'])

                product_['url'] = self.xpath_string(tr, './td[@class="prod-name"]/a/@href')
                product_['url'] = self.fix_url(product_['url'])

                party_['on_stock']   = self.xpath_int(tr, ('./td', './span/@class'), index = 2) # TODO
                party_['on_transit'] = self.xpath_int(tr, ('./td', './span/@class'), index = 3) # TODO
#                party_['on_order']   = self.get_int(tr, ('./td', './span/@class'), index = 4) # TODO
                party_['price']      = self.xpath_float(tr, './td', index = 5)
                party_['currency']   = self.xpath_currency(tr, ('./td', './span/@class'), index = 5)

                try:
                    product = Product.objects.take(article = product_['article'],
                                                   vendor = vendor,
                                                   name = product_['name'])
                    self.products.append(product)
                except ValueError as error:
                    continue

                try:
                    party = Party.objects.make(product    = product,
                                               stock      = self.stock,
                                               price      = party_['price'],
                                               currency   = party_['currency'],
                                               quantity   = party_['on_stock'],
                                               time       = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product    = product,
                                               stock      = self.transit,
                                               price      = party_['price'],
                                               currency   = party_['currency'],
                                               quantity   = party_['on_transit'],
                                               time       = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product    = product,
                                               stock      = self.on_order,
                                               price      = party_['price'],
                                               currency   = party_['currency'],
                                               quantity   = None,
                                               time       = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass

    def xpath_currency(self, element, query, index = 0):

        result = None

        try:
            text = element.xpath(query[0])[index].text
        except Exception:
            return None

        if not text:
            result = None
        elif '₽' in text:
            result = self.rub
        elif '$' in text:
            result = self.usd

        else:
            try:
                text = element.xpath(query[0])[index].xpath(query[1])[0]
            except Exception:
                return None

            if 'rub' in text:
                result = self.rub
            elif 'usd' in text:
                result = self.usd

        return result

    def xpath_int(self, element, query, index = 0):

        i = super().xpath_int(element, query[0], index)

        if i == 0:

            try:
                text = element.xpath(query[0])[index].xpath(query[1])[0]
            except Exception:
                return i

            if 'small-qty' in text:
                i = 2
            elif 'normal-qty' in text:
                i = 5
            elif 'big-qty' in text:
                i = 10
            elif 'all-reserv' in text:
                i = None
            else:
                i = 0

        return i


    def fix_string(self, string):

        super().fix_string(string)

        blacklist = ['files', ]

        if string in blacklist:
            string = ''

        return string
