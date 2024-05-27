from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from django.utils.functional import StrPromise

    _: Callable[[str], StrPromise]
else:
    from django.utils.translation import gettext_lazy as _

from .classic import *

PUTKA_PERSONALITY = "tomo"
PROMETHEUS_DEPLOY = "tomo"

# For setting descriptions see common.py
DOMAIN = "kokoska.fmf.uni-lj.si"
URL = "https://" + DOMAIN
CSRF_TRUSTED_ORIGINS = [URL]
OVERALL_PAGE_TITLE = _("Tomo")

# Default e-mail address to use for various automated correspondence, e.g. account confirmation emails.
DEFAULT_FROM_EMAIL = "Projekt Tomo <info@projekt-tomo.si>"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

INSTALLED_APPS = ("ui.specific.tomo",) + INSTALLED_APPS
# TEMPLATES[0]['OPTIONS']['context_processors'].append('ui.specific.cerc.context_processors.settings')

# The spam targets for exception emails.
ADMINS = (
    ("Jan Bercic", "jan.bercic@gmail.com"),
    ("Jure Slak", "jure.slak@gmail.com"),
    ("Matija Pretnar", "matija.pretnar@fmf.uni-lj.si"),
)
MANAGERS = ADMINS

DATABASES["default"]["NAME"] = DATABASE_NAME
DATABASES["default"]["USER"] = DATABASE_USER
DATABASES["default"]["PASSWORD"] = DATABASE_PASSWORD

REGISTRATION_OPEN = True
REGISTRATION_COUNTRIES = ("AT", "HR", "CZ", "HU", "PL", "SK", "SI", "CH")

PRESENTATION_ERRORS = False
COMPILER_ERRORS = True  # Remote contest, people don't have the same compilers.
