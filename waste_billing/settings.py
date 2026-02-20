from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'replace-this-with-a-secure-one-for-production'
DEBUG = True # keep True while developing


ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
'core',
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


ROOT_URLCONF = 'waste_billing.urls'


TEMPLATES = [
{
'BACKEND': 'django.template.backends.django.DjangoTemplates',
'DIRS': [BASE_DIR / 'templates'],
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


WSGI_APPLICATION = 'waste_billing.wsgi.application'


# Use SQLite for simplicity (no DB server required). If you want MySQL, I can provide config.
DATABASES = {
'default': {
'ENGINE': 'django.db.backends.sqlite3',
'NAME': BASE_DIR / 'db.sqlite3',
}
}


AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] # add your project-level static
STATIC_ROOT = BASE_DIR / 'static_root' # used with collectstatic in production


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# ========================
# EMAIL CONFIGURATION (Gmail SMTP)
# ========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'YOUR_GMAIL@gmail.com'       # <-- Replace with your Gmail address
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'     # <-- Replace with your Gmail App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ========================
# OTP SETTINGS
# ========================
OTP_EXPIRY_MINUTES = 5  # OTP validity duration
OTP_MAX_ATTEMPTS = 5     # Maximum verification attempts
