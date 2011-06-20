# Import default settings
from tomo.settings import *


# Production settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tomodev',
        'USER': 'tomo',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

MEDIA_ROOT = '/srv/dev/tomo/static/'
MEDIA_URL = '/dev/tomo/static/'
ADMIN_MEDIA_PREFIX = '/dev/tomo/media/'
TEMPLATE_DIRS = (
    '/srv/dev/tomo/templates',
)
