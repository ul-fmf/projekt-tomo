from django.utils.translation import gettext_lazy as _

from .common import *

PUTKA_PERSONALITY = "ceoi"
PROMETHEUS_DEPLOY = "ceoi"

# For setting descriptions see common.py
DOMAIN = "putka-ceoi.fri.uni-lj.si"
URL = "https://" + DOMAIN
CSRF_TRUSTED_ORIGINS = [URL]
OVERALL_PAGE_TITLE = _("CEOI Judge")

# Default e-mail address to use for various automated correspondence, e.g. account confirmation emails.
DEFAULT_FROM_EMAIL = "Putka CEOI <expurtka.putka.upm@gmail.com>"

# The e-mail address that error messages come from, such as those sent to ADMINS and MANAGERS.
SERVER_EMAIL = DEFAULT_FROM_EMAIL

INSTALLED_APPS = ("ui.specific.ceoi",) + INSTALLED_APPS

# The spam targets for exception emails.
ADMINS = (("Jan Bercic", "jan.bercic@gmail.com"),)
MANAGERS = ADMINS

DATABASES["default"]["NAME"] = DATABASE_NAME
DATABASES["default"]["USER"] = DATABASE_USER
DATABASES["default"]["PASSWORD"] = DATABASE_PASSWORD
