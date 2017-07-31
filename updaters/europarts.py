import re
import time

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name = 'EuroParts'
    alias = 'europarts'
    url = {'start': 'http://euro-parts.ru/catalog/index.aspx',
           'base': 'http://euro-parts.ru',
           'price': 'http://euro-parts.ru/catalog/index.aspx'}

    def __init__(self):

        super().__init__()

        self.stock = self.take_stock('stock', 'склад', 3, 10)
        self.transit = self.take_stock('transit', 'транзит', 20, 60)

    def run(self):

        # Заходим на начальную страницу
        tree = self.load_html(self.url['price'])

        # Проходим по всем категориям
        cs = tree.xpath('//div[@id="categories"]//ul[@class="list"]/li/a')
        for n, c in enumerate(cs):

            # Ждем, чтобы не получить отбой сервера
            time.sleep(1)

            category = str(c.text)

            # Загружаем список моделей
            c_url = self.xpath_string(c, './@href')
            c_url = '{}{}'.format(self.url['base'], c_url)
            tree = self.load_html(c_url)

            # Проходим по всем моделям
            ms = tree.xpath('//div[@class="catalog-list"]//a/@href')

            if not len(ms):
                self.parse(tree, category)
                continue

            for m_url in ms:

                # Ждем, чтобы не получить отбой сервера
                time.sleep(1)

                m_url = '{}{}'.format(self.url['base'], m_url)
                tree = self.load_html(m_url)

                self.parse(tree, category)


        # Чистим устаревшие партии
        Party.objects.clear(stock = self.stock, time = self.start_time)

        # Пишем результат в лог
        self.log()


    def parse(self, tree, category):

        # Проходим по всем строкам
        rows = tree.xpath('.//div[@class="rows"]/ul[@class="row"]')
        for row in rows:

            product_ = {}
            party_ = {}

            # Продукт
            product_['article'] = self.xpath_string(row, './/li[@class="title"]/span/input/@value')
            product_['article'] = self.fix_article(product_['article'])

            product_['name'] = self.xpath_string(row, './/li[@class="title"]/small[@class="name"]/a')
            product_['name'] = self.fix_name(product_['name'])

            product_['url'] = self.xpath_string(row, './/li[@class="title"]/small[@class="name"]/a/@href')
            product_['url'] = self.fix_url(product_['url'])

            product_['vendor'] = self.xpath_string(row, './/li[@class="brand"]')
            product_['vendor'] = Vendor.objects.take(product_['vendor'])

            try:
                product = Product.objects.take(article = product_['article'],
                                               vendor = product_['vendor'],
                                               name = product_['name'],
                                               category = category,
                                               test = self.test)

                # Один продукт может встречаться в разных моделях, поэтому:
                # проверяем, не обработан ли уже этот продукт
                if product.id in self.products:
                    continue
                self.products.append(product.id)
            except ValueError as error:
                continue

            # Партии
            party_['price'] = self.get_price(row.get('data'))
            party_['quantity'] = self.xpath_string(row, './/li[@class="stock"]')
            party_['quantity_stock'] = self.fix_quantity_stock(party_['quantity'])
            party_['quantity_transit'] = self.fix_quantity_transit(party_['quantity'])

            try:
                party = Party.objects.make(product = product,
                                           stock = self.stock,
                                           price = party_['price'],
                                           currency = self.usd,
                                           quantity = party_['quantity_stock'],
                                           time = self.start_time,
                                           test = self.test)
                self.parties.append(party.id)
            except ValueError as error:
                pass

            try:
                party = Party.objects.make(product = product,
                                           stock = self.transit,
                                           price = party_['price'],
                                           currency = self.usd,
                                           quantity = party_['quantity_transit'],
                                           time = self.start_time,
                                           test = self.test)
                self.parties.append(party.id)
            except ValueError as error:
                pass

    def fix_quantity_stock(self, quantity):

        if 'Уточняйте' in quantity:
            return None
        elif 'Да' in quantity:
            return 1
        else:
            return 0

    def fix_quantity_transit(self, quantity):

        if 'Транзит' in quantity:
            return None
        else:
            return 0

    def get_price(self, data):

        # Регулярное выражение
        # Из строки '{price: {rur: 15099, usd: 227.87}}'
        # достать 227.87

        price = re.search(re.compile('usd: (?P<price>[0-9\.]+)'), data)

        try:
            return float(price.group('price'))
        except Exception:
            return None
