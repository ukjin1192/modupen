#!usr/bin/python
# -*- coding:utf-8 -*-

import ConfigParser
import djcelery
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_NAME = os.path.basename(PROJECT_DIR)
ROOT_DIR = os.path.dirname(PROJECT_DIR)
APPS_DIR = os.path.join(PROJECT_DIR, 'apps')
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, APPS_DIR)

# Get sensitive configuration
config = ConfigParser.ConfigParser()
config.read(ROOT_DIR + '/conf/sensitive/configuration.ini')

# Send bug reports on debug mode
ADMINS = (
    ('Developer', config.get('gmail:developer', 'email_address')),
)

# Send email through SMTP
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = config.get('gmail:smtp', 'email_address')
EMAIL_HOST_PASSWORD = config.get('gmail:smtp', 'password')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Internationalization
LANGUAGE_CODE = 'ko'
ugettext = lambda s: s
LANGUAGES = (
    ('ko', ugettext('Korean')),
    ('en', ugettext('English')),
    ('jp', ugettext('Japanese')),
    ('cn', ugettext('Chinese')),
)
LOCALE_PATHS = (
    ROOT_DIR + '/locale/',
)
USE_I18N = True
USE_L10N = True
TIME_ZONE = 'UTC'
USE_TZ = True
DEFAULT_CHARSET = 'utf-8'

def ABS_PATH(*args):
    return os.path.join(PROJECT_DIR, *args)

