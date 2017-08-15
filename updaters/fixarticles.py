# TODO Описание и фотографии товара с сайте

import datetime

from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

import catalog.runner
from catalog.models import *
from anodos.models import Log


class Runner(catalog.runner.Runner):

    name = 'Fix articles'
    alias = 'fixarticles'

    def __init__(self):

        super().__init__()

    def run(self):

        self.start = datetime.datetime.now()

        self.complite = set()
        self.dif = 0

        self.products = Product.objects.all()

        if self.mp:

            # Make the Pool of workers
            pool = ThreadPool(4)

            # Open the urls in their own threads
            # and return the results
            pool.map(self.get_match, self.products)

            #close the pool and wait for the work to finish 
            pool.close()
            pool.join()

        else:
            for product in self.products:
                self.get_match(product)

        Log.objects.add(subject = "catalog.updater.{}".format(self.updater.alias),
                        channel = "info",
                        title = "Updated",
                        description = "Updated")

    def get_match(self, product):

#        print(product)
        products = Product.objects.filter(article__iexact = product.article, vendor = product.vendor)
        for n, product in enumerate(products):
            if n:
                print('Delete:', product)
                product.delete()
