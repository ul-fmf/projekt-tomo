# Django settings for UI.
import datetime
import pathlib
from typing import List, Tuple

import icu
from debug_toolbar import settings as djdt_settings

# If an exception happens while logged in as a member of the 'ui_developers'
# group, this implicitly becomes True.
DEBUG = False

# Set our app-based runner instead of the default blind directory scan one.
TEST_RUNNER = 'ui.core.common.runner.AppDiscoverRunner'

# This can be set to True by the test config fudger under certain conditions to
# enable some config that slows testing down but is required by certain test cases.
# When in doubt, leave it as is; if not in doubt, find its usages and read
# config/settings/test.py.
FULL_TESTING = False

# Directory configuration

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
LOCAL_DJDT_ENABLED = (BASE_DIR / 'djdt_enable').is_file()
LOCAL_SILK_ENABLED = (BASE_DIR / 'silk_enable').is_file()
LOCAL_SILK_PROFILER = (BASE_DIR / 'silk_profile').is_file()
PROMETHEUS_ENABLED = (BASE_DIR / 'prometheus_enable').is_file()

# Target directory for manage.py collectstatic; default is to just shove it in the source directory.
STATIC_ROOT = '/var/www/putka/static'

# Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = (
	BASE_DIR / 'static',
)
STATICFILES_FINDERS = (
	"django.contrib.staticfiles.finders.AppDirectoriesFinder",
	"django.contrib.staticfiles.finders.FileSystemFinder",
)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'sl'
LOCALE_PATHS = (BASE_DIR / 'locale',)

# The set of supported languages is smaller than Django's, and we don't
# want pages that are only partially translated, so restrict available translations.
LANGUAGES = (
	('sl', 'Slovenščina'),
	('en', 'English'),
)

# Language sort order - used for key comparisons as key= lambda x: LANG_SORT_KEY[x]
# The ordering itself is defined by the ordering of languages in the LANGUAGES setting.
LANG_SORT_KEY = {l[0]: i for i, l in enumerate(LANGUAGES)}
LANG_COLLATOR = {
	lang: icu.Collator.createInstance(icu.Locale(lang))
	for lang, _ in LANGUAGES
}

# Converts language code to flag code associated with the language. No way this gets controversial.
LANG_COUNTRY = {
	'sl': 'si',
	'en': 'gb',
}
assert set(LANG_COUNTRY) == set([lang for lang, _ in LANGUAGES])


# The cookie used to store language settings; best have this under our control for site-support.
LANGUAGE_COOKIE_NAME = 'lang'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Ljubljana'
USE_TZ = True

# Cookiez
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# We allow any host because we listen only on localhost (goes through proxy)
ALLOWED_HOSTS = ['*']

TEMPLATES = [{
	'BACKEND': 'django.template.backends.django.DjangoTemplates',
	'APP_DIRS': True,
	'OPTIONS': {
		'context_processors': [
			'django.template.context_processors.debug',
			'django.template.context_processors.request',
			'django.contrib.auth.context_processors.auth',
			'django.contrib.messages.context_processors.messages',
			'django.template.context_processors.i18n',
			'django.template.context_processors.media',
			'django.template.context_processors.static',
			'django.template.context_processors.tz',
			'ui.core.common.context_processors.constants_from_settings',
			'ui.core.common.context_processors.putka_config',
			'ui.core.contests.views.context_processor',
			'ui.core.alerts.views.alert_context_processor',
		],
	},
}]

MIDDLEWARE = (
	'ui.core.controlpanel.localmetrics.middleware.MetricsMiddleware',
	'ui.core.pauth.backend.UserLogging',
	'ui.core.pauth.backend.Http403Middleware',
	'ui.core.wiki.middleware.MarkdownifyErrorSuppressor',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'ui.core.common.middleware.AdminDebugMiddleware',
	'ui.onsite.middleware.OnsiteMiddleware',
)
if LOCAL_DJDT_ENABLED:
	MIDDLEWARE = MIDDLEWARE[:-2] + ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE[-2:]
if LOCAL_SILK_ENABLED:
	MIDDLEWARE = ('silk.middleware.SilkyMiddleware',) + MIDDLEWARE
if PROMETHEUS_ENABLED:
	MIDDLEWARE = ('ui.core.controlpanel.prometheus.TopMiddleware',) + MIDDLEWARE + ('ui.core.controlpanel.prometheus.BottomMiddleware',)

