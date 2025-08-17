"""
Test settings for Finance Tracker project.
This file contains settings specifically for running tests.
"""

from .settings import *

# Use in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Use faster password validation
AUTH_PASSWORD_VALIDATORS = []

# Disable debug mode for tests
DEBUG = False

# Use a simple secret key for tests
SECRET_KEY = 'test-secret-key-for-testing-only'

# Disable static file collection during tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Use simple cache backend for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable middleware that's not needed for tests
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Use simple session engine for tests
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Disable timezone support for faster tests
USE_TZ = False

# Use simple locale for tests
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

# Disable internationalization for tests
USE_I18N = False
USE_L10N = False
