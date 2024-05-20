import os

# Choose one of the deploys and override
from .rtk import *


class InvalidString(str):
	def __mod__(self, varname):
		from django.template.base import TemplateSyntaxError
		raise TemplateSyntaxError(f"Undefined variable or unknown value for: {varname}")

# Uncomment this to get undefined variable errors from the template system.
# TEMPLATES[0]['OPTIONS']['string_if_invalid'] = InvalidString("%s")

SPOOL_ROOT = str(BASE_DIR / 'spool')

# If an exception happens while logged in as a member of the 'ui_developers'
# group, this implicitly becomes True.
DEBUG = True
LOCAL_SECURITY_DISABLE = True
REGISTER_MODELS_IN_ADMIN = True
GRAVATAR_ENABLED = False
LANGUAGE_CODE = 'en'

DOMAIN = '127.0.0.1'
URL = 'http://' + DOMAIN

# Enable debugging in templates.
TEMPLATES[0]['OPTIONS']['debug'] = True
STORAGES['staticfiles']['BACKEND'] = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Dummy no-op cache.
# CACHES = {
# 	'default': {
# 		'BACKEND': CACHE_BASE + '.cache.backends.dummy.DummyCache',
# 	},
# }

# In-memory cache.
CACHES = {
	'default': {
		'BACKEND': CACHE_BASE + '.cache.backends.locmem.LocMemCache',
		'LOCATION': 'putka',
		'TIMEOUT': 60 * 30,  # 30 minutes
	},
}

# Do not use postgresql locally unless specified using the test runner
# config plumbing. If using postgres, make sure we're using the default.
if os.environ.get('PUTKA_TESTING_DB_OVERRIDE', None) == 'postgres':
	DATABASES = {
		'default': {
			'ENGINE': DB_ENGINE_BASE + '.db.backends.postgresql',
			'NAME': DATABASE_NAME,
			'USER': DATABASE_USER,
			'PASSWORD': DATABASE_PASSWORD,
			'HOST': '',
			'PORT': '',
		},
	}
else:
	DATABASES = {
		'default': {
			'ENGINE': DB_ENGINE_BASE + '.db.backends.sqlite3',
			'NAME': BASE_DIR / 'db.sqlite3',
			# 'TEST': {
			# 	'MIGRATE': False,
			# }
		}
	}

	# This extra config is enabled by the test config fudger when
	# PUTKA_TESTING_FULL=true is in the environment; it is meant
	# to support live server testcases, which require a physical database.
	FULL_TESTING_DB = {
		'NAME': BASE_DIR / 'db_test.sqlite3',
	}

# Don't require Redis locally
LOCALMETRICS_BACKEND = 'ui.core.controlpanel.localmetrics.local.Backend'
SERVERPUSH_REACTOR = 'ui.core.serverpush.reactors.local.Reactor'

# Prometheus for local running.
PROMETHEUS_MULTIPROC_DIR = None
PROMETHEUS_DEPLOY = 'local'

# Local logging has slightly different requirements
LOGGING['handlers']['file']['filename'] = 'ui.log'  # type: ignore
