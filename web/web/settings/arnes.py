from common import *
import saml2
from os import path

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
SUBMISSION_URL = 'https://www.tomo.si'

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

SAML_CONFIG = {
  'xmlsec_binary': '/usr/bin/xmlsec1',
  'entityid': 'http://tomo.arnes.si/saml2/metadata/',

  # TODO
  'attribute_map_dir': path.join(BASEDIR, 'attribute-maps'),

  # this block states what services we provide
  'service': {
      # we are just a lonely SP
      'sp' : {
          'name': 'Projekt Tomo',
          'name_id_format': saml2.saml.NAMEID_FORMAT_PERSISTENT,
          'endpoints': {
              # url and binding to the assetion consumer service view
              # do not change the binding or service name
              'assertion_consumer_service': [
                  ('http://localhost:8000/saml2/acs/',
                   saml2.BINDING_HTTP_POST),
                  ],
              # url and binding to the single logout service view
              # do not change the binding or service name
              'single_logout_service': [
                  ('http://localhost:8000/saml2/ls/',
                   saml2.BINDING_HTTP_REDIRECT),
                  ],
                  ('http://localhost:8000/saml2/ls/post',
                   saml2.BINDING_HTTP_POST),
                  ],
              },

           # attributes that this project need to identify a user
          'required_attributes': ['uid'],

           # attributes that may be useful to have but not required
          'optional_attributes': ['eduPersonAffiliation'],

          # in this section the list of IdPs we talk to are defined
          'idp': {
              # we do not need a WAYF service since there is
              # only an IdP defined here. This IdP should be
              # present in our metadata

              # the keys of this dictionary are entity ids
              'https://localhost/simplesaml/saml2/idp/metadata.php': {
                  'single_sign_on_service': {
                      saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SSOService.php',
                      },
                  'single_logout_service': {
                      saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SingleLogoutService.php',
                      },
                  },
              },
          },
      },

  # where the remote metadata is stored
  'metadata': {
      'local': [path.join(BASEDIR, 'remote_metadata.xml')],
      },

  # set to 1 to output debugging information
  'debug': 1,

  # certificate
  'key_file': path.join(BASEDIR, 'mycert.key'),  # private part
  'cert_file': path.join(BASEDIR, 'mycert.pem'),  # public part

  # own metadata settings
  'contact_person': [
      {'given_name': 'Lorenzo',
       'sur_name': 'Gil',
       'company': 'Yaco Sistemas',
       'email_address': 'lgs@yaco.es',
       'contact_type': 'technical'},
      {'given_name': 'Angel',
       'sur_name': 'Fernandez',
       'company': 'Yaco Sistemas',
       'email_address': 'angel@yaco.es',
       'contact_type': 'administrative'},
      ],
  # you can set multilanguage information here
  'organization': {
      'name': [('Yaco Sistemas', 'es'), ('Yaco Systems', 'en')],
      'display_name': [('Yaco', 'es'), ('Yaco', 'en')],
      'url': [('http://www.yaco.es', 'es'), ('http://www.yaco.com', 'en')],
      },
  'valid_for': 24,  # how long is our metadata valid
  }
