#!usr/bin/python
# -*- coding:utf-8 -*-

from base import *

# Debugging option
DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = [
    'modupen.com',
]
INTERNAL_IPS = (
    '127.0.0.1',
)
DEVELOPMENT_MODE = False

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'modupen',
        'USER': 'root',
        'PASSWORD': config.get('mysql_prod', 'password'),
        'HOST': config.get('mysql_prod', 'end_point'),
        'PORT': '3306',
        'DEFAULT-CHARACTER-SET': 'utf8',
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config.get('redis_prod', 'end_point'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Firebase secret code
FIREBASE_USERNAME = config.get('firebase_dev', 'username')
FIREBASE_REPO_URL = config.get('firebase_dev', 'repo_url')
FIREBASE_API_SECRET = config.get('firebase_dev', 'api_secret')

# Compressor settings
COMPRESS_ENABLED = not DEBUG
