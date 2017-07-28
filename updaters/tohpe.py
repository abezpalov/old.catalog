# TODO Описание и фотографии товара с сайте

import catalog.runner
from catalog.models import *


class Runner(catalog.runner.Runner):

    name = 'HP to HPE'
    alias = 'tohpe'

    def __init__(self):

        super().__init__()

    def run(self):

        count = 0

        pairs = [('hp', 'hpe')]

        for pair in pairs:

            try:
                vendor_1 = Vendor.objects.get(alias = pair[0])
                vendor_2 = Vendor.objects.get(alias = pair[1])
            except Exception:
                continue

            products_1 = Product.objects.filter(vendor = vendor_1)
            products_2 = Product.objects.filter(vendor = vendor_2)

            for product_1 in products_1:
                for product_2 in products_2:

                    if product_1.article == product_2.article:
                        product_1.double = product_2
                        product_1.state = False
                        product_1.save()

                        print('{} to {}'.format(product_1, product_2))
