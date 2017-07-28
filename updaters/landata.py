import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name = 'Landata'
    alias = 'landata'
    url = {'start': 'http://www.landata.ru/forpartners/',
           'login': 'http://www.landata.ru/forpartners/',
           'price': 'http://www.landata.ru/forpartners/sklad/sklad_tranzit_online/',
           'filter': '?vendor_code='}

    def __init__(self):

        super().__init__()

        self.s1 = self.take_stock('stock-1', 'склад № 1', 3, 10)
        self.s2 = self.take_stock('stock-2', 'склад № 2', 3, 10)
        self.bt = self.take_stock('b-transit', 'ближний транзит', 10, 30)
        self.dt = self.take_stock('d-transit', 'дальний транзит', 20, 60)
        self.on_order = self.take_stock('on-order', 'на заказ', 60, 80)

    def run(self):

        import time

        self.login({'AUTH_FORM': 'Y',
                    'TYPE': 'AUTH',
                    'backurl': '/index.php',
                    'USER_LOGIN': self.updater.login,
                    'USER_PASSWORD': self.updater.password,
                    'Login': '%C2%EE%E9%F2%E8'})

        # Заходим на начальную страницу каталога
        tree = self.load_html(self.url['price'])

        # Проходим по всем ссылкам
        urls = tree.xpath('//a/@href')
        done = []
        for url in urls:
            if self.url['filter'] in url:

                # Проверяем ссылку
                url = self.url['price'] + url
                if url in done:
                    continue

                # Загружаем и парсим страницу
                tree = self.load_html(url)
                vendor = Vendor.objects.take(url.split(self.url['filter'])[1])

                try:
                    self.parse(tree, vendor)
                    done.append(url)
                except ValueError:
                    pass

                # Ждем, чтобы не получить отбой сервера
                time.sleep(1)

        # Чистим партии
        Party.objects.clear(stock = self.s1, time = self.start_time)
        Party.objects.clear(stock = self.s2, time = self.start_time)
        Party.objects.clear(stock = self.bt, time = self.start_time)
        Party.objects.clear(stock = self.dt, time = self.start_time)
        Party.objects.clear(stock = self.on_order, time = self.start_time)

        self.log()

    def parse(self, tree, vendor):

        # Номера строк и столбцов
        num = {}

        # Распознаваемые слова
        word = {'party_article': 'Н/н',
                'product_article': 'Код',
                'product_name': 'Наименование',
                's1': 'Р',
                's2': 'C',
                'bt': '<th>БТ</th>',
                'dt': '<th>ДТ</th>',
                'price': 'Цена Dealer',
                'currency_alias': 'Валюта'}

        # Валюты
        currencies = {'RUB': self.rub,
                      'USD': self.usd,
                      'EUR': self.eur}

        table = tree.xpath('//table[@class="table  table-striped tablevendor"]//tr')

        # Проходим по строкам таблицы
        for trn, tr in enumerate(table):

            # Заголовок таблицы
            if not trn:
                for thn, th in enumerate(tr):
                    text = self.fix_string(th.text)
                    if text == word['party_article']:
                        num['party_article'] = thn
                    elif text == word['product_article']:
                        num['product_article'] = thn
                    elif text == word['product_name']:
                        num['product_name'] = thn
                    elif th.text == word['s1']:
                        num['s1'] = thn
                    elif text == word['s2']:
                        num['s2'] = thn
                    elif text == word['bt']:
                        num['bt'] = thn
                    elif text == word['dt']:
                        num['dt'] = thn
                    elif text == word['price']:
                        num['price'] = thn
                    elif text == word['currency_alias']:
                        num['currency_alias'] = thn

                # Проверяем, все ли столбцы распознались
                if len(num) < len(word):
                    raise(ValueError('Ошибка структуры данных: не все столбцы опознаны.'))
                else:
                    pass

            # Строка товара
            else:

                product_ = {}
                party_ = {}

                try:
                    product_['article'] = tr[num['product_article']].text.strip().split('//')[0]
                    product_['article'] = self.fix_article(product_['article'])

                    product_['name'] = tr[num['product_name']].text.strip()
                    product_['name'] = self.fix_name(product_['name'])
                except Exception:
                    continue

                try:
                    product = Product.objects.take(article = product_['article'],
                                                   vendor = vendor,
                                                   name = product_['name'])
                    self.products.append(product)
                except ValueError as error:
                    continue

                party_['article'] = tr[num['party_article']].text.strip()
                party_['article'] = self.fix_article(party_['article'])

                party_['price'] = tr[num['price']].text
                party_['price'] = self.fix_price(party_['price'])

                party_['currency_alias'] = tr[num['currency_alias']].text
                party_['currency_alias'] = self.fix_string(party_['currency_alias'])
                if party_['currency_alias']:
                    party_['currency'] = currencies[party_['currency_alias']]
                else:
                    party_['currency'] =  None

                party_['quantity_s1'] = self.fix_quantity(tr[num['s1']].text)
                party_['quantity_s2'] = self.fix_quantity(tr[num['s2']].text)
                party_['quantity_bt'] = self.fix_quantity(tr[num['bt']].text)
                party_['quantity_dt'] = self.fix_quantity(tr[num['dt']].text)

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.s1,
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = party_['quantity_s1'],
                                               time = self.start_time)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.s2,
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = party_['quantity_s2'],
                                               time = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.bt,
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = party_['quantity_bt'],
                                               time = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.dt,
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = party_['quantity_dt'],
                                               time = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.on_order,
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = None,
                                               time = self.start_time)
                    self.parties.append(party)
                except ValueError as error:
                    pass
