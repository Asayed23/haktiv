# -*- coding: utf-8 -*-
from .com import *  # noqa

# DATABASES = {
#     'default': env.db('PRODB_URL', default='postgres://postgres:123456@127.0.0.1:5432/middlebeasts_db')
# }

DATABASES = {
    'default': env.db('DEVDB_URL', default='sqlite:///db.sqlite3')
}
DATABASES['default']['ATOMIC_REQUESTS'] = True

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])


ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

INSTALLED_APPS += ("gunicorn", )

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(str(ROOT_DIR), 'logs/app.log'),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'request_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(str(ROOT_DIR), 'logs/django.log'),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

# SENTRY_KEY = env('SENTRY_KEY', default="https://b7ffffff265b676395d9@sentry.io/5189493")

# sentry_sdk.init(
#     dsn=SENTRY_KEY,
#     integrations=[
#         DjangoIntegration(),
#         RedisIntegration(),
#         CeleryIntegration()
#     ],

#     # If you wish to associate users to errors (assuming you are using
#     # django.contrib.auth) you may enable sending PII data.
#     send_default_pii=True
# )