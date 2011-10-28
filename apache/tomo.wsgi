import os, site

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

def maintenance_wsgi_application(environ, start_response):
    start_response('503 Service Unavailable',
                   [('Content-Type', 'text/html; charset=UTF-8')])
    with open(os.path.join(BASE_PATH, 'maintenance.html')) as f:
        return [f.read()]

if not os.path.exists(os.path.join(BASE_PATH, 'tomo.lock')):
    os.environ["DJANGO_SETTINGS_MODULE"] = "tomo.settings.production"
    site.addsitedir('/srv/tomo/virtualenv/lib/python2.6/site-packages')
    site.addsitedir('/srv')
    from django.core.handlers.wsgi import WSGIHandler
    application = WSGIHandler()
else:
    application = maintenance_wsgi_application
