"""
Django settings for production environment.

Overrides base settings for production deployment.
IMPORTANT: Set all sensitive values via environment variables in production.
"""

from .base import *

# Production-specific settings
DEBUG = False

# Ensure allowed hosts are properly configured
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='',
    cast=Csv()
)
ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h]

# CSRF trusted origins for deployed domains (must include scheme)
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=Csv()
)
CSRF_TRUSTED_ORIGINS = [o for o in CSRF_TRUSTED_ORIGINS if o]

# Security settings - enable in production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Use production database (typically PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
        # Transaction poolers (e.g., Supabase PgBouncer) work best with short-lived app DB connections.
        'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=0, cast=int),
        'OPTIONS': {
            'sslmode': config('DB_SSLMODE', default='require'),
            'connect_timeout': config('DB_CONNECT_TIMEOUT', default=10, cast=int),
        },
    }
}

# Static files - use WhiteNoise in production
STATIC_ROOT = BASE_DIR / 'staticfiles'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    *[m for m in MIDDLEWARE if m != 'django.middleware.security.SecurityMiddleware'],
]
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media files - use Supabase Storage (S3-compatible) when configured.
SUPABASE_PROJECT_REF = config('SUPABASE_PROJECT_REF', default='').strip()
SUPABASE_STORAGE_BUCKET = config('SUPABASE_STORAGE_BUCKET', default='').strip()
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='').strip()
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='').strip()
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1').strip()

USE_SUPABASE_STORAGE = all(
    [
        SUPABASE_PROJECT_REF,
        SUPABASE_STORAGE_BUCKET,
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
    ]
)

if USE_SUPABASE_STORAGE:
    _supabase_s3_endpoint = f'https://{SUPABASE_PROJECT_REF}.supabase.co/storage/v1/s3'
    STORAGES['default'] = {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'bucket_name': SUPABASE_STORAGE_BUCKET,
            'access_key': AWS_ACCESS_KEY_ID,
            'secret_key': AWS_SECRET_ACCESS_KEY,
            'endpoint_url': _supabase_s3_endpoint,
            'region_name': AWS_S3_REGION_NAME,
            'default_acl': 'public-read',
            'querystring_auth': False,
            'file_overwrite': False,
        },
    }
    MEDIA_URL = (
        f'https://{SUPABASE_PROJECT_REF}.supabase.co/storage/v1/object/public/'
        f'{SUPABASE_STORAGE_BUCKET}/'
    )

# CORS - restrict to known origins
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='',
    cast=Csv()
)

# Email configuration for production
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Logging to file in production
LOGGING = {
    **LOGGING,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Cache configuration (Redis when available, fallback for simple deployments)
REDIS_URL = config('REDIS_URL', default='')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'hooptrack-cache',
        }
    }

# Session engine uses configured default cache backend.
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
