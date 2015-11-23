#!usr/bin/python
# -*- coding:utf-8 -*-

from base import *

# Debugging option
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = [
    '*',
]
INTERNAL_IPS = (
    '127.0.0.1',
)
DEVELOPMENT_MODE = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'modupen',
        'USER': 'root',
        'PASSWORD': config.get('mysql_dev', 'password'),
        'HOST': '',
        'PORT': '',
        'DEFAULT-CHARACTER-SET': 'utf8',
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Firebase settings
FIREBASE_USERNAME = config.get('firebase_dev', 'username')
FIREBASE_REPO_URL = config.get('firebase_dev', 'repo_url')
FIREBASE_API_SECRET = config.get('firebase_dev', 'api_secret')

# Compressor settings
COMPRESS_ENABLED = not DEBUG
