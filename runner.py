import requests

from django.utils import timezone

from anodos.models import Log
from catalog.models import *


class Runner:

    test = True

    def __init__(self):

        self.start_time = timezone.now()

        self.distributor = Distributor.objects.take(
            alias = self.alias,
            name  = self.name)

        self.updater = Updater.objects.take(
            alias       = self.alias,
            name        = self.name,
            distributor = self.distributor)

        self.rub = Currency.objects.take(
            alias     = 'RUB',
            name      = 'р.',
            full_name = 'Российский рубль',
            rate      = 1,
            quantity  = 1)

        self.usd = Currency.objects.take(
            alias     = 'USD',
            name      = '$',
            full_name = 'US Dollar',
            rate      = 60,
            quantity  = 1)

        self.eur = Currency.objects.take(
            alias     = 'EUR',
            name      = 'EUR',
            full_name = 'Euro',
            rate      = 80,
            quantity  = 1)

        self.s = requests.Session()

        Log.objects.add(
            subject     = "catalog.updater.{}".format(self.updater.alias),
            channel     = "start",
            title       = "Start",
            description = "Запущен загрузчик {}.".format(self.updater.name))

        self.products = []
        self.parties = []


    def take_stock(self, alias_end = 'stock', name_end = 'склад',
                delivery_time_min = 5, delivery_time_max = 10):

        stock = Stock.objects.take(
            alias             = '{}-{}'.format(self.alias, alias_end),
            name              = '{}: {}'.format(self.name, name_end),
            delivery_time_min = delivery_time_min,
            delivery_time_max = delivery_time_max,
            distributor       = self.distributor)

        return stock


    def take_vendor(self, key):

        return Vendor.objects.get_by_key(
            updater = self.updater,
            key     = key)


    def take_parametersynonym(self, name):

        return ParameterSynonym.objects.take(
            name        = name,
            updater     = self.updater)


    def load(self, url, result_type = None, timeout = 100.0, try_quantity = 10):

        import time

        try:
            self.cookies
        except AttributeError:
            self.cookies = None

        for i in range(try_quantity):

            try:
                if self.cookies is None:
                    r = self.s.get(url, allow_redirects = True, verify = False,
                        timeout = timeout)
                    self.cookies = r.cookies
                else:
                    r = self.s.get(url, cookies = self.cookies,
                        allow_redirects = True, verify = False, timeout = timeout)
                    self.cookies = r.cookies

            except requests.exceptions.Timeout:
                print("Ошибка: превышен интервал ожидания [{}].".format(url))
                if i + 1 == try_quantity:
                    return None
                else:
                    time.sleep(10)
                    print("Пробую ещё раз.")

            except Exception:
                print("Ошибка: нет соединения [{}].".format(url))
                if i + 1 == try_quantity:
                    return None
                else:
                    time.sleep(10)
                    print("Пробую ещё раз.")

            else:
                break

        if result_type == 'cookie':
            return r.cookie
        elif result_type == 'text':
            return r.text
        elif result_type == 'content':
            return r.content
        elif result_type == 'request':
            return r

        return r


    def load_cookie(self, timeout = 100.0):

        self.load(self.url['start'], timeout = 100.0)

        return True


    def login(self, payload = {}, timeout = 100.0):

        url = self.url['login']

        # Параметры авторизации
        if not self.updater.login or not self.updater.password:
            raise('Ошибка: отсутствуют параметры авторизации.')

        self.load_cookie()

        # Авторизуемся
        try:
            r = self.s.post(url, cookies = self.cookies,
                    data = payload, allow_redirects = True, verify = False,
                    timeout = timeout)
            self.cookies = r.cookies
        except requests.exceptions.Timeout:
            raise(ValueError("Ошибка: превышен интервал ожидания [{}].".format(url)))
        except Exception:
            raise(ValueError("Ошибка: нет соединения [{}].".format(url)))

        return True


    def load_text(self, url, timeout = 100.0):

        return self.load(url, result_type = 'text', timeout = 100.0)


    def load_html(self, url, timeout = 100.0):

        import lxml.html

        text = self.load(url, result_type = 'text', timeout = 100.0)

        try:
            tree = lxml.html.fromstring(text)

        except Exception:
            return None

        return tree


    def load_xml(self, url, timeout = 100.0):

        import lxml.etree

        text = self.load(url, result_type = 'text', timeout = 500.0)

        try:
            tree = lxml.etree.fromstring(text.encode('utf-8'))

        except Exception:
            return None

        return tree

    def load_data(self, url, timeout = 100.0):
        from io import BytesIO
        content = self.load(url, result_type = 'content', timeout = 100.0)
        return BytesIO(content)

    def unpack(self, data):
        from catalog.lib.zipfile import ZipFile
        try:
            zip_data = ZipFile(data)
            data = zip_data.open(zip_data.namelist()[0])
        except Exception:
            return None
        else:
            return data

    def unpack_xml(self, data):
        import lxml.etree
        data = self.unpack(data)
        text = data.read()
        try:
            tree = lxml.etree.fromstring(text.decode('utf-8'))
        except Exception:
            return None
        return tree

    def fix_string(self, string):

        # Избавляемся от исключений
        if string is None:
            string = ''
        else:
            string = str(string)

        # Убираем ненужные символы
        string = string.replace('\t', ' ')
        string = string.replace('\n', ' ')

        # Убираем двойные пробелы
        while '  ' in string:
            string = string.replace('  ', ' ')

        # Убираем обрамляющие пробелы
        string = string.strip()

        return string

    def xpath_string(self, element, query, index = 0):

        targets = element.xpath(query)
        if targets:
            target = targets[index]
        else:
            return ''

        if str(type(target)) in ["<class 'lxml.html.HtmlElement'>", "<class 'lxml.etree._Element'>"]:
            try:
                string = target.text
            except Exception:
                string = ''
        elif str(type(target)) in ["<class 'lxml.etree._ElementUnicodeResult'>"]:
            try:
                string = target
            except Exception:
                string = None
        else:
            raise(ValueError('Некорректный тип данных:', str(type(target))))

        string = self.fix_string(string)
        return string

    def fix_text(self, text):

        # Избавляемся от исключений
        if text is None:
            text = ''
        else:
            text = str(text)

        # Убираем двойные пробелы
        while '  ' in text:
            text = text.replace('  ', ' ')

        # Убираем обрамляющие пробелы
        text = text.strip()

        return text


    def xpath_text(self, element, query):

        try:
            text = element.xpath(query)[0].text
        except Exception:
            text = ''

        text = self.fix_text(text)

        return text


    def xpath_int(self, element, query, index = 0):

        try:
            i = int(element.xpath(query)[index].text.strip())

        except Exception:
            i = 0

        return i

    def xpath_float(self, element, query, index = 0):

        try:
            text = element.xpath(query)[index].text.strip()
            text = text.replace('₽', '')
            text = text.replace('$', '')
            text = text.replace(' ', '')
            text = text.replace('&nbsp;', '')
            text = text.replace(' ', '') # Хитрый пробел
            print(text)
            result = float(text)

        except Exception:
            result = None

        return result


    def fix_url(self, url):
        if self.url.get('base', None):
             if self.url['base'] not in url:
                 url = self.url['base'] + url
        return url


    def fix_price(self, price):

        price = str(price).strip()

        if price in ('Цена не найдена', 'звоните', 'Звоните', 'CALL', '?',):
            return None

        translation_map = {
            ord('$') : '', ord('€') : '', ord(' ') : '',
            ord('р') : '', ord('у') : '', ord('б') : '',
            ord('R') : '', ord('U') : '', ord('B') : '',
            ord('+') : '', ord(',') : '.'}

        price = price.translate(translation_map)

        try:
            price = float(price)

        except ValueError:
            return None

        if not price:
            return None

        return price


    def fix_quantity(self, quantity):

        # Гарантируем строковой тип
        quantity = str(quantity).strip()

        quantity = quantity.replace('>', '')
        quantity = quantity.replace('более', '')
        quantity = quantity.replace(' ', '')

        if quantity in ('', '0*', 'call', 'Нет', 'в транзите'):
            return 0
        elif quantity in ('Звоните', 'под заказ', 'звонить'):
            return None
        elif quantity in ('Есть'):
            return 1
        elif quantity in('мало', '+', '+ '):
            return 2
        elif quantity in ('много', '++', '++ ', 'Много'):
            return 5
        elif quantity in ('+++', '+++ '):
            return 50
        elif quantity in ('++++', '++++ '):
            return 100

        try:
            quantity = int(float(quantity))
        except Exception:
            return 0

        return quantity


    def fix_article(self, article):

        # Гарантируем строковой тип
        article = str(article)

        # Проверяем на наличие стоп-сочетиний
        if ' ' in article or'Уценка' in article or 'демо' in article or 'ДЕМО' in article or 'DEMO' in article or 'б.у.' in article:
            return None

        # Избавляемся от мусорных символов
        translation_map = {
            ord('(') : '', ord(')') : '', ord('[') : '',
            ord(']') : '', ord('™') : '', ord('®') : ''}
        article = article.translate(translation_map)
        article = article.replace('\u00AD', '')
        article = article.replace('\t', ' ')
        article = article.replace('\n', ' ')

        # Убираем двойные пробелы
        while '  ' in article:
            article = article.replace('  ', ' ')

        # Убираем обрамляющие пробелы
        article = str(article).strip()

        return article


    def fix_name(self, name):

        # Гарантируем строковой тип
        name = str(name)

        # Проверяем на наличие стоп-сочетиний
        if 'демо' in name or 'ДЕМО' in name or 'DEMO' in name or 'б.у.' in name or 'Б/У' in name:
            return None

        # Избавляемся от мусорных символов
        translation_map = {
            ord('(') : '', ord(')') : '', ord('[') : '',
            ord(']') : '', ord('™') : '', ord('®') : ''}
        name = name.translate(translation_map)
        name = name.replace('\u00AD', '')
        name = name.replace('\t', ' ')
        name = name.replace('\n', ' ')

        # Убираем двойные пробелы
        while '  ' in name:
            name = name.replace('  ', ' ')

        # Убираем обрамляющие пробелы
        name = name.strip()


        return name



    def log(self):

        if len(self.products) and len(self.parties):
            Log.objects.add(
                subject     = "catalog.updater.{}".format(self.updater.alias),
                channel     = "info",
                title       = "Updated",
                description = "Updated: products - {}; parties - {}.".format(
                    '{:,}'.format(len(self.products)).replace(',', ' '),
                    '{:,}'.format(len(self.parties)).replace(',', ' ')))

        else:
            Log.objects.add(
                subject     = "catalog.updater.{}".format(self.updater.alias),
                channel     = "error",
                title       = "Error",
                description = "Updated error: products - {}; parties - {}.".format(
                    '{:,}'.format(len(self.products)).replace(',', ' '),
                    '{:,}'.format(len(self.parties)).replace(',', ' ')))
