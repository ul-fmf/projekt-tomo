from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from django.utils.functional import StrPromise

    _: Callable[[str], StrPromise]
else:
    from django.utils.translation import gettext_lazy as _

from .upm import *

PUTKA_PERSONALITY = "cerc"
PROMETHEUS_DEPLOY = "cerc"

SPOOL_ROOT = "/var/lib/putka/spool"
SPOOL_LIMITER = "ui.printing.utils.spool_limiter"
SPOOL_SIZE_LIMIT = 64 * 1024
SPOOL_USER_TIMEOUT = 15
SPOOL_USER_COUNT = 50
SPOOL_ENABLED = lambda _: True


class PRINTJOB_STATUS_(IntegerChoices):
    waiting = 0, "waiting"
    scraped = 1, "scraped"
    delivered = 2, "delivered"


PRINTJOB_STATUS: Type[PRINTJOB_STATUS_] = PRINTJOB_STATUS_


class BALLOON_STATUS_(IntegerChoices):
    waiting = 0, "waiting"
    creating = 1, "creating"
    delivered = 2, "delivered"


BALLOON_STATUS: Type[BALLOON_STATUS_] = BALLOON_STATUS_


IS_LANG_ACTUALLY_SUPPORTED = {
    PROG_LANGS.auto: True,
    PROG_LANGS.txt: False,
    PROG_LANGS.c: True,
    PROG_LANGS.cpp: True,
    PROG_LANGS.pas: False,
    PROG_LANGS.java: True,
    PROG_LANGS.py_noauto: False,
    PROG_LANGS.py3: True,
    PROG_LANGS.perl: False,
    PROG_LANGS.cs: False,
    PROG_LANGS.prolog: False,
    PROG_LANGS.rb: False,
    PROG_LANGS.rust: False,
    PROG_LANGS.kotlin: True,
    PROG_LANGS.go: False,
}
assert set(IS_LANG_ACTUALLY_SUPPORTED) == set(
    PROG_LANGS
), f"Mismatch: {set(IS_LANG_ACTUALLY_SUPPORTED)} vs. {set(PROG_LANGS)}"

ALERT_TYPES = IntegerChoices(
    "ALERT_TYPES",
    [(a.name, (a.value, a.label)) for a in ALERT_TYPES]
    + [
        ("cerc_balloon", (100, "Balloon created")),
        ("cerc_printjob", (101, "Print job created")),
    ],
)
ALERT_SUBCLASS_MAP[ALERT_TYPES.cerc_balloon] = "ui.balloons.alerts.BalloonAlert"
ALERT_SUBCLASS_MAP[ALERT_TYPES.cerc_printjob] = "ui.printing.alerts.PrintJobAlert"
assert set(ALERT_TYPES) == set(
    ALERT_SUBCLASS_MAP
), f"{set(ALERT_TYPES)} vs. {set(ALERT_SUBCLASS_MAP)}"

# For setting descriptions see common.py
DOMAIN = "putka-cerc.acm.si"
URL = "https://" + DOMAIN
CSRF_TRUSTED_ORIGINS = [URL]
OVERALL_PAGE_TITLE = _("CERC Judge System")

# Default e-mail address to use for various automated correspondence, e.g. account confirmation emails.
DEFAULT_FROM_EMAIL = "Putka CERC <expurtka.putka.upm@gmail.com>"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# This personality is supposed to be English-only.
LANGUAGE_CODE = "en"
LANGUAGES = (("en", "English"),)


class UPM_TEAM_LOCATIONS_(TextChoices):
    Austria = "AT", "Austria"
    Czechia = "CZ", "Czech Republic"
    Croatia = "HR", "Croatia"
    Hungary = "HU", "Hungary"
    Latvia = "LV", "Latvia"
    Poland = "PL", "Poland"
    Slovakia = "SK", "Slovakia"
    Slovenia = "SI", "Slovenia"


UPM_TEAM_LOCATIONS: Type[UPM_TEAM_LOCATIONS_] = UPM_TEAM_LOCATIONS_

INSTALLED_APPS = ("ui.specific.cerc", "ui.balloons", "ui.printing") + INSTALLED_APPS
TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "ui.printing.context_processors.settings"
)

# The spam targets for exception emails.
ADMINS = (("Jan Bercic", "jan.bercic@gmail.com"),)
MANAGERS = ADMINS

DATABASES["default"]["NAME"] = DATABASE_NAME
DATABASES["default"]["USER"] = DATABASE_USER
DATABASES["default"]["PASSWORD"] = DATABASE_PASSWORD

REGISTRATION_OPEN = True
UPM_TEAM_REGISTRATION_OPEN = False
REGISTRATION_COUNTRIES = ("AT", "HR", "CZ", "HU", "PL", "SK", "SI")

PRESENTATION_ERRORS = False
COMPILER_ERRORS = True  # Remote contest, people don't have the same compilers.
UPM_SCOREBOARD_RENDER_WITH_HIDDEN = True
