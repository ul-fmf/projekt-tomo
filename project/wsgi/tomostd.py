"""
WSGI config for projekt-tomo.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
and
http://blog.dscpl.com.au/2012/10/requests-running-in-wrong-django.html
"""

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "project.settings.tomostd"

import site
base_path = "/srv/tomostd"
site.addsitedir(base_path)
site.addsitedir(os.path.join(base_path, "virtualenv/lib/python2.6/site-packages"))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
