# TODO Описание и фотографии товара с сайте

import datetime

from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

import catalog.runner
from catalog.models import *
from anodos.models import Log


class Runner(catalog.runner.Runner):

    name = 'Fix doubles'
    alias = 'fixdoubles'

    def __init__(self):

        super().__init__()

    def run(self):

        self.start = datetime.datetime.now()

        self.complite = set()
        self.dif = 0

        self.vendors = Vendor.objects.all()

        # Make the Pool of workers
        pool = ThreadPool(4)

        # Open the urls in their own threads
        # and return the results
        pool.map(self.get_match, self.vendors)

        #close the pool and wait for the work to finish 
        pool.close()
        pool.join()

        Log.objects.add(subject = "catalog.updater.{}".format(self.updater.alias),
                        channel = "info",
                        title = "Updated",
                        description = "Updated")

    def get_match(self, vendor):

        print('Time: {}; dif: {:,}. [{}].'.format(
                    datetime.datetime.now() - self.start,
                    round(self.dif, 2),
                    vendor).replace(',', ' '))

        for vendor_2 in self.vendors:

            if vendor != vendor_2 \
                and (vendor.id, vendor_2.id) not in self.complite \
                and vendor.double != vendor_2 and vendor_2.double != vendor:

                match = []

                products_1 = Product.objects.filter(vendor = vendor, double = None).values('article')
                products_2 = Product.objects.filter(vendor = vendor_2, double = None).values('article')
                self.dif += len(products_1)*len(products_2)

                for product_1 in products_1:
                    for product_2 in products_2:

                        if product_1['article'] == product_2['article']:
                            match.append(product_1['article'])

                if len(match) > 0:

                    Log.objects.add(subject = "catalog.updater.{}".format(self.updater.alias),
                                    channel = "info",
                                    title = "Match",
                                    description = "У [{}] и [{}] совпадения: {}.".format(vendor, vendor_2, match))

            self.complite.add((vendor.id, vendor_2.id))
            self.complite.add((vendor_2.id, vendor.id))
