from .common import *

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = True

ALLOWED_HOSTS = [os.environ["ALLOWED_HOSTS"]]

WSGI_APPLICATION = "web.wsgi.docker.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": "db",
        "PORT": "",
    }
}

STATIC_ROOT = "/var/static/"
STATIC_URL = "/static/"

LOGIN_REDIRECT_URL = "/"
SUBMISSION_URL = "http://127.0.0.1:8000"