AUTHENTICATION_BACKENDS = (
	'ui.core.pauth.backend.PutkaAuthBackend',
	'ui.core.pauth.backend.ObjectPermBackend',
	'ui.core.pauth.backend.BackdoorLoginBackend',
)
AUTH_USER_MODEL = 'expurtka.User'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'homepage'
LOGOUT_REDIRECT_URL = 'homepage'

ROOT_URLCONF = 'ui.urls'

ASGI_APPLICATION = 'ui.routing.application'

INSTALLED_APPS: Tuple[str, ...] = (
	'ui.core',
	'ui.news',
	'ui.forums',
	'ui.onsite',
	'daphne',
	'django.contrib.messages',
	'django.contrib.admin',
	'django.contrib.sessions',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.staticfiles',
	'markdownx',
	'django_registration',
	'django_recaptcha',
	'channels',
)
if LOCAL_DJDT_ENABLED:
	INSTALLED_APPS += ('debug_toolbar', 'template_profiler_panel')
if LOCAL_SILK_ENABLED:
	INSTALLED_APPS += ('silk',)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

if PROMETHEUS_ENABLED:
	DB_ENGINE_BASE = 'ui.core.controlpanel.prometheus'
else:
	DB_ENGINE_BASE = 'django'
DATABASES = {
	'default': {
		'ENGINE': DB_ENGINE_BASE + '.db.backends.postgresql',
		'NAME': '',
		'USER': '',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	},
}

if PROMETHEUS_ENABLED:
	CACHE_BASE = 'ui.core.controlpanel.prometheus'
else:
	CACHE_BASE = 'django.core'
CACHES = {
	'default': {
		'BACKEND': CACHE_BASE + '.cache.backends.redis.RedisCache',
		'LOCATION': 'unix:///var/run/redis/redis-server.sock',
		'TIMEOUT': 24 * 60 * 60,  # 1 day
	}
}

REDIS_URL = 'unix:///var/run/redis/redis-server.sock'

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Logging config.
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'standard': {
			'format': '{asctime} - {levelname} - {name}: {message}',
			'style': '{',
		},
	},
	'filters': {
		'require_debug_false': {
			'()': 'django.utils.log.RequireDebugFalse',
		},
		'require_debug_true': {
			'()': 'django.utils.log.RequireDebugTrue',
		},
	},
	'handlers': {
		'null': {
			'class': 'logging.NullHandler',
			'level': 'DEBUG',
		},
		'file': {
			'class': 'logging.FileHandler',
			'filename': '/var/log/putka/ui.log',
			'formatter': 'standard',
		},
		'console': {
			'class': 'logging.StreamHandler',
			'level': 'INFO',
			'filters': ['require_debug_true'],
			'formatter': 'standard',
		},
		'mail_admins': {
			'class': 'django.utils.log.AdminEmailHandler',
			'level': 'ERROR',
			'filters': ['require_debug_false'],
		},
	},
	'loggers': {
		'django': {
			'handlers': ['console', 'file', 'mail_admins'],
			'level': 'INFO',
			'propagate': False,
		},
		'django.request': {
			'handlers': ['console', 'file', 'mail_admins'],  # standard access logs are already handled by frontend proxies etc.
			'level': 'ERROR',
			'propagate': False,
		},
		'django.channels.server': {
			'handlers': ['console'],
			'propagate': False,
		},
		'ui': {
			'handlers': ['console', 'file', 'mail_admins'],
			'level': 'INFO',
			'propagate': False,
		},
	},
}

#
# Profiling
#

def _perm_checker(user):
	pass
	# from ui.core.pauth.sacl import is_ui_developer
	# return is_ui_developer(user)

SILKY_AUTHENTICATION = True  # User must login
SILKY_AUTHORISATION = True  # User must have permissions
SILKY_IGNORE_PATHS = [
	'/controlpanel/prometheus/export/',
	'/controlpanel/manager-alive/',
]
SILKY_PERMISSIONS = _perm_checker
SILKY_PYTHON_PROFILER = LOCAL_SILK_PROFILER
SILKY_PYTHON_PROFILER_BINARY = LOCAL_SILK_PROFILER
SILKY_PYTHON_PROFILER_RESULT_PATH = BASE_DIR / 'silk_profiles'
if LOCAL_SILK_PROFILER:
	SILKY_PYTHON_PROFILER_RESULT_PATH.mkdir(parents=True, exist_ok=True)

