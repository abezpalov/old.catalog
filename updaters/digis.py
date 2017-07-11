import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name  = 'Digis'
    alias = 'digis'

    url = {'start' : 'http://digis.ru/distribution/',
           'login' : 'http://digis.ru/distribution/?login=yes',
           'files' : 'http://digis.ru/personal/profile/price/',
           'base'  : 'http://digis.ru',
           'price' : '/bitrix/redirect.php?event1=news_out&event2=/personal/profile/price/p14u/daily_price_cs_pdl.xlsx'}

    def __init__(self):

        super().__init__()

        self.stock   = self.take_stock('stock', 'склад', 3, 10)
        self.transit = self.take_stock('transit', 'транзит', 10, 40)
        self.factory = self.take_stock('factory', 'на заказ', 20, 60)

        self.count = {'product' : 0, 'party'   : 0}

    def run(self):

        # Авторизуемся
        self.login({'AUTH_FORM'     : 'Y',
                    'TYPE'          : 'AUTH',
                    'backurl'       : '/distribution/',
                    'href'          : self.url['start'],
                    'USER_LOGIN'    : self.updater.login,
                    'USER_PASSWORD' : self.updater.password,
                    'USER_REMEMBER' : 'Y',
                    'Login'         : 'Войти'})

        # Заходим на страницу загрузки
        tree = self.load_html(self.url['files'])

        # Получаем ссылки со страницы
        urls = tree.xpath('//a/@href')

        parsed = []

        for url in urls:
            if self.url['price'] in url:

                # Дописываем префикс url при необходимости
                if not self.url['base'] in url:
                    url = self.url['base'] + url

                if not url in parsed:

                    parsed.append(url)

                    # Скачиваем и парсим
                    data = self.load_data(url)
                    self.parse(data)

        # Чистим устаревшие партии
        Party.objects.clear(stock = self.factory, time = self.start_time)
        Party.objects.clear(stock = self.stock,   time = self.start_time)
        Party.objects.clear(stock = self.transit, time = self.start_time)

        # Пишем в лог
        self.log()


    def parse(self, data):

        import xlrd

        # Номера строк и столбцов
        num = {'header': 10}

        # Распознаваемые слова
        word = {'category'           : 'Категория',
                'category_sub'       : 'Подкатегория',
                'product_vendor'     : 'Бренд',
                'party_article'      : 'Код',
                'product_article'    : 'Артикул',
                'product_name'       : 'Наименование',
                'quantity_factory'   : 'На складе',
                'quantity_stock'     : 'Доступно к заказу',
                'quantity_transit'   : 'Транзит',
                'party_price_in'     : 'Цена (партн)',
                'party_currency_in'  : None,
                'party_price_out'    : 'Цена (розн)',
                'party_currency_out' : None,
                'product_warranty'   : 'Гарантия'}

        currency = {'RUB' : self.rub,
                    'RUR' : self.rub,
                    'руб' : self.rub,
                    'руб.': self.rub,
                    'USD' : self.usd,
                    'EUR' : self.eur,
                    ''    : None}

        book = xlrd.open_workbook(file_contents = data.read())
        sheet = book.sheet_by_index(1)

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
                    elif str(cel).strip() == word['product_vendor']:
                        num['product_vendor'] = cel_num
                    elif str(cel).strip() == word['party_article']:
                        num['party_article'] = cel_num
                    elif str(cel).strip() == word['product_article']:
                        num['product_article'] = cel_num
                    elif str(cel).strip() == word['product_name']:
                        num['product_name'] = cel_num
                    elif str(cel).strip() == word['quantity_factory']:
                        num['quantity_factory'] = cel_num
                    elif str(cel).strip() == word['quantity_stock']:
                        num['quantity_stock'] = cel_num
                    elif str(cel).strip() == word['quantity_transit']:
                        num['quantity_transit'] = cel_num
                    elif str(cel).strip() == word['party_price_in']:
                        num['party_price'] = cel_num
                        num['party_currency'] = cel_num + 1
                    elif str(cel).strip() == word['party_price_out']:
                        num['party_price_out'] = cel_num
                        num['party_currency_out'] = cel_num + 1
                    elif str(cel).strip() == word['product_warranty']:
                        num['product_warranty'] = cel_num

                # Проверяем, все ли столбцы распознались
                if not len(num) == 15:
                    print("Ошибка структуры данных: не все столбцы опознаны.")
                    return False
                else:
                    print("Структура данных без изменений.")

            # Товар
            elif row[num['product_article']] and row[num['product_vendor']]:

                product_ = {}
                party_ = {}

                # Категория
                category = "{} | {}".format(row[num['category']], row[num['category_sub']])

                # Производитель
                product_['vendor'] = self.fix_name(row[num['product_vendor']])
                product_['vendor'] = Vendor.objects.get_by_key(updater = self.updater, key = product_['vendor'])

                # Продукт
                product_['article'] = self.fix_article(row[num['product_article']])
                product_['name']    = self.fix_name(row[num['product_name']])

                # Гарантия
                product_['warranty'] = self.fix_string(row[num['product_warranty']])

                try:
                    product = Product.objects.take(article  = product_['article'],
                                                   vendor   = product_['vendor'],
                                                   name     = product_['name'])
                    self.products.append(product)
                except ValueError as error:
                    continue

                party_['article'] = self.fix_string(row[num['party_article']])

                party_['quantity_stock']   = self.fix_quantity(row[num['quantity_stock']])
                party_['quantity_transit'] = self.fix_quantity_transit(row[num['quantity_transit']])
                party_['quantity_factory'] = self.fix_quantity(row[num['quantity_factory']])

                party_['price']        = self.fix_price(row[num['party_price']])
                party_['currency']     = currency[row[num['party_currency']]]
                party_['price_out']    = self.fix_price(row[num['party_price_out']])
                party_['currency_out'] = currency[row[num['party_currency_out']]]

                try:
                    party = Party.objects.make(product        = product,
                                               stock          = self.stock,
                                               article        = party_['article'],
                                               price          = party_['price'],
                                               currency       = party_['currency'],
                                               price_out      = party_['price_out'],
                                               currency_out   = party_['currency_out'],
                                               quantity       = party_['quantity_stock'],
                                               time           = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product        = product,
                                               stock          = self.transit,
                                               article        = party_['article'],
                                               price          = party_['price'],
                                               currency       = party_['currency'],
                                               price_out      = party_['price_out'],
                                               currency_out   = party_['currency_out'],
                                               quantity       = party_['quantity_transit'],
                                               time           = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product        = product,
                                               stock          = self.factory,
                                               article        = party_['article'],
                                               price          = party_['price'],
                                               currency       = party_['currency'],
                                               price_out      = party_['price_out'],
                                               currency_out   = party_['currency_out'],
                                               quantity       = party_['quantity_factory'],
                                               time           = self.start_time)
                except ValueError as error:
                    pass

    def fix_quantity_transit(self, quantity):

        quantity = str(quantity).strip()

        if quantity:
            return 5
        else:
            return None
