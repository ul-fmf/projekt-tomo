from django.utils.translation import gettext_lazy as _

from .common import *

PUTKA_PERSONALITY = 'rtk'
PROMETHEUS_DEPLOY = 'rtk'

IS_LANG_ACTUALLY_SUPPORTED = {
	PROG_LANGS.auto: True,
	PROG_LANGS.txt: True,
	PROG_LANGS.c: True,
	PROG_LANGS.cpp: True,
	PROG_LANGS.pas: True,
	PROG_LANGS.java: True,
	PROG_LANGS.py_noauto: False,
	PROG_LANGS.py3: True,
	PROG_LANGS.perl: False,
	PROG_LANGS.cs: True,
	PROG_LANGS.prolog: False,
	PROG_LANGS.rb: False,
	PROG_LANGS.rust: True,
	PROG_LANGS.kotlin: False,
	PROG_LANGS.go: False,
}
assert set(IS_LANG_ACTUALLY_SUPPORTED.keys()) == {key for key, _ in PROG_LANGS.choices}

# For setting descriptions see common.py
DOMAIN = 'putka-rtk.acm.si'
URL = 'https://' + DOMAIN
CSRF_TRUSTED_ORIGINS = [URL]
OVERALL_PAGE_TITLE = _('RTK Judge')

# Default e-mail address to use for various automated correspondence, e.g. account confirmation emails.
DEFAULT_FROM_EMAIL = "Putka RTK <expurtka.putka.upm@gmail.com>"

# The e-mail address that error messages come from, such as those sent to ADMINS and MANAGERS.
SERVER_EMAIL = DEFAULT_FROM_EMAIL

INSTALLED_APPS = ('ui.specific.rtk',) + INSTALLED_APPS

# The spam targets for exception emails.
ADMINS = (
	('Jan Bercic', 'jan.bercic@gmail.com'),
)
MANAGERS = ADMINS

DATABASES['default']['NAME'] = DATABASE_NAME
DATABASES['default']['USER'] = DATABASE_USER
DATABASES['default']['PASSWORD'] = DATABASE_PASSWORD

MIDDLEWARE = MIDDLEWARE + ('ui.specific.rtk.middleware.ProfileCompletionMiddleware',)
PROFILE_ATTENTION_GROUPS = []

# Contest settings

DEFAULT_TESTSCRIPT = """jail.limits.memory = 256  # MB
jail.limits.time = 2  # seconds
expurtka.putka.testAllOutputs()"""
