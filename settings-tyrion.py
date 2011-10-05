# Import default settings
from tomo.settings import *


# Production settings

# http://www.djangosnippets.org/snippets/501/
### ACTIVE DIRECTORY SETTINGS

# AD_DNS_NAME should set to the AD DNS name of the domain (ie; example.com)
# If you are not using the AD server as your DNS, it can also be set to
# FQDN or IP of the AD server.

AD_DNS_NAME = 'warpout.fmf.uni-lj.si'
AD_LDAP_PORT = 389

AD_SEARCH_DN = 'ou=uporabniki,dc=std,dc=fmf,dc=uni-lj,dc=si'

# This is the NT4/Samba domain name
AD_NT4_DOMAIN = 'std'

AD_SEARCH_FIELDS = ['mail','givenName','sn','sAMAccountName']

AD_LDAP_URL = 'ldap://%s:%s' % (AD_DNS_NAME,AD_LDAP_PORT)

AUTHENTICATION_BACKENDS = (
    'tomo.auth.ActiveDirectoryBackend',
    'django.contrib.auth.backends.ModelBackend',
)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tomo',
        'USER': 'tomo',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

ROOT_URL = '/'
MEDIA_ROOT = '/srv/tomo/static/'
MEDIA_URL = '/static/'
STATIC_ROOT = '/srv/tomo/static/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/media/'
TEMPLATE_DIRS = (
    '/srv/tomo/templates',
)
