from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
import dj_database_url
from decouple import config
import logging

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Heroku dynamically assigns a hostname, so we need to handle that
ALLOWED_HOSTS = ['*'] if DEBUG else [
    '127.0.0.1',
    'localhost',
    '.herokuapp.com',
    'snipvocab-backend-4991c989741a.herokuapp.com'
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'corsheaders',
    'shared',
    'authapi',
    'learnapi',
    'cms',
    'payment',
    'backend', # just for admin (and settings are here)
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'backend.middleware.APIKeyMiddleware',  # Add API key middleware
]

# Security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://snipvocab-ar.netlify.app",  # Production frontend
    "https://arabicwithvideos.com",       # Production frontend
    "https://snipvocab-backend-4991c989741a.herokuapp.com",  # Production backend
    "https://snipvocab.com",  # Add your deployed frontend URL here
]

if DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        "http://127.0.0.1:5173",  # Additional dev server
        "http://localhost:5173",   # Additional dev server
    ])


# CORS Headers configuration
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-api-key',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# CORS settings for production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_PRIVATE_NETWORK = True

# Add CORS_EXPOSE_HEADERS if you need to access any custom headers in frontend
CORS_EXPOSE_HEADERS = [
    'Content-Type',
    'X-API-Key',
]

# Add URL regex to ensure CORS is applied to all API endpoints
CORS_URLS_REGEX = r'^/api/.*$'

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database configuration
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Create static directory if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Stripe settings
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
if not STRIPE_SECRET_KEY:
    raise ValueError("STRIPE_SECRET_KEY environment variable is not set")

STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
if not STRIPE_PUBLISHABLE_KEY:
    raise ValueError("STRIPE_PUBLISHABLE_KEY environment variable is not set")

STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
if not STRIPE_WEBHOOK_SECRET:
    raise ValueError("STRIPE_WEBHOOK_SECRET environment variable is not set")

# Premium subscription price ID
STRIPE_PREMIUM_PRICE_ID = os.getenv('STRIPE_PREMIUM_PRICE_ID')
if not STRIPE_PREMIUM_PRICE_ID:
    raise ValueError("STRIPE_PREMIUM_PRICE_ID environment variable is not set")

# Frontend URLs for success/cancel
STRIPE_SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL', 'http://localhost:5173/subscription/success')
STRIPE_CANCEL_URL = os.getenv('STRIPE_CANCEL_URL', 'http://localhost:5173/subscription/cancel')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] '
                      'pathname=%(pathname)s lineno=%(lineno)s '
                      'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'learnapi': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'authapi': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'shared': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

# API Keys
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is not set")

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    raise ValueError("EMAIL_HOST_USER and EMAIL_HOST_PASSWORD environment variables must be set")

# Frontend password reset URL
FRONTEND_PASSWORD_RESET_URL = os.getenv('FRONTEND_PASSWORD_RESET_URL', 'http://localhost:5173/reset-password')

# API Key settings
API_KEY_HEADER = 'X-API-Key'
API_KEY = os.getenv('FRONTEND_API_KEY')
if not API_KEY:
    raise ValueError("FRONTEND_API_KEY environment variable is not set")

# Define which URL patterns require API key authentication
API_KEY_REQUIRED_PATHS = [
    r'^/learn/',  # All learnapi endpoints
    r'^/auth/',   # All authapi endpoints
]

# Define which paths should bypass API key check
API_KEY_EXEMPT_PATHS = [
    r'^/admin/',  # Django admin
    r'^/cms/',    # CMS endpoints
]
