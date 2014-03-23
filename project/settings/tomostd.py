from project.settings.common import *

SESSION_COOKIE_NAME = 'sessionstdid'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '***REMOVED***'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['.tomo.fmf.uni-lj.si', '.tomo.std.fmf.uni-lj.si']


# Application definition

WSGI_APPLICATION = 'project.wsgi.tomostd.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql_psycopg2',
        'NAME': 'tomostd',
        'USER': 'tomo',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = '/srv/tomostd/static/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

# http://www.djangosnippets.org/snippets/501/
AD_DNS_NAME = 'warpout.fmf.uni-lj.si'
AD_LDAP_PORT = 389
AD_SEARCH_DN = 'ou=uporabniki,dc=std,dc=fmf,dc=uni-lj,dc=si'
AD_NT4_DOMAIN = 'std'
AD_SEARCH_FIELDS = ['mail','givenName','sn','sAMAccountName']
AD_LDAP_URL = 'ldap://%s:%s' % (AD_DNS_NAME,AD_LDAP_PORT)
AUTHENTICATION_BACKENDS = (
    'libs.auth.ActiveDirectoryBackend',
    'django.contrib.auth.backends.ModelBackend',
)

