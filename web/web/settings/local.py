from common import *

SECRET_KEY = '0vb+-_-52phz@ii^cxr+mlgvmn6fctd+v5qpnv&k+-00#u-==0'

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

WSGI_APPLICATION = 'web.wsgi.local.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_URL = '/static/'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# Tell nose to measure coverage on the 'problems', 'attemtps', 'courses' and 'users' apps
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=problems,attempts,courses,users',
]