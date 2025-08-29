from pathlib import Path

from decouple import config, Csv
import os
from urllib.parse import urlparse, parse_qs

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root using python-decouple if present, regardless of CWD
ENV_FILE = BASE_DIR / '.env'
if ENV_FILE.exists():
    from decouple import Config, RepositoryEnv
    config = Config(RepositoryEnv(str(ENV_FILE)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-(0p*%$d6a=fg%(6b1%l8!in68)ad_im+&1a52_p%xwx*tr#(0$')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool, default=True)

# SMSLeopard settings
SMSLEOPARD_ENVIRONMENT = config('SMSLEOPARD_ENVIRONMENT')
SMSLEOPARD_API_KEY = config('SMSLEOPARD_API_KEY')
SMSLEOPARD_API_SECRET = config('SMSLEOPARD_API_SECRET')
SMSLEOPARD_ACCESS_TOKEN = config('SMSLEOPARD_ACCESS_TOKEN')


ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='localhost,127.0.0.1')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'App',
    'App.admin.apps.AdminConfig',
    'App.reseller',
    'App.business',
    
]

# Pesapal Configurations
PESAPAL_BASE_URL = config('PESAPAL_BASE_URL', default='https://cybqa.pesapal.com/pesapalv3')
PESAPAL_CONSUMER_KEY = config('PESAPAL_CONSUMER_KEY', default='')
PESAPAL_CONSUMER_SECRET = config('PESAPAL_CONSUMER_SECRET', default='')
PESAPAL_SANDBOX = config('PESAPAL_SANDBOX', cast=bool, default=True)  # Set to False in production


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'App.reseller.context_processors.reseller_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Switch to Postgres if DATABASE_URL is provided
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    if parsed.scheme.startswith('postgres'):
        query = parse_qs(parsed.query)
        sslmode = (query.get('sslmode', ['require'])[0] or 'require')
        options = {'sslmode': sslmode}
        sslrootcert = config('DB_SSLROOTCERT', default=None)
        if sslrootcert:
            p = Path(sslrootcert)
            if not p.is_absolute():
                p = BASE_DIR / p
            options['sslrootcert'] = str(p)
        else:
            ca_default = BASE_DIR / 'config' / 'aiven-ca.pem'
            if ca_default.exists():
                options['sslrootcert'] = str(ca_default)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': (parsed.path[1:] if parsed.path else ''),
                'USER': parsed.username,
                'PASSWORD': parsed.password,
                'HOST': parsed.hostname,
                'PORT': parsed.port or 5432,
                'OPTIONS': options,
            }
        }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default=None)
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default=None)

LOGIN_URL = '/login/'

# Production Security Settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', cast=bool, default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

