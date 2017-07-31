# TODO Добавление описания о гарантии (с таблицы)
# TODO Обработку описаний товара (по ссылкам из таблицы)
# TODO Загрузка фотографий товара (со страниц с описанием)

import time

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name  = 'Elko'
    alias = 'elko'
    url = {'start': 'https://ecom.elko.ru/Account/Login',
           'login': 'https://ecom.elko.ru/Account/Login',
           'price': 'https://ecom.elko.ru/Catalog/PriceList?'}

    def __init__(self):

        super().__init__()

        self.stock = self.take_stock('stock', 'склад', 3, 10)
        self.transit = self.take_stock('transit', 'транзит', 10, 60)

    def run(self):

        # Заходим на начальную страницу
        tree = self.load_html(self.url['start'])
        token = self.xpath_string(tree, './/input[@name="__RequestVerificationToken"]/@value')

        # Авторизуемся
        self.login({'__RequestVerificationToken': token,
                    'Amnesia': '',
                    'Username': self.updater.login,
                    'Password': self.updater.password,
                    'submit': 'Войти',
                    'Username2': ''})

        # Получаем данные
        data = self.load(self.url['price'], result_type = 'content')

        # Парсим
        self.parse(data)

        # Пишем устаревшие партии
        Party.objects.clear(stock = self.stock, time = self.start_time)
        Party.objects.clear(stock = self.transit, time = self.start_time)

        # Пишем результат в лог
        self.log()

    def parse(self, data):

        import xlrd

        # Номера строк и столбцов
        num = {'header': 5}

        # Распознаваемые слова
        word = {'category': 'Категория',
                'category_sub': 'Подкатегория',
                'party_article': 'Код ELKO',
                'product_vendor': 'Производитель',
                'product_article': 'Заводской код',
                'product_name': 'Название и описание продукта',
                'product_description': 'Дополнительная информация',
                'party_price': 'Цена',
                'party_quantity': 'В наличии',
                'product_warranty': 'Гарантия',
                'product_url': 'Ссылка на товар'}

        book = xlrd.open_workbook(file_contents = data)

        sheet = book.sheet_by_index(0)

        for row_num in range(sheet.nrows):
            row = sheet.row_values(row_num)

            # Пустые строки
            if row_num < num['header']:
                continue

            # Заголовок таблицы
            elif row_num == num['header']:
                for cel_num, cel in enumerate(row):
                    if   str(cel).strip() == word['category']:
                        num['category'] = cel_num
                    elif str(cel).strip() == word['category_sub']:
                        num['category_sub'] = cel_num
                    elif str(cel).strip() == word['party_article']:
                        num['party_article'] = cel_num
                    elif str(cel).strip() == word['product_vendor']:
                        num['product_vendor'] = cel_num
                    elif str(cel).strip() == word['product_article']:
                        num['product_article'] = cel_num
                    elif str(cel).strip() == word['product_name']:
                        num['product_name'] = cel_num
                    elif str(cel).strip() == word['product_description']:
                        num['product_description'] = cel_num
                    elif str(cel).strip() == word['party_price']:
                        num['party_price'] = cel_num
                    elif str(cel).strip() == word['party_quantity']:
                        num['party_quantity'] = cel_num
                    elif str(cel).strip() == word['product_warranty']:
                        num['product_warranty'] = cel_num
                    elif str(cel).strip() == word['product_url']:
                        num['product_url'] = cel_num

                # Проверяем, все ли столбцы распознались
                if len(num) < len(word):
                    raise(ValueError("Ошибка структуры данных: не все столбцы опознаны."))

            # Товар
            elif row[num['product_article']] and row[num['product_vendor']]:

                product_ = {}
                party_ = {}

                # Категория
                category = "{} | {}".format(row[num['category']], row[num['category_sub']])

                # Производитель
                product_['vendor'] = self.fix_name(row[num['product_vendor']])
                product_['vendor'] = Vendor.objects.take(product_['vendor'])

                # Продукт
                product_['article'] = self.fix_article(row[num['product_vendor']])
                product_['article'] = self.fix_article(row[num['product_article']])
                product_['name'] = self.fix_name(row[num['product_name']])
                product_['description'] = self.fix_name(row[num['product_description']])
                product_['warranty'] = self.fix_name(row[num['product_warranty']])
                product_['url'] = self.fix_name(row[num['product_url']])

                try:
                    product = Product.objects.take(article = product_['article'],
                                                   vendor = product_['vendor'],
                                                   name = product_['name'],
                                                   test = self.test)
                    product = Product.objects.take(article = product_['article'],
                                                   vendor = product_['vendor'],
                                                   name = product_['description'],
                                                   test = self.test)
                    self.products.append(product.id)
                except ValueError as error:
                    continue

                # Партия
                party_['quantity_stock'] = self.fix_quantity(row[num['party_quantity']])
                if row[num['party_quantity']] == 'в транзите':
                    party_['quantity_transit'] = None
                else:
                    party_['quantity_transit'] = 0

                party_['article'] = self.fix_quantity(row[num['party_article']])
                party_['price'] = self.fix_price(row[num['party_price']])

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.stock,
                                               article = party_['article'],
                                               price = party_['price'],
                                               currency = self.rub,
                                               quantity = party_['quantity_stock'],
                                               time = self.start_time,
                                               test = self.test)
                    self.parties.append(party.id)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.transit,
                                               article = party_['article'],
                                               price = party_['price'],
                                               currency = self.rub,
                                               quantity = party_['quantity_transit'],
                                               time = self.start_time,
                                               test = self.test)
                    self.parties.append(party.id)
                except ValueError as error:
                    pass
