import os
import sys
from django.utils import timezone

# Импортируем настройки проекта Django
sys.path.append('/home/abezpalov/anodos.ru/project/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'

# Магия
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Выполняем необходимый загрузчик
print("Пробую выполнить загрузчик " + sys.argv[1])
Updater = __import__('catalog.updaters.' + sys.argv[1], fromlist=['Runner'])
runner = Updater.Runner()
if runner.updater.state:
	if runner.run():
		runner.updater.updated = timezone.now()
		runner.updater.save()
exit()
