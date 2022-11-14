from .docker import *

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware") + 1,
    "shibboleth.middleware.ShibbolethRemoteUserMiddleware",
)

DEBUG = False

SHIBBOLETH_ATTRIBUTE_MAP = {
    "mail": (True, "username"),
    "givenName": (True, "first_name"),
    "sn": (True, "last_name"),
    "mail": (False, "email"),
}

AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
    "django.contrib.auth.backends.ModelBackend",
    "shibboleth.backends.ShibbolethRemoteUserBackend",
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ["SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"]
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ["SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"]
SOCIAL_AUTH_FACEBOOK_KEY = os.environ["SOCIAL_AUTH_FACEBOOK_KEY"]
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ["SOCIAL_AUTH_FACEBOOK_SECRET"]
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_USER_MODEL = "users.User"
SOCIAL_AUTH_FACEBOOK_API_VERSION = "2.11"
