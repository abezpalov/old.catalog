import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name  = 'Merlion'
    alias = 'merlion'

    url = {'start': 'https://b2b.merlion.com/',
           'login': 'https://b2b.merlion.com/',
           'links': 'https://b2b.merlion.com/?action=Y3F86565&action1=YC2E8B7C',
           'base': 'https://b2b.merlion.com/'}

    def __init__(self):

        super().__init__()

        self.stocks = {}
        self.stocks['samara'] = self.take_stock('samara-stock', 'склад в Самаре', 1, 3)
        self.stocks['moscow'] = self.take_stock('moscow-stock', 'склад в Москве', 3, 10)
        self.stocks['chehov'] = self.take_stock('chehov-stock', 'склад в Москве (Чехов)', 3, 10)
        self.stocks['bykovo'] = self.take_stock('bykovo-stock', 'склад в Москве (Быково)', 3, 10)
        self.stocks['dostavka'] = self.take_stock('dostavka-stock', 'склад в Москве (склад доставки)', 3, 10)
        self.stocks['transit_b'] = self.take_stock('b-transit', 'ближний транзит', 10, 20)
        self.stocks['transit_d'] = self.take_stock('d-transit', 'дальний транзит', 20, 60)

    def run(self):

        self.login({'client': self.updater.login.split('|')[0],
                    'login': self.updater.login.split('|')[1],
                    'password' : self.updater.password,
                    'Ok': '%C2%EE%E9%F2%E8'})

        # Получаем ссылки на прайс-листы
        tree = self.load_html(self.url['links'])

        forms = tree.xpath('//form')

        for form in forms:

            url = self.url['base']

            elements = form.xpath('.//input')

            for n, element in enumerate(elements):

                if element.name and element.value:

                    if n:
                        url = '{}&{}={}'.format(url, element.name, element.value)
                    else:
                        url = '{}?{}={}'.format(url, element.name, element.value)

            # Выбираем формат XML
            if 'type=xml' in url:

                # Загружаем прайс-лист
                data = self.load_data(url)
                data = self.unpack(data)

                self.parse(data)

        # Чистим партии
        for key in self.stocks:
            Party.objects.clear(stock = self.stocks[key], time = self.start_time)

        self.log()

    def parse(self, data):

        import lxml.etree

        try:
            tree = lxml.etree.parse(data)

        except Exception:
            return None

        # Словарь для составления имени синонима категории
        g = {0: '', 1: '', 2: ''}

        # Распознаваемые слова
        word = {'party_article': 'No',
                'product_name': 'Name',
                'vendor': 'Brand',
                'product_article': 'PartNo',
                'price_usd': 'Price',
                'price_rub': 'PriceR',
                'stock_chehov': 'Avail_SV_CHEHOV',
                'stock_bykovo': 'Avail_SV_BYKOVO',
                'stock_dostavka': 'Avail_DOSTAVKA',
                'stock_samara': 'Avail_RSMR',
                'stock_moscow': 'Avail_MSK',
                'transit_b': 'Avail_Expect',
                'transit_d': 'Avail_ExpectNext',
                'transit_date': 'Date_ExpectNext',
                'pack_minimal': 'Min_Pack',
                'pack': 'Pack',
                'volume': 'Vol',
                'weight': 'WT',
                'warranty': 'Warranty',
                'status': 'Status',
                'maction': 'MAction',
                'rrp': 'RRP',
                'rrp_date': 'RRP_Date'}

        for g1 in tree.xpath('.//G1'):
            for g2_n, g2 in enumerate(g1):
                if not g2_n:
                    g[0] = g2.text.strip()
                else:
                    for g3_n, g3 in enumerate(g2):
                        if not g3_n:
                            g[1] = g3.text.strip()
                        else:
                            for item_n, item in enumerate(g3):
                                if not item_n:
                                    # Получаем объект синонима категории
                                    g[2] = item.text.strip()
                                    category = "{} | {} | {}".format(g[0], g[1], g[2])
                                else:

                                    # Обнуляем значения
                                    product_ = {}
                                    party_ = {}

                                    # Получаем информацию о товаре
                                    for attr in item:
                                        if attr.tag == word['party_article']:
                                            party_['article'] = attr.text
                                        elif attr.tag == word['product_name']:
                                            product_['name'] = attr.text
                                        elif attr.tag == word['vendor']:
                                            product_['vendor'] = Vendor.objects.take(self.fix_name(attr.text))
                                        elif attr.tag == word['product_article']:
                                            product_['article'] = attr.text
                                        elif attr.tag == word['price_usd']:
                                            party_['price_usd'] = self.fix_price(attr.text)
                                        elif attr.tag == word['price_rub']:
                                            party_['price_rub'] = self.fix_price(attr.text)
                                        elif attr.tag == word['stock_chehov']:
                                            party_['quantity_chehov'] = self.fix_quantity(attr.text)
                                        elif attr.tag == word['stock_bykovo']:
                                            party_['quantity_bykovo'] = self.fix_quantity(attr.text)
                                        elif attr.tag == word['stock_dostavka']:
                                            party_['quantity_dostavka'] = self.fix_quantity(attr.text)
                                        elif attr.tag == word['stock_samara']:
                                            party_['quantity_samara'] = self.fix_quantity(attr.text)
                                        elif attr.tag == word['stock_moscow']:
                                            party_['quantity_moscow'] = self.fix_quantity(attr.text)
                                        elif attr.tag == word['transit_b']:
                                            party_['quantity_transit_b'] = self.fix_quantity(attr.text)
                                        elif attr.tag == word['transit_d']:
                                            party_['quantity_transit_d'] = self.fix_quantity(attr.text)
                                        elif attr.tag == word['transit_date']:
                                            party_['transit_date'] = attr.text
                                        elif attr.tag == word['pack_minimal']:
                                            party_['pack_minimal'] = attr.text
                                        elif attr.tag == word['pack']:
                                            party_['pack'] = attr.text
                                        elif attr.tag == word['volume']:
                                            product_['volume'] = attr.text
                                        elif attr.tag == word['weight']:
                                            product_['weight'] = attr.text
                                        elif attr.tag == word['warranty']:
                                            product_['warranty'] = attr.text
                                        elif attr.tag == word['status']:
                                            product_['status'] = attr.text
                                        elif attr.tag == word['maction']:
                                            product_['maction'] = attr.text
                                        elif attr.tag == word['rrp']:
                                            party_['rrp'] = attr.text
                                        elif attr.tag == word['rrp_date']:
                                            party_['rrp_date'] = attr.text

                                    # Получаем объект товара
                                    try:
                                        product = Product.objects.take(article = product_['article'],
                                                                       vendor = product_['vendor'],
                                                                       name = product_['name'],
                                                                       category = category)
                                        self.products.append(product)
                                    except ValueError as error:
                                        continue

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
                                                                   stock = self.stocks['chehov'],
                                                                   price = party_['price'],
                                                                   currency = party_['currency'],
                                                                   quantity = party_['quantity_chehov'],
                                                                   time = self.start_time)
                                        self.parties.append(party)
                                    except ValueError as error:
                                        pass
                                    except KeyError as error:
                                        pass

                                    try:
                                        party = Party.objects.make(product = product,
                                                                   stock = self.stocks['bykovo'],
                                                                   price = party_['price'],
                                                                   currency = party_['currency'],
                                                                   quantity = party_['quantity_bykovo'],
                                                                   time = self.start_time)
                                        self.parties.append(party)
                                    except ValueError as error:
                                        pass
                                    except KeyError as error:
                                        pass

                                    try:
                                        party = Party.objects.make(product = product,
                                                                   stock = self.stocks['samara'],
                                                                   price = party_['price'],
                                                                   currency = party_['currency'],
                                                                   quantity = party_['quantity_samara'],
                                                                   time = self.start_time)
                                        self.parties.append(party)
                                    except ValueError as error:
                                        pass
                                    except KeyError as error:
                                        pass

                                    try:
                                        party = Party.objects.make(product = product,
                                                                   stock = self.stocks['moscow'],
                                                                   price = party_['price'],
                                                                   currency = party_['currency'],
                                                                   quantity = party_['quantity_moscow'],
                                                                   time = self.start_time)
                                        self.parties.append(party)
                                    except ValueError as error:
                                        pass
                                    except KeyError as error:
                                        pass

                                    try:
                                        party = Party.objects.make(product = product,
                                                                   stock = self.stocks['transit_b'],
                                                                   price = party_['price'],
                                                                   currency = party_['currency'],
                                                                   quantity = party_['quantity_transit_b'],
                                                                   time = self.start_time)
                                        self.parties.append(party)
                                    except ValueError as error:
                                        pass
                                    except KeyError as error:
                                        pass

                                    try:
                                        party = Party.objects.make(product = product,
                                                                   stock = self.stocks['transit_d'],
                                                                   price = party_['price'],
                                                                   currency = party_['currency'],
                                                                   quantity = party_['quantity_transit_d'],
                                                                   time = self.start_time)
                                        self.parties.append(party)
                                    except ValueError as error:
                                        pass
                                    except KeyError as error:
                                        pass
