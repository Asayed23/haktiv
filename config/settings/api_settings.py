REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
        'main.users.backends.permissions.EnsureAuthenticated',
        'main.users.backends.permissions.IsResearcher',
        'main.users.backends.permissions.IsCustomer',
        'main.users.backends.permissions.IsTriager',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
    # Throttle Middleware settings
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
        # 'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
        # 'contacts': '1000/day',
        # 'uploads': '20/day'
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=315),  # 5 Hours + 15 Minutes
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,  # This expire the refresh token after rotates.

    'ALGORITHM': 'HS512',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=20),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    "USE_SESSION_AUTH": True,
    "PERSIST_AUTH": False,
    "APIS_SORTER": 'alpha',
    "exclude_namespaces": [],  # List URL namespaces to ignore
    "api_version": 'alpha 1.0',  # API's version
    "api_path": "/api-docs/",  # the path to API (it could not be a root level)
    "enabled_methods": [  # method to enable in Swagger UI
        'get',
        'post',
        'put',
        'patch',
        'head',
        'delete',
        'option',
    ],
    "api_key": '',  # An API key
    "is_authentcated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
}

# FORCE_SCRIPT_NAME = '/api/v1/'

from password_strength import PasswordPolicy

PASSWORD_POLICY = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=2,  # need min. 2 uppercase letters
    numbers=2,  # need min. 2 digits
    special=2,  # need min. 2 special characters
    nonletters=2,  # need min. 2 non-letter characters (digits, specials, anything)
)

STAGE2_AUTH = {
    'APPLICATION_ISSUER_NAME': "Haktive",
    'TWOFACTOR_TIMEOUT': env("TWOFACTOR_TIMEOUT", default=60),
}

CORS_ORIGIN_WHITELIST = (
    "localhost:8080",
    "localhost:8000",
    'localhost:3000',
    "localhost:9000",
    "127.0.0.1:8080",
    "127.0.0.1:8000",
    '127.0.0.1:3000',
    "127.0.0.1:9000",
)

CORS_ALLOWED_ORIGINS = (
    "http://localhost:8080",
    "http://localhost:8000",
    'http://localhost:3000',
    "http://localhost:9000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8000",
    'http://127.0.0.1:3000',
    "http://127.0.0.1:9000",
)

# CORS_ALLOWED_ORIGIN_REGEXES = [
#     r"^https://\w+\.haktiv\.com$",
#     r"^http://localhost\:\d+{4}$",
#     r"^http://127.0.0.1\:\d+{4}$",
# ]

from corsheaders.defaults import default_methods, default_headers

CORS_ALLOW_METHODS = default_methods

CORS_ALLOW_HEADERS = default_headers

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CORS_URLS_REGEX = r'^/api/.*$'

ALLOWED_COUNTRY_CODE_LIST = ["EG", "ND"]

LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

BACKEND_SCHEMA = env("BACKEND_SCHEMA", default="https://")
BACKEND_DOMAIN = env("BACKEND_DOMAIN", default="example.com")
BACKEND_BASE_URL = f"{BACKEND_SCHEMA}{BACKEND_DOMAIN}"

FRONTEND_SCHEMA = env("FRONTEND_SCHEMA", default="https://")
FRONTEND_DOMAIN = env("FRONTEND_DOMAIN", default="example.com")
FRONTEND_BASE_URL = f"{FRONTEND_SCHEMA}{FRONTEND_DOMAIN}"
FRONTEND_SITE_NAME = env("FRONTEND_SITE_NAME", default="Haktiv")
FRONTEND_LOGO_LARGE = env("FRONTEND_LOGO_LARGE", default="https://cdn.example.com/img/logo-lg.png")

PASSWORD_EXPIRE_DAYS = env.int("PASSWORD_EXPIRE_DAYS", default=60)

REWARD_MATRIX = {
    "na": {"bounty": 0, "points": -5, "swag": -5},
    "info": {"bounty": 0, "points": 1, "swag": 1},
    "low": {"bounty": 5, "points": 5, "swag": 5},
    "medium": {"bounty": 10, "points": 15, "swag": 15},
    "high": {"bounty": 15, "points": 30, "swag": 30},
    "critical": {"bounty": 20, "points": 50, "swag": 50},
}

RANKING_MECHANISM = {
    "new-comer": {"min": 0, "max": 4},
    "junior": {"min": 5, "max": 300},
    "hacker": {"min": 301, "max": 900},
    "phreak": {"min": 901, "max": 1800},
    "1337": {"min": 1801, "max": 3000},
    "dragon": {"min": 3001, "max": 4500},
    "alien": {"min": 4501, "max": 6300},
}

CORS_ORIGIN_WHITELIST = CORS_ORIGIN_WHITELIST + (BACKEND_DOMAIN, FRONTEND_DOMAIN,)
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS + (BACKEND_BASE_URL, FRONTEND_BASE_URL,)

REST_USE_JWT = True

JWT_AUTH_COOKIE = 'haktiv'

REST_AUTH_SERIALIZERS = {
    # 'LOGIN_SERIALIZER': 'path.to.custom.LoginSerializer',
    'TOKEN_SERIALIZER': 'main.auth.serializers.HaktivTokenObtainPairSerializer',
}

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_MAX_LENGTH = 50
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False