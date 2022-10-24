from .common import *

INSTALLED_APPS += [
    "silk",
]
MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")

SECRET_KEY = "0vb+-_-52phz@ii^cxr+mlgvmn6fctd+v5qpnv&k+-00#u-==0"

DEBUG = True

ALLOWED_HOSTS = []

WSGI_APPLICATION = "web.wsgi.local.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "tomo.sqlite3",
    }
}

STATIC_URL = "/static/"
LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"
LOGIN_REDIRECT_URL = "/"
SUBMISSION_URL = "http://127.0.0.1:8000"
