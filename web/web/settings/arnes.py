from common import *

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['tomo.arnes.si']

WSGI_APPLICATION = 'web.wsgi.dev.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tomo',
        'USER': 'tomo',
        'PASSWORD': 'tomo',
        'HOST': 'db',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'users',
    'problems',
    'attempts',
    'bootstrap3',
    'simple_history',
    'courses',
    'taggit',
    'djangosaml2',
)

STATIC_ROOT = '/home/tomo/projekt-tomo/web/static'
STATIC_URL = '/static/'

# SAML login URL
# LOGIN_URL = '/accounts/login/'
LOGIN_URL = '/saml2/login/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

AD_DNS_NAME = 'warpout.fmf.uni-lj.si'
AD_LDAP_PORT = 389
AD_SEARCH_DN = 'ou=uporabniki,dc=std,dc=fmf,dc=uni-lj,dc=si'
AD_NT4_DOMAIN = 'std'
AD_SEARCH_FIELDS = ['mail', 'givenName', 'sn', 'sAMAccountName']
AD_LDAP_URL = 'ldap://%s:%s' % (AD_DNS_NAME, AD_LDAP_PORT)

AUTHENTICATION_BACKENDS = (
    # 'utils.auth.ActiveDirectoryBackend',
    'djangosaml2.backends.Saml2Backend',
    'django.contrib.auth.backends.ModelBackend',
)
