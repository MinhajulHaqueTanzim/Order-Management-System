
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'secret-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Admin Registration Security
ADMIN_REGISTRATION_KEY = '12345-secure-admin-key'  

os.makedirs(os.path.join(BASE_DIR, 'media', 'products'), exist_ok=True)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'order_management.urls'
WSGI_APPLICATION = 'order_management.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


# Database configuration (required for Django sessions)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# MongoDB Configuration
MONGODB_SETTINGS = {
    'host': 'localhost',
    'port': 27017,
    'db_name': 'order_management_db'
}

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# SSLCommerz Configuration
SSLCOMMERZ_SETTINGS = {
    'store_id': 'tanzi68dfebc02e1d0',  # Sandbox Store ID
    'store_pass': 'tanzi68dfebc02e1d0@ssl',  # Sandbox Password
    'is_sandbox': True,  # Set to False for production
    'api_url': 'https://sandbox.sslcommerz.com/gwprocess/v4/api.php',  # Sandbox URL
    # For production use: 'https://securepay.sslcommerz.com/gwprocess/v4/api.php'
    'success_url': 'http://127.0.0.1:8000/api/payment/success/',
    'fail_url': 'http://127.0.0.1:8000/api/payment/fail/',
    'cancel_url': 'http://127.0.0.1:8000/api/payment/cancel/',
    'ipn_url': 'http://127.0.0.1:8000/api/payment/ipn/',
}

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 1 day

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'