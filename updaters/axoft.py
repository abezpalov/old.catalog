import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name  = 'Axoft'
    alias = 'axoft'
    url   = {'start'   : 'http://axoft.ru/',
             'login'   : 'http://axoft.ru/',
             'vendors' : 'http://axoft.ru/vendors/',
             'prefix'  : 'http://axoft.ru'}
    word  = {'vendor' : '/vendors/',
             'price'  : '/pricelists/download.php?'}

    def __init__(self):

        super().__init__()

        self.stock = self.take_stock('on-order', 'на заказ', 5, 40)
        self.count = {'product' : 0, 'party' : 0}

    def run(self):

        # Авторизуемся
        self.login({
            'backurl'       : '/',
            'AUTH_FORM'     : 'Y',
            'TYPE'          : 'AUTH',
            'IS_POPUP'      : '1',
            'USER_LOGIN'    : self.updater.login,
            'USER_PASSWORD' : self.updater.password,
            'Login'         : 'Вход для партнеров'})

        # Получаем список производителей
        prices = self.get_prices_urls()

        # Проходим по каждому прайс-листу
        for n, price in enumerate(prices):

            # Синоним производителя
            vendor = Vendor.objects.take(price[0])

            if vendor:

                # Скачиваем архив с прайс-листом
                data = self.load_data(price[1])

                # Распаковываем и парсим
                data = self.unpack(data)

                if data is not None:
                    self.parse(data, vendor)

        # Чистим устаревшие партии
        Party.objects.clear(stock = self.stock, time = self.start_time)

        # Пишем в лог
        self.log()


    def get_prices_urls(self):

        prices  = set()

        tree = self.load_html(self.url['vendors'])

        links = tree.xpath('//a')

        # Выбираем ссылкки на страницы производителей
        for n, link in enumerate(links):

            vendor_name = link.text
            vendor_url  = '{}{}'.format(self.url['prefix'], link.get('href'))

            if self.word['vendor'] in vendor_url:

                tree = self.load_html(vendor_url)

                # Добавляем в список ссылок на прайс-листы соответсвующие
                for url in tree.xpath('//a/@href'):

                    if self.word['price'] in url:

                        if not self.url['prefix'] in url:
                            url  = '{}{}'.format(self.url['prefix'], url)

                        price = (vendor_name, url,)
                        prices.add(price)

        return prices


    def parse(self, data, vendor):

        import xlrd

        # Номера строк и столбцов
        num = {
            'header_line' : 3,
            'first_line'  : 5}

        # Распознаваемые слова
        word = {
            'party_article'   : 'AxoftSKU',
            'product_article' : 'VendorSKU',
            'product_name'    : 'ProductDescription',
            'product_version' : 'Version',
            'price_in'        : 'Partner',
            'price_out'       : 'Retail',
            'product_vat'     : 'NDS'}

        # Сопоставление валют
        currencies = {
            'General'           : None,
            '#,##0.00[$р.-419]' : self.rub,
            '[$$-409]#,##0.00'  : self.usd,
            '[$€-2]\\ #,##0.00' : self.eur}

        # Имя категории поставщика
        category = None

        # Парсим
        try:
            book = xlrd.open_workbook(
                file_contents   = data.read(),
                formatting_info = True)
        except NotImplementedError:
            raise(NotImplementedError('Ошибка: непонятная ошибка при открытии файла.'))
        sheet = book.sheet_by_index(0)

        # Получаем словарь форматов (потребуется при получении валюты)
        formats = book.format_map

        # Проходим по всем строкам
        for row_num in range(sheet.nrows):
            row = sheet.row_values(row_num)

            # Заголовок
            if row_num == num['header_line']:

                # Разбираем заголовок
                for cel_num, cel in enumerate(row):
                    if   str(cel).strip() == word['party_article']:
                        num['party_article'] = cel_num
                    elif str(cel).strip() == word['product_article']:
                        num['product_article'] = cel_num
                    elif str(cel).strip() == word['product_name']:
                        num['product_name'] = cel_num
                    elif str(cel).strip() == word['product_version']:
                        num['product_version'] = cel_num
                    elif str(cel).strip() == word['price_in']:
                        num['price_in'] = cel_num
                    elif str(cel).strip() == word['price_out']:
                        num['price_out'] = cel_num
                    elif str(cel).strip() == word['product_vat']:
                        num['product_vat'] = cel_num

                # Проверяем, все ли столбцы распознались
                if len(num) < 9:
                    raise(ValueError('Ошибка структуры данных: не все столбцы опознаны.'))

            # Строка с данными
            elif row_num >= num['first_line']:

                # Временные значения
                product_ = {}
                party_   = {}

                # Данные о продукте
                if row[num['product_article']]:
                    product_['article'] = self.fix_article(row[num['product_article']])
                else:
                    product_['article'] = self.fix_article(row[num['party_article']])
                product_['name']     = self.fix_name(row[num['product_name']])
                product_['version']  = self.fix_string(row[num['product_version']])
                product_['vat']      = self.fix_string(row[num['product_vat']])

                # Данные о партии
                party_['article']   = self.fix_article(row[num['party_article']])
                party_['price']     = self.fix_price(row[num['price_in']])
                party_['price_out'] = self.fix_price(row[num['price_out']])

                # Валюта входной цены
                xfx = sheet.cell_xf_index(row_num, num['price_in'])
                xf = book.xf_list[xfx]
                format_str = formats[xf.format_key].format_str
                party_['currency'] = currencies[format_str]

                # Валюта выходной цены
                xfx = sheet.cell_xf_index(row_num, num['price_out'])
                xf = book.xf_list[xfx]
                format_str = formats[xf.format_key].format_str
                party_['currency_out'] = currencies[format_str]

                # Если всё-таки это категория
                if product_['name'] and not product_['article']:
                    category = self.fix_name(row[num['product_name']])

                # Или же продукт
                elif product_['name'] and product_['article']:
                    try:
                        product = Product.objects.take(article  = product_['article'],
                                                       vendor   = vendor,
                                                       name     = product_['name'],
                                                       category = category)
                        self.products.append(product)
                    except ValueError as error:
                        continue

                    try:
                        party = Party.objects.make(product = product,
                                                   stock          = self.stock,
                                                   price          = party_['price'],
                                                   currency       = party_['currency'],
                                                   price_out      = party_['price_out'],
                                                   currency_out   = party_['currency_out'],
                                                   quantity       = None,
                                                   time           = self.start_time)
                        self.parties.append(party)
                    except ValueError as error:
                        pass

        return True
