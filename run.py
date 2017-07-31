import os
import sys

from django.utils import timezone

# Импортируем настройки проекта Django
sys.path.append('/home/ubuntu/anodos.ru/anodos/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'anodos.settings'

# Магия
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Выполняем необходимый загрузчик
print("Пробую выполнить загрузчик " + sys.argv[1])
Runner = __import__('catalog.updaters.' + sys.argv[1], fromlist=['Runner'])

for arg in sys.argv:
    if 'test' == arg:
        test = True
        break
    else:
        test = False

for arg in sys.argv:
    if 'mp' == arg:
        mp = True
        break
    else:
        mp = False

runner = Runner.Runner()
if runner.updater.state:
    runner.test = test
    runner.mp = mp
    if runner.run():
        runner.updater.updated = timezone.now()
        runner.updater.save()
exit()
