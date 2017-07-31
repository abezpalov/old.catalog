import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name  = 'Mics'
    alias = 'mics'
    url = {'start': 'http://www.mics.ru/ru/content/main/',
           'login': 'https://www.mics.ru/ru/ajax/authorize/',
           'price': 'https://www.mics.ru/ru/ajax/price/?action=getXMLprice'}

    def __init__(self):

        super().__init__()

        self.stocks = {'stock': self.take_stock('stock', 'склад', 3, 10),
                      'transit': self.take_stock('transit', 'транзит', 10, 40),
                      'on-order': self.take_stock('order', 'на заказ', 60, 80)}

    def run(self):

        self.login({'login': self.updater.login,
                    'password': self.updater.password,
                    'action': 'authorize'})

        tree = self.load_xml(self.url['price'])

        self.parse(tree)

        for key in self.stocks:
            Party.objects.clear(stock = self.stocks[key], time = self.start_time)

        self.log()

    def parse(self, tree):

        currencies = {'RUB': self.rub, 'USD': self.usd, 'EUR': self.eur, '' : None}

        categories = {}
        for o in tree.xpath('..//Group'):

            category_ = {}
            category_['id'] = o.attrib.get('GroupID')
            category_['parent_id'] = o.attrib.get('ParentID')

            category_['name'] = o.attrib.get('Name')
            category_['name'] = self.fix_name(category_['name'])

            try:
                category_['parent_name'] = categories['parent_id']
                category_['parent_name'] = self.fix_name(category_['parent_name'])
                category_['name'] = '{} | {}'.format(category_['parent_name'], category_['name'])
            except Exception:
                pass

            categories[category_['id']] = category_['name']

        vendors = {}
        for o in tree.xpath('..//Vendor'):

            vendor_ = {}
            vendor_['id'] = o.attrib.get('VendorID')
            vendor_['name'] = self.fix_name(o.attrib.get('Name'))

            vendor = Vendor.objects.take(vendor_['name'])
            vendors[vendor_['id']] = vendor

        for o in tree.xpath('..//Ware'):

            product_ = {}
            party_ = {}

            # Продукт
            product_['article'] = self.fix_article(o.attrib.get('Partnumber'))
            product_['name'] = self.fix_name(o.attrib.get('Name'))
            product_['vendor'] = vendors[o.attrib.get('VendorID')]
            product_['category'] = categories[o.attrib.get('GroupID')]

            try:
                product_['description'] = o.attrib.get('Description')
            except Exception:
                product_['description'] = ''

            try:
                product = Product.objects.take(article = product_['article'],
                                               vendor = product_['vendor'],
                                               name = product_['name'],
                                               category = product_['category'],
                                               description = product_['description'],
                                               test = self.test)
                self.products.append(product.id)
            except ValueError as error:
                continue

            # Партии
            party_['article'] = o.attrib.get('WareID')
            party_['stock'] = self.fix_quantity(o.attrib.get('Stock_TK11'))
            party_['transit'] = self.fix_transit(o.attrib.get('Transit_TK11'))
            party_['price'] = self.fix_price(o.attrib.get('Price_TK11'))
            party_['currency'] = currencies[o.attrib.get('Currency')]

            try:
                party = Party.objects.make(product = product,
                                           stock = self.stocks['stock'],
                                           article = party_['article'],
                                           price = party_['price'],
                                           currency = party_['currency'],
                                           quantity = party_['stock'],
                                           product_name = product_['name'],
                                           time = self.start_time,
                                           test = self.test)
                self.parties.append(party.id)
            except ValueError as error:
                pass

            try:
                party = Party.objects.make(product = product,
                                           stock = self.stocks['transit'],
                                           article = party_['article'],
                                           price = party_['price'],
                                           currency = party_['currency'],
                                           quantity = party_['transit'],
                                           product_name = product_['name'],
                                           time = self.start_time,
                                           test = self.test)
                self.parties.append(party.id)
            except ValueError as error:
                pass

            if not party_['stock'] and not party_['transit']:

                try:
                    party = Party.objects.make(product = product,
                                               stock = self.stocks['on-order'],
                                               article = party_['article'],
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = None,
                                               product_name = product_['name'],
                                               time = self.start_time,
                                               test = self.test)
                    self.parties.append(party.id)
                except ValueError as error:
                    pass

    def fix_transit(self, value):

        if value == 'Транзит':
            return None
        else:
            return 0
