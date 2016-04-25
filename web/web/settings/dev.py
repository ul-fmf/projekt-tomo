from .common import *

with open(os.path.join(os.path.dirname(BASE_DIR), 'secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

DEBUG = True

ALLOWED_HOSTS = ['tomo.fmf.uni-lj.si']

WSGI_APPLICATION = 'web.wsgi.dev.application'

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

STATIC_ROOT = '/srv/tomodev/static/'

STATIC_URL = '/uvp/static/'
LOGIN_URL = '/uvp/accounts/login/'
LOGOUT_URL = '/uvp/accounts/logout/'
LOGIN_REDIRECT_URL = '/uvp/'
SUBMISSION_URL = 'https://tomo.fmf.uni-lj.si'

AD_DNS_NAME = 'warpout.fmf.uni-lj.si'
AD_LDAP_PORT = 389
AD_SEARCH_DN = 'ou=uporabniki,dc=std,dc=fmf,dc=uni-lj,dc=si'
AD_NT4_DOMAIN = 'std'
AD_SEARCH_FIELDS = ['mail', 'givenName', 'sn', 'sAMAccountName']
AD_LDAP_URL = 'ldap://%s:%s' % (AD_DNS_NAME, AD_LDAP_PORT)
AUTHENTICATION_BACKENDS = (
    'utils.auth.ActiveDirectoryBackend',
    'django.contrib.auth.backends.ModelBackend',
)
