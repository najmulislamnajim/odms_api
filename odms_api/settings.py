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

# Logger setup
# Ensure log directories exist
os.makedirs(BASE_DIR / 'logs/delivery', exist_ok=True)

# Custom Date Formatter to format date and time into Dhaka timezone
class DhakaFormatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp, pytz.timezone("Asia/Dhaka"))
        return dt

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

# Custom Filter to set log level
class LevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level
        
    def filter(self, record):
        record.levelname = self.level
        return record.levelno == self.level

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
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
    },
    'filters':{
        'info_only':{
            '()': LevelFilter,
            'level': logging.INFO,
        },
        'error_only':{
            '()': LevelFilter,
            'level': logging.ERROR,
        },
        'critical_only':{
            '()': LevelFilter,
            'level': logging.CRITICAL,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'delivery_info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/delivery/info.log',
            'formatter': 'standard',
            'filters': ['info_only'],
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,  
        },
        'delivery_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/delivery/error.log',
            'formatter': 'standard',
            'filters': ['error_only'],
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5, 
        },
        'delivery_critical': {
            'level': 'CRITICAL',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/delivery/critical.log',
            'formatter': 'standard',
            'filters': ['critical_only'],
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5, 
        },
        
    },
    'loggers':{
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'delivery_app': {
            'handlers': ['delivery_info', 'delivery_error', 'delivery_critical'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

runserver.default_port = "8001"