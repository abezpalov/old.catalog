import datetime
from django.utils import timezone
from catalog.models import *
from anodos.models import Log


class Runner:

    name  = 'Служебное: ежедневный запуск'
    alias = 'everyday'

    max_time = datetime.timedelta(0, 23*60*60, 0)

    updaters = [
        'cbr',

        'auvix',
        'axoft',
        'cmo',
        'digis',
        'fujitsu',
        'kramer',
        'landata',
        'marvel',
        'merlion',
        'ocs',
        'rrc',
        'treolan',
        'mics',
        'comptek',
        'elko',
        'europarts',

        'recalculate']

    def __init__(self):

        self.start_time = timezone.now()

        self.updater = Updater.objects.take(
            alias       = self.alias,
            name        = self.name,
            distributor = None)


    def run(self):

        start = datetime.datetime.now()

        for updater in self.updaters:

            # Выполняем необходимый загрузчик
            try:
                print("Пробую выполнить загрузчик {}".format(updater))
                Runner = __import__('catalog.updaters.' + updater, fromlist=['Runner'])
                runner = Runner.Runner()
                if runner.updater.state:
                    if runner.run():
                        runner.updater.updated = timezone.now()
                        runner.updater.save()

            except Exception as error:
                Log.objects.add(
                    subject    = "catalog.updater.{}".format(updater),
                    channel    = "error",
                    title      = "Exception",
                    description = error)

            if self.is_time_up():
                return True


        print("Обработки завершены за {}.".format(datetime.datetime.now() - start))

        return True

    def is_time_up(self):
        'Определяет не вышло ли время'

        if timezone.now() - self.start_time > self.max_time:
                print("Время вышло {}.".format(timezone.now() - self.start_time))
                return True

        else:
            return False