DEBUG_TOOLBAR_CONFIG = {
	'SHOW_TOOLBAR_CALLBACK': lambda request: _perm_checker(request.user),
}

DEBUG_TOOLBAR_PANELS = djdt_settings.PANELS_DEFAULTS + [
	'template_profiler_panel.panels.template.TemplateProfilerPanel',
]

# The window length, in minutes, for the local metrics module.
LOCALMETRICS_WINDOW_MINUTES = 2 * 24 * 60  # Two days of histogram history for local metrics.

# The backend to use for local metrics.
LOCALMETRICS_BACKEND = 'ui.core.controlpanel.localmetrics.redis.Backend'

# Prometheus.
PROMETHEUS_MULTIPROC_DIR = None
PROMETHEUS_DEPLOY = '<noname>'

#
# Putka config
#

# Putka manager connection details.
PUTKA_MANAGER = {
	'HOST': 'localhost',
	'PORT': 31415,
	'PROTO': '03',
}

SERVERPUSH_REACTOR = 'ui.core.serverpush.reactors.redis.Reactor'

# How much time does the user have to validate his registration?
ACCOUNT_ACTIVATION_DAYS = 7

# Is it possible for outsiders to register?
REGISTRATION_OPEN = True

# Markdownx settings
MARKDOWNX_MARKDOWNIFY_FUNCTION = "ui.core.wiki.markdown_support.markdown_to_html"
MARKDOWNX_MARKDOWN_EXTENSIONS = [
	'markdown.extensions.tables', 'markdown.extensions.fenced_code',
	'ui.core.wiki.markdown_support:EscapeHtml', 'ui.core.wiki.markdown_support:MathJaxExtension',
]
MARKDOWNX_UPLOAD_URLS_PATH = 'wiki:markdown-image-upload'

# Enable gravatar avatars (requires internet access).
GRAVATAR_ENABLED = True

# ##################################
# Putka core config; judge behaviour
# ##################################

# The currently active personality (overridden in their configs);
# doesn't really affect behaviour, used for testing.
PUTKA_PERSONALITY = '_'

# Overall page title. The titles are generally of the form "Tasks - Putka 5", the latter part is configured here.
OVERALL_PAGE_TITLE = 'Putka 5'

# Include things like birthday, school and graduation year in the profile forms.
EXTENDED_PROFILE = True

# Show jailrun statuses directly to users. If false, mask exit error, memory
# limit error etc. with runtime error, ACM-style.
JAILRUN_DETAILS = True

# Show presentation errors.
PRESENTATION_ERRORS = True

# Show compiler errors even during contests.
COMPILER_ERRORS = False

# Show code diffs to previous submissions of the same user+task combo to staff or not.
CODE_DIFFS = True

# The default test script, used when creating a new task.
DEFAULT_TESTSCRIPT = "expurtka.putka.testAllOutputs()"

# Groups whose users can't edit their profiles.
FROZEN_PROFILE_GROUPS: List[str] = [
	# 'groupname',
]

# Disable CAPTCHA fields on forms.
# Used mostly for local deploys.
LOCAL_SECURITY_DISABLE = False

# List of permissible IP ASN countries for registration (leave empty to allow all).
# This is in addition to captcha filtering.
REGISTRATION_COUNTRIES: Tuple[str, ...] = ('SI', )

# Register and display models on admin control panel?
REGISTER_MODELS_IN_ADMIN = False

# Activity is considered "recent" for forums if it's at most this old.
FORUM_RECENT_SPAN = datetime.timedelta(days=15)

# Maximum alert age before they're deleted regardless of views.
FORUM_ALERT_CUTOFF = datetime.timedelta(days=180)  # about half a year

# After no activity for the period below, users are auto-deactivated.
USER_DEACTIVATE_CUTOFF = datetime.timedelta(days=3*365)  # about three years

# Maximum user test age before they're deleted.
USER_TEST_CUTOFF = datetime.timedelta(days=30)  # about 1 month

from .country_enums import *  # noqa

# ENUMS
from .enums import *  # noqa

# Import the required secrets
from .secrets.secrets import *  # noqa
