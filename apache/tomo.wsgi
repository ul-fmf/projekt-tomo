import os
import site

os.environ["DJANGO_SETTINGS_MODULE"] = "tomo.settings-tyrion"

site.addsitedir('/srv/tomo/virtualenv/lib/python2.6/site-packages')
site.addsitedir('/srv/')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
