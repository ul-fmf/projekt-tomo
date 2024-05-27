from .common import *

PUTKA_PERSONALITY = "classic"

# For setting descriptions see common.py
DOMAIN = "www.expurtka.putka.si"
URL = "https://" + DOMAIN
CSRF_TRUSTED_ORIGINS = [URL]

# Default e-mail address to use for various automated correspondence, e.g. account confirmation emails.
DEFAULT_FROM_EMAIL = "Putka <sistem@expurtka.putka.si>"

# The e-mail address that error messages come from, such as those sent to ADMINS and MANAGERS.
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# The spam targets for exception emails.
ADMINS = (("Jan Bercic", "jan.bercic@gmail.com"),)
MANAGERS = ADMINS

DATABASES["default"]["NAME"] = DATABASE_NAME
DATABASES["default"]["USER"] = DATABASE_USER
DATABASES["default"]["PASSWORD"] = DATABASE_PASSWORD
