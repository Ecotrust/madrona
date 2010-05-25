import os

# !!!!!!!!!!!!!!!!!!!!!!!
# DONT FORGET TO DOCUMENT ANY NEW SETTINGS IN /docs/settings.rst
# !!!!!!!!!!!!!!!!!!!!!!

RELEASE = '1.4' # The next milestone

GEOMETRY_DB_SRID = 3310

GEOMETRY_CLIENT_SRID = 4326

GOOGLE_API_KEY = 'ABQIAAAAu2dobIiH7nisivwmaz2gDhT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSLaQmJjJuOq03hTEjc-cNV8eegYg'

# Define the models which will represent the MPA and Array child classes
MPA_CLASS = None
ARRAY_CLASS = None
MPA_FORM = None
ARRAY_FORM = None

from lingcod.common import assets

COMPRESS_CSS = {
    'application': {
        'source_filenames': assets.get_css_files(),
        'output_filename': 'common/css/marinemap.r?.css',
        'extra_context': {
            'media': 'all'
        }
    }
}

COMPRESS_JS = {
    'application': {
        'source_filenames': assets.get_js_files(),
        'output_filename': 'marinemap.r?.js'
    },
    'tests': {
        'source_filenames': assets.get_js_test_files(),
        'output_filename': 'marinemap_tests.r?.js'
    }
}

COMPRESS_VERSION = True
COMPRESS_AUTO = True

GOOGLE_ANALYTICS_MODEL = True

MIDDLEWARE_CLASSES = (
    # GZip speeds up downloads by compressing on the fly
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

INSTALLED_APPS = (
    'lingcod.common',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.gis',
    'compress',
    'lingcod.shapes',
    'lingcod.google-analytics', 
    'lingcod.layers',
    'lingcod.studyregion',
    'lingcod.simplefaq',
    'lingcod.help',
    'lingcod.staticmap',
    'lingcod.screencasts',
    'lingcod.news',
    'lingcod.manipulators',
    'lingcod.array',
    'lingcod.mpa',
    'lingcod.sharing',
    'lingcod.wave',
    'lingcod.kmlapp',
    'lingcod.rest',
    'lingcod.intersection',
    'lingcod.replication',
    'lingcod.bioregions',
    'lingcod.data_manager',
    'lingcod.data_distributor',
    'lingcod.depth_range',
    'lingcod.geographic_report',
    'lingcod.spacing',
    'lingcod.user_profile',
    'registration',
    'south',
)

ACCOUNT_ACTIVATION_DAYS = 7 # New users have one week to activate account
REGISTRATION_OPEN = True # Can users register themselves or not?
GROUP_REQUEST_EMAIL = None # When user requests group membership, send email to this address (None = no email sent) 
GROUP_REGISTERED_BY_WEB = 'registered_by_web'  #Group name assigned to users who register using the web interface

MEDIA_ROOT = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + '/../../media/')

MEDIA_URL = '/media/'

LOGIN_URL = '/accounts/login/'

LOGIN_REDIRECT_URL = '/'

ADMIN_MEDIA_PREFIX = '/media/admin/'

# KML SETTINGS
KML_SIMPLIFY_TOLERANCE = 20
KML_EXTRUDE_HEIGHT = 100

# SHARING SETTINGS
SHARING_TO_PUBLIC_GROUPS = ['Share with Public']
SHARING_TO_STAFF_GROUPS = ['Share with Staff']

# TEMPLATE SETTINGS
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request'
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

#MIDDLEWARE_CLASSES = (
#    'django.middleware.common.CommonMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
#)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#Screencast videos, images, and video-player locations
SCREENCASTS = 'screencasts/'
SCREENCAST_IMAGES = 'screencasts/images'
VIDEO_PLAYER = MEDIA_URL + 'screencasts/video_player/player-viral.swf'

# This path is used by lingcod.layers.views to handle requests initiated by a UserLayerList 
USER_DATA_ROOT = '/mnt/EBS_userdatalayers/display'

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

AWS_USE_S3_MEDIA = False  # Set true IF you want to use S3 to serve static media. 
                          # If true, need to set AWS_ACCESS_KEY, AWS_SECRET_KEY and AWS_MEDIA_BUCKET, AWS_MEDIA_SUBDIR and MEDIA_URL
