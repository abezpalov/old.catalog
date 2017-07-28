import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name  = 'Treolan'
    alias = 'treolan'
    url = {'start': 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F',
           'login': 'https://b2b.treolan.ru/Account/Login?ReturnUrl=%2F',
           'price': 'https://b2b.treolan.ru/Catalog/SearchToExcel?Template=&Commodity=true&IncludeFullPriceList=false&OrderBy=0&Groups=&Vendors=&IncludeSubGroups=false&Condition=0&PriceMin=&PriceMax=&Currency=0&AvailableAtStockOnly=false&AdditionalParamsStr=&AdditionalParams=&AddParamsShow=&GetExcel=false&FromLeftCol=false&CatalogProductsOnly=true&RusDescription=false&skip=0&take=50&LoadResults=false&DemoOnly=false&ShowHpCarePack=false&MpTypes=-1&showActualGoods=false'}

    def __init__(self):

        super().__init__()

        self.stocks = {'stock': self.take_stock('stock', 'склад', 3, 10),
                       'transit': self.take_stock('transit', 'транзит', 10, 40),
                       'on-order': self.take_stock('on-order', 'на заказ', 30, 60)}

    def run(self):

        # Авторизуемся
        self.login({'UserName': self.updater.login,
                    'Password': self.updater.password,
                    'RememberMe': 'false'})

        # Получаем HTML-данные
        tree = self.load_html(self.url['price'])

        # Парсим прайс-лист
        self.parse(tree)

        # Чистим партии
        for key in self.stocks:
            Party.objects.clear(stock = self.stocks[key],   time = self.start_time)

        self.log()

    def parse(self, tree):

        num = {}

        word = {'article': 'Артикул',
                'name': 'Наименование',
                'vendor': 'Производитель',
                'quantity_stock': 'Св.',
                'quantity_transit': 'Св.+Тр.',
                'transit_date': 'Б. Тр.',
                'price_usd': 'Цена*',        
                'price_rub': 'Цена руб.**'}

        # Парсим
        try:
            table = tree.xpath("//table")[0]
        except IndexError:
            print("Не получилось загрузить прайс-лист.")
            print("Проверьте параметры доступа.")
            return False

        for trn, tr in enumerate(table):

            # Заголовок таблицы
            if trn == 0:
                for tdn, td in enumerate(tr):
                    if td[0].text.strip() == word['article']:
                        num['article'] = tdn + 1
                    elif td[0].text.strip() == word['name']:
                        num['name'] = tdn + 1
                    elif td[0].text.strip() == word['vendor']:
                        num['vendor'] = tdn + 1
                    elif td[0].text.strip() == word['quantity_stock']:
                        num['quantity_stock'] = tdn + 1
                    elif td[0].text.strip() == word['quantity_transit']:
                        num['quantity_transit'] = tdn + 1
                    elif td[0].text.strip() == word['transit_date']:
                        num['transit_date'] = tdn + 1
                    elif td[0].text.strip() == word['price_usd']:
                        num['price_usd'] = tdn + 1
                    elif td[0].text.strip() == word['price_rub']:
                        num['price_rub'] = tdn + 1

                # Проверяем, все ли столбцы распознались
                if len(num) < len(word):
                    print(num)
                    raise(ValueError('Ошибка структуры данных: не все столбцы опознаны.'))

            # Категория
            elif len(tr) == 1:
                category = self.fix_name(tr[0][0].text)

            # Товар
            elif len(tr) > 8:

                product_ = {}
                party_ = {}

                # Продукт
                product_['article'] = self.xpath_string(tr, './/td[{}]'.format(num['article']))
                product_['article'] = self.fix_article(product_['article'])

                product_['name'] = self.xpath_string(tr, './/td[{}]'.format(num['name']))
                product_['name'] = self.fix_name(product_['name'])

                product_['vendor'] = self.xpath_string(tr, './/td[{}]'.format(num['vendor']))
                product_['vendor'] = self.fix_name(product_['vendor'])
                product_['vendor'] = Vendor.objects.take(product_['vendor'])

                try:
                    product = Product.objects.take(article = product_['article'],
                                                   vendor = product_['vendor'],
                                                   name = product_['name'],
                                                   category = category)
                    self.products.append(product)
                except ValueError as error:
                    continue

                # Партии
                party_['quantity_stock'] = self.xpath_string(tr, './/td[{}]'.format(num['quantity_stock']))
                party_['quantity_stock'] = self.fix_quantity(party_['quantity_stock'])

                party_['quantity_transit'] = self.xpath_string(tr, './/td[{}]'.format(num['quantity_transit']))
                party_['quantity_transit'] = self.fix_quantity(party_['quantity_transit'])

                party_['transit_date'] = self.xpath_string(tr, './/td[{}]'.format(num['transit_date']))

                party_['price_usd'] = self.xpath_string(tr, './/td[{}]'.format(num['price_usd']))
                party_['price_usd'] = self.fix_price(party_['price_usd'])

                party_['price_rub'] = self.xpath_string(tr, './/td[{}]'.format(num['price_rub']))
                party_['price_rub'] = self.fix_price(party_['price_rub'])

                if party_['price_usd']:
                    party_['price'] = party_['price_usd']
                    party_['currency'] = self.usd
                elif party_['price_rub']:
                    party_['price'] = party_['price_rub']
                    party_['currency'] = self.rub
                else:
                    party_['price'] = None
                    party_['currency'] = None

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.stocks['stock'],
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = party_['quantity_stock'],
                                               product_name = product_['name'],
                                               time = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.stocks['transit'],
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = party_['quantity_transit'],
                                               product_name = product_['name'],
                                               time = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.stocks['on-order'],
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = None,
                                               product_name = product_['name'],
                                               time = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass
