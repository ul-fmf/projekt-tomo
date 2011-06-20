import os
import site

os.environ["DJANGO_SETTINGS_MODULE"] = "tomo.settings-dev"

site.addsitedir('/srv/dev/tomo/virtualenv/lib/python2.6/site-packages')
site.addsitedir('/srv/dev')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