# Static files
STATIC_ROOT = ABS_PATH('..', 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    ABS_PATH('static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Template files
TEMPLATE_DIRS = (
    ABS_PATH('templates'),
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# Application configuration
ROOT_URLCONF = PROJECT_NAME + '.urls'
WSGI_APPLICATION = PROJECT_NAME + '.wsgi.application'
SECRET_KEY = config.get('django', 'secret_key')

# Defualt applications
INSTALLED_APPS = (
    # django-suit should come before 'django.contrib.admin'
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

# Django-suit settings
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
)

# Custom applications
INSTALLED_APPS += (
    'main',
    'utils',
    'extra',
)   

# Middlewares
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    # LocaleMiddleware should come after SessionMiddleware & CacheMiddleware
    # LocaleMiddleware should come before CommonMiddleware
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line to deactivate clickjacking protection
    # It would not allow to show site via iframe tag
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# 3rd-party applications
INSTALLED_APPS += (
    'debug_toolbar',
    'compressor',
    'redisboard',
    'djcelery',
)

# 3rd-party middlewares
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# Extend default user class
AUTH_USER_MODEL = "main.Users"

# Login & Logout URL
LOGIN_URL = '/'
LOGOUT_URL = '/logout'

# Password for OAuth logged in user
OAUTH_SECRET_PASSWORD = config.get('django', 'oauth_secret_password') 

# Facebook application ID and secret code
FACEBOOK_APP_ID = config.get('facebook', 'app_id')
FACEBOOK_SECRET_CODE = config.get('facebook', 'secret_code')

# Cloudinary API key and secret code
CLOUDINARY_API_KEY = config.get('cloudinary', 'api_key')
CLOUDINARY_API_SECRET = config.get('cloudinary', 'api_secret')

# Celery settings for async tasks
djcelery.setup_loader()
BROKER_URL = 'amqp://guest:guest@localhost:5672/'       # Use RabbitMQ as broker

# Celery beat settings for cron tasks
CELERY_IMPORTS = ('utils.cron',)
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

# Compressor settings
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OUTPUT_DIR = 'CACHE'
STATICFILES_FINDERS += (
    'compressor.finders.CompressorFinder',
)

# Custom variables
FORGOT_PWD_TTL = 60 * 60                # Time to live for forgot password cache / 1 hour
EMAIL_VERIFICATION_TTL = 60 * 60 * 24   # Time to live for email verification cache / 1 day
CACHE_TTL = 60 * 60 * 24 * 10           # Time to live for normal cache / 10 days

STORIES_PER_QUERY = 20                  # Number of stories per query / 20
COMMENTS_PER_QUERY = 10                 # Number of comments per query / 10
REPLIES_PER_QUERY = 10                  # Number of replies per query / 10
NOTIFICATIONS_PER_QUERY = 10            # Number of notifications per query / 10
RECOMMENDED_STORIES_PER_QUERY = 3       # Number of recommended stories per query / 3
BUFFER_TO_CHOOSE_POPULAR_STORIES = 10   # Number of stories to choose popular stories among processing stories / 10
HITS_TO_COMMIT = 20                     # Interval to commit hits value of story at DB / 20 times
MAX_TAGS_PER_STORY = 3                  # Maximum tags per story / 3

NICKNAME_MAX_LENGTH = 15                # Maximum length for nickname
TITLE_MAX_LENGTH = 20                   # Maximum length for title
COMMENT_MAX_LENGTH = 300                # Maximum length for comment
REPLY_MAX_LENGTH = 100                  # Maximum length for reply
NOTIFICATION_PREVIEW_MAX_LENGTH = 20    # Maximum length for notification preview 
TAG_MAX_LENGTH = 8                      # Maximum length for tag

MAX_IMAGE_SIZE = 10485760           # Maximum size for uploadable image / 10 MB
MAX_IMAGE_RATIO = 4                 # Maximum ratio of image width and height / 1:4

INACTIVATE_DAYS_TO_CLOSE_STORY = 5          # Inactive days to close story / 5 days
MIN_AGREEMENT_RATIO_TO_CLOSE_STORY = 60     # Minimum agreement ratio to close story / 60 %
MIN_COMMENTS_TO_INITIATE_CLOSING_VOTE = 20  # Minimum comments to initiate closing vote / 20

TIME_INTERVAL_FOR_NEW_STORY = 10    # Time interval limit to write new story / 10 minutes
TIME_INTERVAL_FOR_NEW_COMMENT = 1   # Time interval limit to write new story / 1 minute
TIME_INTERVAL_FOR_NEW_REPLY = 1     # Time interval limit to write new story / 1 minute
TIME_INTERVAL_FOR_EDIT_VOTE = 1     # Time interval limit to edit vote / 1 minute

SCORE_FOR_NEW_COMMENT = 5           # Score for new comment / +5
SCORE_FOR_LIKE_COMMENT = 3          # Score for like comment / +3
SCORE_FOR_DISLIKE_COMMENT = -3      # Score for dislike comment / -3
SCORE_FOR_NEW_REPLY = 1             # Score for new reply / +1
SCORE_FOR_INFORMANT = 5             # Score for informant if report was reasonable / +5
COST_TO_VOTE_DISLIKE = 1            # Cost to vote dislike / 1
MIN_DISLIKE_COUNT_TO_HIDE = 2       # Minimum dislike count to hide comment

MIN_SCORE_FOR_THE_FIRST_TITLE = 0       # Minimum score for the first title / 0 point
MIN_SCORE_FOR_THE_SECOND_TITLE = 50     # Minimum score for the second title / 50 points
MIN_SCORE_FOR_THE_THIRD_TITLE = 300     # Minimum score for the third title / 300 points
MIN_SCORE_FOR_THE_FOURTH_TITLE = 1000   # Minimum score for the fourth title / 1000 points
MIN_SCORE_FOR_THE_FIFTH_TITLE = 3000    # Minimum score for the fifth title / 3000 points
MIN_SCORE_FOR_THE_SIXTH_TITLE = 10000   # Minimum score for the sixth title / 10000 points
MIN_SCORE_FOR_THE_SEVENTH_TITLE = 50000 # Minimum score for the seventh title / 50000 points

MIN_LIKE_FOR_GOLD_MEDAL = 10        # Minimum like count for gold medal / 10 likes
MIN_LIKE_FOR_SILVER_MEDAL = 5       # Minimum like count for silver medal / 5 likes
MIN_LIKE_FOR_BRONZE_MEDAL = 2       # Minimum like count for bronze medal / 2 likes
