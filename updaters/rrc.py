import re
import time

import catalog.runner
from catalog.models import *

class Runner(catalog.runner.Runner):

    name  = 'RRC'
    alias = 'rrc'
    url = {'start': 'http://rrc.ru/catalog/',
           'login': 'http://rrc.ru/catalog/?login=yes',
           'links': 'http://rrc.ru/catalog/',
           'base': 'http://rrc.ru',
           'sub_menu': 'http://rrc.ru/local/templates/rrc_common/js/api/Catalog/getCatalogSubMenu.php'}
    p = re.compile('^\/catalog\/[0-9]{4}_[0-9]_[0-9]{4}\/(\?PAGEN_[0-9]+=[0-9]+)?$')

    def __init__(self):

        super().__init__()

        self.stocks = {'stock': self.take_stock('stock', 'склад', 3, 10),
                       'on-order': self.take_stock('on-order', 'на заказ', 20, 60)}

    def run(self):

        # Авторизуемся
        self.login({'AUTH_FORM': 'Y',
                    'TYPE': 'AUTH',
                    'backurl': '/catalog/',
                    'USER_LOGIN': self.updater.login,
                    'USER_PASSWORD': self.updater.password,
                    'Login': '1'})

        # Заходим на начальную страницу
        tree = self.load_html(self.url['links'])
        urls = []

        # Получаем id для получекния ссылок
        for i in tree.xpath('//div/@data-id'):

            tree = self.load_html(url = self.url['sub_menu'], post = True,
                                  data = {'id': i, 'url': '/catalog/'})

            # Проходим по всем ссылкам
            for url in self.get_urls(tree):
                if url not in urls:
                    urls.append(url)

            time.sleep(1)

        # Проходим по всем полученным ссылкам
        i = 0
        while i < len(urls):

            tree = self.load_html(urls[i])

            # Проходим по всем ссылкам
            for url in self.get_urls(tree):
                if url not in urls:
                    urls.append(url)

            self.parse(tree)
            time.sleep(1)
            i += 1

        # Чистим партии
        for key in self.stocks:
            Party.objects.clear(stock = self.stocks[key], time = self.start_time)

        self.log()

    def get_urls(self, tree):

        urls = []

        for url in tree.xpath('//a/@href'):

            if re.match(self.p, url):
                url = self.url['base'] + url
                urls.append(url)
        return urls            

    def parse(self, tree):

        for tr in tree.xpath('.//table[@class="catalog-item-list"]//tr'):

            product_ = {}
            party_ = {}

            # Товар
            product_['article'] = self.xpath_string(tr, './/td')
            product_['article'] = self.fix_article(product_['article'])

            product_['vendor'] = self.xpath_string(tr, './/td[2]')
            if not product_['vendor']:
                product_['vendor'] = self.xpath_string(tr, './/td[2]/a')
            product_['vendor'] = self.fix_name(product_['vendor'])
            product_['vendor'] = Vendor.objects.take(product_['vendor'])

            product_['name'] = self.xpath_string(tr, './/td[@class="b-catalog-productName"]/a')
            product_['name'] = self.fix_name(product_['name'])

            product_['url'] = self.xpath_string(tr, './/td[@class="b-catalog-productName"]/a/@href')
            if self.url['base'] not in product_['url']:
                product_['url'] = "{}{}".format(self.url['base'], product_['url'])

            try:
                product = Product.objects.take(article = product_['article'],
                                               vendor = product_['vendor'],
                                               name = product_['name'],
                                               test = self.test)
                self.products.append(product.id)
            except ValueError as error:
                continue

            # Партии
            party_['article'] = self.xpath_string(tr, './/td/span[@class="ansm"]')

            for n, q in enumerate(tr.xpath('.//td[4]/table//td')):
                party_['on_stock'] = self.fix_quantity(q.text)
                party_['currency'] = self.fix_currency(self.xpath_string(tr, './/td[5]/table//tr[{}]//span'.format(n+1)))
                party_['price'] = self.fix_price(self.xpath_string(tr, './/td[5]/table//tr[{}]//span'.format(n+1)))

                if party_['on_stock']:
                    stock = self.stocks['stock']
                else:
                    stock = self.stocks['on-order']

                try:
                    party = Party.objects.make(product = product,
                                               stock = stock,
                                               price = party_['price'],
                                               currency = party_['currency'],
                                               quantity = party_['on_stock'],
                                               time = self.start_time,
                                               test = self.test)
                    self.parties.append(party.id)
                except ValueError as error:
                    pass

    def fix_currency(self, string):

        if '$' in string:
            currency = self.usd
        elif '€' in string:
            currency = self.eur
        elif string:
            currency = self.rub
        else:
            currency = None

        return currency

    def fix_price(self, price):

        price = price.replace(',', '')

        price = super().fix_price(price)

        return price

    def fix_quantity(self, quantity):

        quantity = super().fix_quantity(quantity)

        if not quantity:
            quantity = None

        return quantity
