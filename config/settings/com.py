from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext_lazy as _
import os, environ
from datetime import timedelta

ROOT_DIR = environ.Path(__file__) - 3  # (/a/b/myfile.py - 3 = /)
APPS_DIR = ROOT_DIR.path('main')
CONF_DIR = ROOT_DIR.path('config')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
env.read_env('.env')

SECRET_KEY = env("SECRET_KEY", default='rw#izqc=s@pq91+h!4aubi5snxdm$kxor999+yupo^7al0s3&0')

DEBUG = env.bool("DEBUG", True)

SITE_ID = int(env("SITE_ID", default='1'))

INSTALLED_APPS = [
    'channels',
    'jet.dashboard',
    'jet',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'crequest',
    'rest_framework',
    'dj_rest_auth',
    'drf_yasg',
    'corsheaders',
    'allauth',
    'allauth.account',

    'main.core',
    'main.filemanager',
    'main.notify',
    'main.taskapp',
    'main.users',
    'main.programs',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crequest.middleware.CrequestMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(APPS_DIR.path('templates')),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.core.context_processors.site',
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

MIGRATION_MODULES = {"sites": "main.core.contrib.sites.migrations"}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_settings.py')) as f: exec(f.read())

WSGI_APPLICATION = 'config.wsgi.application'

ROOT_URLCONF = 'config.urls'

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'main.users.backends.UserModelBackend',
)

MEDIA_FILEMANAGER_MODEL = 'filemanager.FileManager'

ADMIN_URL = env('ADMIN_URL', default="admin/")

LOGIN_URL = f"/{ADMIN_URL}login/"

LOCALE_PATHS = (str(APPS_DIR('locale')), str(CONF_DIR('locale')),)

LANGUAGE_CODE = env('LANGUAGE_CODE', default="en")

LANGUAGES = (
    ('en', _('English')),
    ('tr', _('Türkçe')),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_TITLE  = "Haktiv site admin"
SITE_HEADER = "Haktiv administration"
INDEX_TITLE = "Dashboard administration"

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.DEBUG: 'info',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

STATIC_ROOT = str(ROOT_DIR('public/static'))

STATIC_URL = '/static/'

STATICFILES_DIRS = (str(APPS_DIR.path('static', )),)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

MEDIA_ROOT = str(ROOT_DIR('public/media'))

MEDIA_URL = '/media/'

REDIS_URL = ('localhost', 6379) #env.str('REDIS_URL', default=('localhost', 6379))
ASGI_APPLICATION = "config.routing.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL,],
        },
    },
}

DEFAULT_USER_AVATAR = STATIC_URL + "assets/img/user.png"
DEFAULT_USER_FOLDER = "users"

X_FRAME_OPTIONS = 'SAMEORIGIN' # Django-JET admin popup required

JET_DEFAULT_THEME = 'light-gray'

JET_THEMES = [
    {
        'theme': 'default', # theme folder name
        'color': '#47bac1', # color of the theme's button in user menu
        'title': 'Default' # theme title
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = env.str("EMAIL_HOST", "smtp.gmail.com")
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')

# INTERNAL_PLATFORM_DOMAIN = env.str("INTERNAL_PLATFORM_DOMAIN")
# INTERNAL_PLATFORM_NAME = env.str("INTERNAL_PLATFORM_NAME")