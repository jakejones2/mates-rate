"""
Django settings for trumps project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
import ast
import subprocess
from pathlib import Path


def get_environ_vars():
    """
    Sets environment variables for AWS elasticbeanstalk.
    Returns a dictionary of key-value pairs
    """
    completed_process = subprocess.run(
        ["/opt/elasticbeanstalk/bin/get-config", "environment"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    return ast.literal_eval(completed_process.stdout)


# toggle these for local dev and debugging
DEBUG = False
dev_mode = False
dockerised = False
use_aws_eb = False
use_postgres_with_docker = False
use_sqlite_with_docker = True
use_render = True

if not dev_mode and use_aws_eb:
    ENV_VARS = get_environ_vars()

BASE_DIR = Path(__file__).resolve().parent.parent

if dev_mode:
    SECRET_KEY = "django-insecure-s)pj#h8@4*=tg006ztfen0%2+ad6^-z#22u9qjjlj^+k@iy53h"
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
elif use_aws_eb:
    SECRET_KEY = ENV_VARS["DJANGO_SECRET_KEY"]
    ALLOWED_HOSTS = [
        "127.0.0.1",
        "localhost",
        ENV_VARS["ALLOWED_HOST1"],
        ENV_VARS["ALLOWED_HOST2"],
        ENV_VARS["ALLOWED_HOST3"],
        ENV_VARS["ALLOWED_HOST4"],
        ENV_VARS["ALLOWED_HOST5"],
    ]
else:
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-s)pj#h8@4*=tg006ztfen0%2+ad6^-z#22u9qjjlj^+k@iy53h")
    ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# Application definition

INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "coverage",
    # my apps
    "basicgame.apps.BasicGameConfig",
]

ASGI_APPLICATION = "trumps.asgi.application"

if use_render:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [os.getenv("RENDER_REDIS_URL")],
            },
        },
    }
elif dockerised:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": ["redis://mr_cache:6379/0"],
            },
        },
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(ENV_VARS["REDIS_HOSTNAME"], ENV_VARS["REDIS_PORT"])],
            },
        },
    }

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "basicgame.middleware.NoCachingMiddleware",
]

ROOT_URLCONF = "trumps.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "trumps.wsgi.application"

# Logging

if not dev_mode:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "time_message": {
                "format": "{asctime}: {message}",
                "style": "{",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": os.getenv("DJANGO_LOG_FILE_PATH"),
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "formatter": "time_message",
            },
        },
        "loggers": {
            "": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "handlers": ["file"],
            },
        },
    }


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


if dockerised and use_postgres_with_docker:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "matesrate",
            "USER": "jakejones",
            "PASSWORD": "matesrate",
            "HOST": "mr_db",
            "PORT": "5432",
        }
    }
elif dev_mode or (dockerised and use_sqlite_with_docker) or use_render:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "TEST": {
                "NAME": BASE_DIR / "db.sqlite3",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": ENV_VARS["RDS_DB_NAME"],
            "USER": ENV_VARS["RDS_USERNAME"],
            "PASSWORD": ENV_VARS["RDS_PASSWORD"],
            "HOST": ENV_VARS["RDS_HOSTNAME"],
            "PORT": ENV_VARS["RDS_PORT"],
        }
    }


STATIC_ROOT = BASE_DIR.joinpath("static/")
STATIC_URL = "/static/"

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
