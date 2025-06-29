import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-development-key')
DEBUG = True
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'dashboard',
    'social_django',
    'home',
    'assistant',
    'UserProfile',
    'ai',
    'csa',
    'triggers',
    'platform_connections',
    'chatui',
    'channels',
    'faq_management',
    'mycrm',
    'task',
    'interaction',
    'settings',
    'team',  # New team management app
    'django_mailbox',
    'email_utility',
    'tickets',
    'crispy_forms',
    'crispy_tailwind',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = '247csa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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

WSGI_APPLICATION = '247csa.wsgi.application'

# Database
if os.environ.get('DOCKER_ENVIRONMENT') == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'csa247',
            'USER': 'csa247user',
            'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
            'HOST': 'db',
            'PORT': '3306',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Static files
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',  # <--- your actual JS/css/images folder
]

STATIC_ROOT = BASE_DIR / 'staticfiles'  # <--- only used when you run `collectstatic`

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Google OAuth2 settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-client-id'  # Google Client ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-client-secret'  # Google Client Secret

# Login URLs
LOGIN_URL = 'authentication:login'
LOGIN_REDIRECT_URL = 'home:home'
LOGOUT_URL = 'authentication:logout'
LOGOUT_REDIRECT_URL = 'authentication:login'

# CRM specific settings
ADMIN_EMAIL = "admin@example.com"
ADMIN_URL = "admin/"
DOMAIN_NAME = "localhost:8000"

# Email settings (if you want to use email features)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '247CSA <noreply@247csa.com>')

# Debug prints
print("Email Settings:")
print(f"EMAIL_HOST_USER: {EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'SET' if EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"DEFAULT_FROM_EMAIL: {DEFAULT_FROM_EMAIL}")

# Django-mailbox Configuration
DJANGO_MAILBOX = {
    'STORE_ORIGINAL_MESSAGE': True,
    'COMPRESS_ATTACHMENTS': False,
    'ATTACHMENT_UPLOAD_TO': 'mailbox_attachments/%Y/%m/%d/',
    'PROCESS_UNREAD_MESSAGES': True,
    'STRIP_UNALLOWED_MIMETYPES': False,
    'ALLOWED_MIMETYPES': None,
    'GMAIL_IMAP_FOLDER': 'INBOX',  # Specifically target the inbox
    'GMAIL_IMAP_KEEP_EMAILS': True,
    'PROCESS_LATEST_MESSAGES_FIRST': True,  # Process newest messages first
    'MAX_MESSAGES_PER_FETCH': 10,  # Limit number of messages per fetch
}



# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# JWT settings
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# Security settings for iframe embedding and CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",  # Add your frontend domain
    "http://127.0.0.1:3000",  # Add your frontend domain
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

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
]

# Security settings for chat widget
X_FRAME_OPTIONS = 'ALLOWALL'  # This allows embedding in any domain
CSRF_COOKIE_SAMESITE = 'None'  # Required for cross-origin requests
CSRF_COOKIE_SECURE = True  # Required when SameSite=None
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',  # Add your frontend domain
    'http://127.0.0.1:3000',  # Add your frontend domain
]

# Add security middleware settings
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_SSL_REDIRECT = False

# Channels
ASGI_APPLICATION = '247csa.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

