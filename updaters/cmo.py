# TODO Описание и фото товара с сайта

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):


    name  = 'ЦМО'
    alias = 'cmo'
    url   = {'start' : 'http://cmo.ru/',
             'price' : 'http://cmo.ru/price/',
             'base'  : 'http://cmo.ru'}

    def __init__(self):

        super().__init__()

        self.stock   = self.take_stock('factory', 'завод', 10, 20)

        self.vendor = Vendor.objects.take(self.name)
        self.rp = PriceType.objects.take(alias = 'RP', name = 'Розничная цена')

    def run(self):

        # Получаем HTML-данные
        r = self.load_cookie()
        tree = self.load_html(self.url['price'])

        self.parse(tree)

        # Чистим устаревшие партии
        Party.objects.clear(stock = self.stock, time = self.start_time)

        # Пишем в лог
        self.log()


    def parse(self, tree):

        # Номера строк и столбцов
        num = {'header': 0}

        # Распознаваемые слова
        word = {
            'article' : 'Артикул',
            'code'    : 'Код (ID)',
            'name'    : 'Наименование продукции'}

        # Проходим по таблицам
        for table in tree.xpath(".//div[@class='price-list']"):

            # Прохидим по группам
            for group in table.xpath(".//li[@id]"):

                # Определяем синоним категории
                category = self.xpath_string(group, './/div[@class="item-text-root"]')

                # Проходим по элементам
                for element in group.xpath(".//div[@class='item-text']"):

                    # Временные значения
                    product_ = {}
                    party_ = {}

                    # Артикулы
                    party_['article']   = self.fix_article(self.xpath_string(element, './/div[@class="service-num"]'))
                    product_['article'] = self.fix_article(self.xpath_string(element, './/div[@class="service-code"]'))

                    # Наименование
                    product_['name'] = self.xpath_string(element, './/div[@class="name-text"]/a')
                    product_['link'] = self.xpath_string(element, './/div[@class="name-text"]/a/@href')

                    # Цена
                    party_['price'] = self.fix_price(self.xpath_string(element, './/div[@class="price"]'))

                    # Получаем объект товара
                    try:
                        product = Product.objects.take(article  = product_['article'],
                                                       vendor   = self.vendor,
                                                       name     = product_['name'],
                                                       category = category)
                        self.products.append(product)
                    except ValueError as error:
                        continue

                    try:
                        party = Party.objects.make(product    = product,
                                                   stock      = self.stock,
                                                   article    = party_['article'],
                                                   price      = party_['price'],
                                                   price_type = self.rp,
                                                   currency   = self.rub,
                                                   quantity   = -1,
                                                   time       = self.start_time)
                        self.parties.append(party)
                    except ValueError as error:
                        pass
