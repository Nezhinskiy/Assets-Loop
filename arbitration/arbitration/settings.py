import os
import random
import sys
from datetime import timedelta, datetime, timezone
from pathlib import Path
import logging.config

from celery.schedules import crontab
from django.utils.log import DEFAULT_LOGGING
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ['*']
#     os.getenv(
#     "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost"
# ).split(",")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_filters',
    'rest_framework',
    'bootstrap4',
    'django_select2',
    'widget_tweaks',
    'crypto_exchanges.apps.CryptoExchangesConfig',
    'banks.apps.BanksConfig',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'arbitration.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'arbitration.wsgi.application'

MULTITHREADING_MODE = os.getenv("MULTITHREADING_MODE", "True") == "True"

# Database

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "True") == "True"

if DEVELOPMENT_MODE is True:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('POSTGRES_USER'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
            },
    }


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Disable Django's logging setup

LOGGING_CONFIG = None

# Logging config

LOGLEVEL = os.environ.get('LOGLEVEL', 'error').upper()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        # console logs to stderr
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        # default for all undefined Python modules
        '': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        # Our application code
        'app': {
            'level': LOGLEVEL,
            'handlers': ['console'],
            # Avoid double logging because of root logger
            'propagate': False,
        },
        # Default runserver request logging
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
})

# Internationalization
LANGUAGE_CODE = 'ru-ru'  # 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATIC_ROOT = 'staticfiles'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom setting

PARSING_WORKER_NAME = 'celery@parsing_worker'
BASE_ASSET = 'USDT'
DATA_OBSOLETE_IN_MINUTES = 10
INTER_EXCHANGES_OBSOLETE_IN_MINUTES = 15
INTER_EXCHANGES_BEGIN_OBSOLETE_MINUTES = 2
ALLOWED_PERCENTAGE = int(os.getenv('ALLOWED_PERCENTAGE', 8))

# Celery settings

CELERY_TASK_ACKS_LATE = True
CELERY_TIMEZONE = timezone.utc

CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

# Celery beat settings

CELERY_BEAT_SCHEDULE = {
    'get_binance_fiat_crypto_list': {
        'task': 'crypto_exchanges.tasks.get_binance_fiat_crypto_list',
        'schedule': timedelta(hours=12),
        'options': {'queue': 'parsing'}
    },
    'parse_currency_market_tinkoff_rates': {
        'task': 'banks.tasks.parse_currency_market_tinkoff_rates',
        'schedule': crontab(minute='*/2', hour='4-16', day_of_week='1-5'),
        'options': {'queue': 'parsing'}
    },
    'get_all_card_2_wallet_2_crypto_exchanges_buy': {
        'task': 'crypto_exchanges.tasks.get_all_card_2_wallet_2_crypto_exchanges_buy',
        'schedule': timedelta(seconds=random.randint(40, 55)),
        'options': {'queue': 'calculating'}
    },
    'get_all_card_2_wallet_2_crypto_exchanges_sell': {
        'task': 'crypto_exchanges.tasks.get_all_card_2_wallet_2_crypto_exchanges_sell',
        'schedule': timedelta(seconds=random.randint(40, 55)),
        'options': {'queue': 'calculating'}
    },
    'get_simpl_binance_inter_exchanges_calculating': {
        'task': 'core.tasks.get_simpl_binance_inter_exchanges_calculating',
        'schedule': timedelta(seconds=random.randint(20, 25)),
        'options': {'queue': 'calculating'}

    },
    'get_complex_binance_inter_exchanges_calculating': {
        'task': 'core.tasks.get_complex_binance_inter_exchanges_calculating',
        'schedule': timedelta(seconds=random.randint(22, 28)),
        'options': {'queue': 'calculating'}
    },
}

CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/2",
    },
    # … default cache config and others
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Tell select2 which cache configuration to use:
SELECT2_CACHE_BACKEND = 'select2'
