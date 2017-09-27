# TODO Фотографии и описание товаров с портала

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name  = 'Fujitsu'
    alias = 'fujitsu'
    url = {'start': 'https://login.ts.fujitsu.com/vpn/tmindex.html',
           'login': 'https://login.ts.fujitsu.com/cgi/login',
           'links': 'https://partners.ts.fujitsu.com/sites/CPP/ru/config-tools/Pages/default.aspx',
           'search': '2017.zip',
           'prefix': 'https://partners.ts.fujitsu.com'}

    def __init__(self):

        super().__init__()

        self.vendor = Vendor.objects.take(name = self.name)

        self.stock = self.take_stock('factory', 'на заказ', 40, 60)

        self.rdp = PriceType.objects.take(alias = 'RDP-Fujitsu',
                                          name  = 'Рекомендованная диллерская цена Fujitsu')

    def run(self):

        # Авторизуемся
        self.login({'login':  self.updater.login,
                    'passwd': self.updater.password})

        # Заходим на страницу загрузки
        tree = self.load_html(self.url['links'])

        # Получаем ссылки со страницы
        result = False
        urls = tree.xpath('//a/@href')
        for url in urls:
            if self.url['search'] in url:

                # Скачиваем архив
                url = self.url['prefix'] + url
                data = self.load_data(url)

                # Парсим sys_arc.mdb
                mdb = self.unpack(data, 'sys_arc.mdb')
                self.parse_categories(mdb)
                self.parse_products(mdb)

                # Парсим prices.mdb
                mdb = self.unpack(data, 'prices.mdb')
                self.parse_prices(mdb)

                result = True
                break

        if result:
            Party.objects.clear(stock = self.stock, time = self.start_time)
            self.log()

        else:
            raise(ValueError('Ошибка: не найден прайс-лист.'))

    def unpack(self, data, mdb_name):

        from zipfile import ZipFile

        zip_data = ZipFile(data)
        zip_data.extract(mdb_name, '/tmp')

        return "/tmp/{}".format(mdb_name)

    def parse_categories(self, mdb):

        import sys, subprocess, os

        # Синонимы категорий
        self.categories = {}

        # Номера строк и столбцов
        num = {}

        # Распознаваемые слова
        word = {'numb': 'PraesKategLfdNr',
                'name': 'PraesKateg'}

        # Загружаем таблицу категорий
        rows = subprocess.Popen(["mdb-export", "-R", "{%row%}", "-d", "{%col%}", mdb, 'PraesentationsKategorien'],
                                stdout = subprocess.PIPE).communicate()[0]
        rows = rows.decode("utf-8").split("{%row%}")

        for rown, row in enumerate(rows):

            row = row.split("{%col%}")

            # Заголовок
            if not rown:

                for celn, cel in enumerate(row):

                    cel = cel.strip().replace('"', '')
                    if   cel.strip() == word['numb']: num['numb'] = celn
                    elif cel.strip() == word['name']: num['name'] = celn

                if len(num) < 2:
                    raise(ValueError('Ошибка структуры данных: не все столбцы опознаны.'))

            # Строка с данными
            elif rown + 1 < len(rows):

                # Получаем объект синонима
                category = self.fix_string("{} | {}".format(row[num['numb']], row[num['name']]))
                self.categories[row[num['numb']]] = category

        return True

    def parse_products(self, mdb):

        import sys, subprocess, os

        # Номера строк и столбцов
        num = {}

        # Распознаваемые слова
        word = {'article': 'SachNr',
                'name': 'Benennung',
                'status': 'VertStat',
                'category_numb': 'PraesKategNr',
                'description-1': 'Beschreibung',
                'description-2': 'CfgHint'}

        # Статусы продуктов
        self.quantity = {}

        # Загружаем таблицу продуктов
        rows = subprocess.Popen(["mdb-export", "-R", "{%row%}", "-d", "{%col%}", mdb, 'Komp'], stdout = subprocess.PIPE).communicate()[0]
        rows = rows.decode("utf-8").split("{%row%}")

        for rown, row in enumerate(rows):

            row = row.split("{%col%}")

            # Заголовок
            if not rown:

                for celn, cel in enumerate(row):

                    cel = cel.strip().replace('"', '')
                    if cel.strip() == word['article']:
                        num['article'] = celn
                    elif cel.strip() == word['name']:
                        num['name'] = celn
                    elif cel.strip() == word['status']:
                        num['status'] = celn
                    elif cel.strip() == word['category_numb']:
                        num['category_numb'] = celn
                    elif cel.strip() == word['description-1']:
                        num['description-1'] = celn
                    elif cel.strip() == word['description-2']:
                        num['description-2'] = celn

                if len(num) < 6:
                    raise(ValueError('Ошибка структуры данных: не все столбцы опознаны.'))

            # Строка с данными
            elif rown + 1 < len(rows):

                product_ = {}

                # Продукт
                product_['article'] = self.fix_string(row[num['article']])
                product_['name'] = self.fix_string(row[num['name']])

                if self.fix_string(row[num['status']]) == '50':
                    self.quantity[product_['article']] = -1
                else:
                    self.quantity[product_['article']] = None

                # Категория
                try:
                    product_['category'] = self.categories[row[num['category_numb']]]
                except KeyError:
                    product_['category'] = None

                # Описание
                product_['description-1'] = self.fix_string(row[num['description-1']])
                product_['description-2'] = self.fix_string(row[num['description-2']])

                if len(product_['description-1']) > len(product_['description-2']):
                    product_['description'] = product_['description-1']
                elif len(product_['description-2']):
                    product_['description'] = product_['description-2']
                else:
                    product_['description'] = None

                try:
                    product = Product.objects.take(article = product_['article'],
                                                   vendor = self.vendor,
                                                   name = product_['name'],
                                                   category = product_['category'],
                                                   description = product_['description'],
                                                   test = self.test)
                    self.products.append(product.id)

                except ValueError as error:
                    continue

                if 'Warranty group: ' in product.name:
                    product.state = False
                    product.save()

    def parse_prices(self, mdb):

        import sys, subprocess, os

        # Номера строк и столбцов
        num = {}

        # Распознаваемые слова
        word = {'price_n': 'SPNr',
                'price_a': 'SPName',
                'article': 'SachNr'}

        price_types = {}

        # Загружаем таблицу типов цен
        rows = subprocess.Popen(["mdb-export", "-R", "{%row%}", "-d", "{%col%}", mdb, 'PriceSpec'],
                                stdout = subprocess.PIPE).communicate()[0]
        rows = rows.decode("utf-8").split("{%row%}")

        for rown, row in enumerate(rows):

            row = row.split("{%col%}")

            # Заголовок
            if not rown:

                for celn, cel in enumerate(row):

                    cel = self.fix_string(cel)
                    if cel.strip() == word['price_n']:
                        num['price_n'] = celn
                    elif cel.strip() == word['price_a']:
                        num['price_a'] = celn

                if len(num) < 2:
                    raise(ValueError('Ошибка структуры данных: не все столбцы опознаны.'))

            # Строка с данными
            elif rown + 1 < len(rows):
                price_types[row[num['price_a']].strip().replace('"', '')] = row[num['price_n']].strip().replace('"', '')

        word['price'] = "SP" + price_types["RDP"]

        # Загружаем таблицу цен
        rows = subprocess.Popen(["mdb-export", "-R", "{%row%}", "-d", "{%col%}", mdb, 'Prices'], stdout = subprocess.PIPE).communicate()[0]
        rows = rows.decode("utf-8").split("%row%}")

        for rown, row in enumerate(rows):

            row = row.split("{%col%}")

            # Заголовок
            if not rown:

                for celn, cel in enumerate(row):

                    cel = cel.strip().replace('"', '')
                    if   cel.strip() == word['article']: num['article'] = celn
                    elif cel.strip() == word['price']:   num['price']   = celn

                if len(num) < 4:
                    raise(ValueError('Ошибка структуры данных: не все столбцы опознаны.'))

            # Строка с данными
            elif rown + 1 < len(rows):

                article = row[num['article']].strip().replace('"', '')
                price = float(row[num['price']].strip().replace('"', '') or 0)

                try:
                    # Получаем объект товара
                    product = Product.objects.get(article = article, vendor = self.vendor)

                    # Определяем количество (из свойств товара)
                    quantity = self.quantity[article]

                    # Добавляем партии
                    party = Party.objects.make(product = product,
                                               stock = self.stock,
                                               price = price,
                                               price_type = self.rdp,
                                               currency = self.usd,
                                               quantity = quantity,
                                               time = self.start_time,
                                               test = self.test)
                    self.parties.append(party.id)

                except ValueError as error:
                    pass
                except Exception:
                    pass
                except Product.DoesNotExist:
                    pass

        return True


    def fix_string(self, string):

        super().fix_string(string)

        string = string.replace('"', '')

        return string
