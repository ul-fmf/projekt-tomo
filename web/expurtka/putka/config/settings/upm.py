from datetime import date
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from django.utils.functional import StrPromise

    _: Callable[[str], StrPromise]
else:
    from django.utils.translation import gettext_lazy as _

from .common import *

PUTKA_PERSONALITY = "upm"
PROMETHEUS_DEPLOY = "upm"

# For setting descriptions see common.py
DOMAIN = "putka-upm.acm.si"
URL = "https://" + DOMAIN
CSRF_TRUSTED_ORIGINS = [URL]
OVERALL_PAGE_TITLE = _("UPM Judge")

# Default e-mail address to use for various automated correspondence, e.g. account confirmation emails.
DEFAULT_FROM_EMAIL = "Putka UPM <expurtka.putka.upm@gmail.com>"

# The e-mail address that error messages come from, such as those sent to ADMINS and MANAGERS.
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# A tuple of recepients that are bcc'd on the activation emails
# (sent when user for UPM team is activated).
UPM_TEAM_ACTIVATION_EMAIL_BCC = ("prijave@upm.si",)

INSTALLED_APPS = (
    "ui.teams",
    "ui.specific.upm",
) + INSTALLED_APPS

# The spam targets for exception emails.
ADMINS = (("Jan Bercic", "jan.bercic@gmail.com"),)
MANAGERS = ADMINS

DATABASES["default"]["NAME"] = DATABASE_NAME
DATABASES["default"]["USER"] = DATABASE_USER
DATABASES["default"]["PASSWORD"] = DATABASE_PASSWORD
DATABASES["default"]["PORT"] = 6432
DATABASES["default"]["TEST"] = {
    "PORT": "",
}

# Contest settings

UPM_TEAM_REGISTRATION_OPEN = REGISTRATION_OPEN
REGISTRATION_COUNTRIES = (
    "SI",
    "BA",
    "RS",
    "MK",
    "AL",
    "HR",
    "XK",
    "IT",
    "ME",
    "CH",
    "AT",
    "DE",
)
JAILRUN_DETAILS = False
EXTENDED_PROFILE = False
PRESENTATION_ERRORS = False

DEFAULT_TESTSCRIPT = """jail.limits.time = 4  # seconds
jail.limits.memory = 256  # MB
expurtka.putka.aggregator = expurtka.putka.agg.acm

expurtka.putka.testAllOutputs(expurtka.putka.diffPEGrader)
"""

# UPM-specific

UPM_SCOREBOARD_RENDER_WITH_HIDDEN = True


# Decorator for team usernames - the name of the team's user is derived from the team name with this.
def UPM_DECORATE_TEAM_USERNAME(name: str) -> str:
    return "{}-{}".format(name, date.today().year)


# Generator for contest group names; when a new team is registered, its user is added to this group automatically.
def UPM_GET_CONTEST_GROUP_NAME() -> str:
    return "tekmovalci{}".format(date.today().year)
