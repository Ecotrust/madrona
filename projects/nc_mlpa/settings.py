import os

from lingcod.common.default_settings import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

EMAIL_USE_TLS = True

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'simple_example'             # Or path to database file if using sqlite3.
DATABASE_USER = 'postgres'             # Not used with sqlite3.
# DATABASE_PASSWORD = ''         # Not used with sqlite3.
# DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
# DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Vancouver'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

#Screencast videos, images, and video-player locations
SCREENCASTS = 'projects/nc_mlpa/screencasts/'
SCREENCAST_IMAGES = 'projects/nc_mlpa/screencasts/images'
VIDEO_PLAYER = MEDIA_URL + 'screencasts/video_player/player-viral.swf'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6c(kr8r%aqf#r8%arr=0py_7t9m)wgocwyp5g@!j7eb0erm(2+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

ROOT_URLCONF = 'nc_mlpa.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
)

INSTALLED_APPS += (
    'lingcod.screencasts',
    'mlpa',
    'report',
)

# lingcod.intersection configuration
SAT_OPEN_COAST = 'satopencoast'
SAT_ESTURINE = 'satestuarine'

# Define the models which will represent the MPA and Array child classes
MPA_CLASS = 'mlpa.models.MlpaMpa'
ARRAY_CLASS = 'mlpa.models.MpaArray'
MPA_FORM = 'mlpa.forms.MpaForm'
ARRAY_FORM = 'mlpa.forms.ArrayForm'

COMPRESS_JS['application']['source_filenames'] += (
    'projects/nc_mlpa/js/mlpa.js',
    'projects/nc_mlpa/js/mpa_form.js',
)


COMPRESS_CSS['application']['source_filenames'] += (
    'projects/nc_mlpa/css/closure_fixes.css',
    'projects/nc_mlpa/css/mlpa_forms.css',
)

# Location where Ecotrust Fishing Data layers can be found
# This variable should actually be set in settings_local.py, just placed here to ensure correct compile
GIS_DATA_ROOT = ''

from settings_local import *