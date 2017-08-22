import os
import sys

from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

import datetime
from django.utils import timezone
from catalog.models import *
from anodos.models import Log


class Runner:

    name  = 'Служебное: ежедневный запуск'
    alias = 'everyday'

    max_time = datetime.timedelta(0, 23*60*60, 0)

    updaters_all = [['cbr', 'fujitsu', 'kramer', 'cmo'],
                    ['auvix', 'axoft', 'comptek', 'digis', 'elko', 'europarts', 'landata',
                     'marvel', 'merlion', 'mics', 'ocs', 'rrc', 'treolan'],
                    ['tohpe', 'recalculate']]


    def __init__(self):

        self.start_time = timezone.now()

        self.updater = Updater.objects.take(alias = self.alias,
                                            name = self.name,
                                            distributor = None)

    def run(self):

        start = datetime.datetime.now()

        for updaters in self.updaters_all:

            if self.mp:
                # Make the Pool of workers
                pool = ThreadPool(4)

                # Open the urls in their own threads
                # and return the results
                pool.map(self.run_updater, updaters)

                #close the pool and wait for the work to finish 
                pool.close()
                pool.join()
            else:
                for updater in updaters:
                    self.run_updater(updater)

        print("Обработки завершены за {}.".format(datetime.datetime.now() - start))

        return True

    def run_updater(self, updater):

        # Выполняем необходимый загрузчик
        try:
            print("Run {}".format(updater))
            Runner = __import__('catalog.updaters.' + updater, fromlist=['Runner'])
            runner = Runner.Runner()
            if runner.updater.state:
                runner.test = self.test
                runner.mp = self.mp
                if runner.run():
                    runner.updater.updated = timezone.now()
                    runner.updater.save()
            print("Complite {}".format(updater))

        except Exception as error:
            Log.objects.add(subject = "catalog.updater.{}".format(updater),
                            channel = "error",
                            title = "Exception",
                            description = error)
            print("Error {}".format(updater))

    def is_time_up(self):
        'Определяет не вышло ли время'

        if timezone.now() - self.start_time > self.max_time:
                print("Время вышло {}.".format(timezone.now() - self.start_time))
                return True

        else:
            return False
