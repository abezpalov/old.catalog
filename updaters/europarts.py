import re
import time

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name = 'EuroParts'
    alias = 'europarts'
    test = True
    url = {'start' : 'http://euro-parts.ru/catalog/index.aspx',
           'base'  : 'http://euro-parts.ru',
           'price' : 'http://euro-parts.ru/catalog/index.aspx'}

    def __init__(self):

        super().__init__()

        self.stock = self.take_stock('stock', 'склад', 3, 10)

        self.reg = re.compile('usd: (?P<price>[0-9\.]+)')

    def run(self):

        # Заходим на начальную страницу
        tree = self.load_html(self.url['price'])

        # Проходим по всем производителям
        vs = tree.xpath('//ul[@class="list ul-brand-list"]/li')
        print('Производителей: {}'.format(len(vs)))

        for v in vs:

            print(type(v))

            vendor_ = {}
            vendor_['id'] = v.get('value')
            vendor_['name'] = v.xpath('.//span[@class="name"]')[0].text
            vendor = Vendor.objects.get_by_key(updater = self.updater, key = vendor_['name'])

            print('\n{} [{}]'.format(vendor_['name'], vendor_['id']))

            if vendor is None:
                print('vendor is None')
                continue

            # Проходим по всем категориям производителя
            try:
                div = tree.xpath('//div[@id="categories"]/div[@brandid="{}"]'.format(vendor_['id']))[0]
            except Exception:
                print('Exception in div = tree.xpath')
                continue

            cs = div.xpath('.//ul[@class="list"]/li')
            print('Категорий: {}'.format(len(cs)))

            for c in cs:

                category_ = {}
                category_['id']   = c.get('value')
                category_['name'] = c.xpath('.//a')[0].text
                category_['url']  = c.xpath('.//a')[0].get('href').replace('//', '/')

                print('\n{} [{}]'.format(category_['name'], category_['id']))

                url = '{}{}'.format(self.url['base'], category_['url'])

                tree = self.load_html(url)

                # Проходим по всем моделям
                ms = tree.xpath('//div[@class="catalog-list"]/ul/li')
                for m in ms:

                    model_ = {}
                    model_['id'] = m.get('modelid')
                    model_['name'] = m.xpath('.//a')[0].text
                    print('\n{}'.format(model_['name']))

                    url = '{}/actions/get_items.ashx?brandId={}&categoryId={}&modelId={}'.format(
                        self.url['base'],
                        vendor_['id'],
                        category_['id'],
                        model_['id'])
                    tree = self.load_html(url)

                    self.parse(tree, vendor, category_['name'])

        # Чистим устаревшие партии
        Party.objects.clear(stock = self.stock, time = self.start_time)

        # Пишем результат в лог
        self.log()


    def parse(self, tree, vendor, category):

        rows = tree.xpath('.//div[@class="rows"]/ul[@class="row"]')

        print('Позиций: {}'.format(len(rows)))

        for row in rows:

            product_ = {}
            party_ = {}

            # Получаем объект товара
#            try:

            product_['article'] = self.fix_article(row.xpath('.//li[@class="title"]/a')[0].text)
            product_['name'] = self.fix_name(row.xpath('.//li[@class="title"]/small[@class="name"]')[0].text)
#            except Exception as error:
#                if self.test:
#                    print(error)
#                    exit()
#                continue

            try:
                product = Product.objects.take(
                    article  = product_article,
                    vendor   = vendor,
                    name     = product_name,
                    category = category)
                self.products.append(product)
            except ValueError as error:
                if self.test:
                    print(error)
                    exit()
                continue

            if product in self.done:
                continue
            else:
                self.done.add(product)

            party_['quantity'] = self.fix_quantity(row.xpath('.//li[@class="stock"]')[0].text)
            party_['price'] = self.get_price(row.get('data'))

            # Добавляем партии
            party = Party.objects.make(
                product    = product,
                stock      = self.stock,
                price      = party_price,
                currency   = self.usd,
                quantity   = None,
                time       = self.start_time)

            if party_quantity:
                party = Party.objects.make(
                    product    = product,
                    stock      = self.stock,
                    article    = None,
                    price      = pary_price,
                    price_type = self.dp,
                    currency   = self.usd,
                    quantity   = party_quantity,
                    unit       = self.default_unit,
                    time       = self.start_time)

            product_link    = '{}{}'.format(
                self.url['base'], row.xpath('.//li[@class="title"]/a')[0].get('href'))

    def fix_quantity(self, quantity):

        quantity = str(quantity).strip()

        if 'Уточняйте' in quantity:
            return None
        elif 'Да' in quantity:
            return 1

    def get_price(self, data):

        # Регулярное выражение
        # Из строки '{price: {rur: 15099, usd: 227.87}}'
        # достать 227.87

        price = re.search(self.reg, data)

        try:
            return float(price.group('price'))
        except Exception:
            return None
