from common import *
import saml2
from os import path

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['www.projekt-tomo.si']

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

STATIC_ROOT = '/home/tomo/projekt-tomo/web/static'
STATIC_URL = '/static/'

LOGIN_URL = 'https://www.projekt-tomo.si/Shibboleth.sso/Login'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'
SUBMISSION_URL = 'https://www.projekt-tomo.si'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware'
)
SHIBBOLETH_ATTRIBUTE_MAP = {
   'uid': (True, 'username'),
   'givenName': (True, 'first_name'),
   'sn': (True, 'last_name'),
   'mail': (False, 'email'),
}
AD_DNS_NAME = 'warpout.fmf.uni-lj.si'
AD_LDAP_PORT = 389
AD_SEARCH_DN = 'ou=uporabniki,dc=std,dc=fmf,dc=uni-lj,dc=si'
AD_NT4_DOMAIN = 'std'
AD_SEARCH_FIELDS = ['mail', 'givenName', 'sn', 'sAMAccountName']
AD_LDAP_URL = 'ldap://%s:%s' % (AD_DNS_NAME, AD_LDAP_PORT)

AUTHENTICATION_BACKENDS = (
    'utils.auth.ActiveDirectoryBackend',
    'social.backends.google.GoogleOAuth2',
    'social.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'shibboleth.backends.ShibbolethRemoteUserBackend',
)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ['SOCIAL_AUTH_GOOGLE_OAUTH2_KEY']
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ['SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET']
SOCIAL_AUTH_FACEBOOK_KEY = os.environ['SOCIAL_AUTH_FACEBOOK_KEY']
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ['SOCIAL_AUTH_FACEBOOK_SECRET']
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

SOCIAL_AUTH_USER_MODEL = 'users.User'
