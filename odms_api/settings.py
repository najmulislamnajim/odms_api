import os, environ, logging, pytz
from datetime import datetime
from pathlib import Path
from django.core.management.commands.runserver import Command as runserver

# Environ Setup
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'rest_framework',
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

ROOT_URLCONF = 'odms_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'odms_api.wsgi.application'
CORS_ALLOW_ALL_ORIGINS = env.list("CORS_ALLOW_ALL_ORIGINS")


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DEFAULT_DB_NAME'),
        'USER': env('DEFAULT_DB_USER'),
        'PASSWORD': env('DEFAULT_DB_PASSWORD'),
        'HOST': env('DEFAULT_DB_HOST'),
        'PORT': env('DEFAULT_DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------------------
# Rest of the settings are for Logging
# -------------------------------------------------------------

# ------------------------------
# Ensure log directories exist
# ------------------------------
def ensure_log_dirs(apps):
    for app in apps:
        os.makedirs(BASE_DIR / 'logs' / app, exist_ok=True)

apps = ['delivery', 'collection']  # Add new apps here
ensure_log_dirs(apps)

# ------------------------------
# Custom Dhaka timezone formatter
# ------------------------------
class DhakaFormatter(logging.Formatter):
    def converter(self, timestamp):
        tz = pytz.timezone("Asia/Dhaka")
        dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc).astimezone(tz)
        return dt

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

# ------------------------------
# Custom filter for log levels
# ------------------------------
class LevelFilter(logging.Filter):
    def __init__(self, levelno):
        super().__init__()
        self.levelno = levelno
        self.levelname = logging.getLevelName(levelno)

    def filter(self, record):
        record.levelname = self.levelname
        return record.levelno == self.levelno

# ------------------------------
# Common formatters and filters
# ------------------------------
formatters = {
    'standard': {
        '()': DhakaFormatter,
        'format': '{levelname} {name} {lineno} {asctime} {filename} {funcName} {message}',
        'style': '{',
        'datefmt': '%d-%m-%Y %H:%M:%S'
    },
    'simple': {
        '()': DhakaFormatter,
        'format': '{levelname} {lineno} {asctime} {filename} {funcName} {message}',
        'style': '{',
        'datefmt': '%d-%m-%Y %H:%M:%S'
    }
}

filters = {
    'info_only': {'()': LevelFilter, 'levelno': logging.INFO},
    'error_only': {'()': LevelFilter, 'levelno': logging.ERROR},
    'critical_only': {'()': LevelFilter, 'levelno': logging.CRITICAL},
}

# ------------------------------
# Function to create app handlers
# ------------------------------
def create_app_handlers(app_name):
    return {
        f'{app_name}_info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / app_name / 'info.log',
            'formatter': 'standard',
            'filters': ['info_only'],
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
        },
        f'{app_name}_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / app_name / 'error.log',
            'formatter': 'standard',
            'filters': ['error_only'],
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
        },
        f'{app_name}_critical': {
            'level': 'CRITICAL',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / app_name / 'critical.log',
            'formatter': 'standard',
            'filters': ['critical_only'],
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
        },
    }

# ------------------------------
# Build handlers dynamically
# ------------------------------
handlers = {'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'}}
for app in apps:
    handlers.update(create_app_handlers(app))

# ------------------------------
# Build loggers dynamically
# ------------------------------
loggers = {'': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False}}
for app in apps:
    loggers[f'{app}_app'] = {
        'handlers': [f'{app}_info', f'{app}_error', f'{app}_critical'],
        'level': 'INFO',
        'propagate': False
    }

# ------------------------------
# Final LOGGING config
# ------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': formatters,
    'filters': filters,
    'handlers': handlers,
    'loggers': loggers
}
