import os
os.environ["CELERY_LOADER"] = "django"

# !!!!!!!!!!!!!!!!!!!!!!!
# DONT FORGET TO DOCUMENT ANY NEW SETTINGS IN /docs/settings.rst
# !!!!!!!!!!!!!!!!!!!!!!

RELEASE = '3.0dev' # The next milestone
APP_NAME = 'MarineMap'

LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False

GEOMETRY_DB_SRID = 3310
GEOMETRY_CLIENT_SRID = 4326
DISPLAY_LENGTH_UNITS = 'mi' # Choices can be found in django.contrib.gis.measure.Distance.UNITS  Most common will be mi, m, km, nm, ft
DISPLAY_AREA_UNITS = 'sq_mi' # Choices can be found in django.contrib.gis.measure.Area.UNITS  Most common will be sq_mi, sq_m, sq_km, sq_nm, sq_ft

GOOGLE_API_KEY = 'ABQIAAAAu2dobIiH7nisivwmaz2gDhT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSLaQmJjJuOq03hTEjc-cNV8eegYg'

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
    'lingcod.common.middleware.IgnoreCsrfMiddleware', 
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'lingcod.openid.middleware.OpenIDMiddleware',
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
    'lingcod.kmlapp',
    'lingcod.features',
    'lingcod.user_profile',
    'lingcod.unit_converter',
    'lingcod.openid',
    'lingcod.async',
    'lingcod.loadshp',
    'lingcod.bookmarks',
    'registration',
    'south',
    'djcelery', 
    'djkombu',
    ##### Optional Apps ####
    #'lingcod.intersection',
    #'lingcod.replication',
    #'lingcod.bioregions',
    #'lingcod.data_manager',
    #'lingcod.data_distributor',
    #'lingcod.depth_range',
    #'lingcod.geographic_report',
    #'lingcod.spacing',
    #'lingcod.heatmap', 
    #'lingcod.analysistools',
    #'lingcod.bioeconomic_model',
    #'lingcod.raster_stats',
    #'lingcod.pg_spacing',
    #'lingcod.straightline_spacing',
    #'lingcod.xyquery',
    #'lingcod.wave',
    #'lingcod.group_management',
)

EXCLUDE_FROM_TESTS = [
    'south', 
    'registration',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.gis'
]

ACCOUNT_ACTIVATION_DAYS = 7 # New users have one week to activate account
REGISTRATION_OPEN = True # Can users register themselves or not?
GROUP_REQUEST_EMAIL = None # When user requests group membership, send email to this address (None = no email sent) 
GROUP_REGISTERED_BY_WEB = 'registered_by_web'  #Group name assigned to users who register using the web interface

MEDIA_ROOT = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + '/../../media/')

MEDIA_URL = '/media/'

LOGIN_URL = '/accounts/signin/'

LOGIN_REDIRECT_URL = '/'

ADMIN_MEDIA_PREFIX = '/media/admin/'

# KML SETTINGS
KML_SIMPLIFY_TOLERANCE = 20 # meters
KML_SIMPLIFY_TOLERANCE_DEGREES = 0.0002 # Very roughly ~ 20 meters
KML_EXTRUDE_HEIGHT = 100
KML_ALTITUDEMODE_DEFAULT = 'absolute'

# SHARING SETTINGS
SHARING_TO_PUBLIC_GROUPS = ['Share with Public']
SHARING_TO_STAFF_GROUPS = ['Share with Staff']

# TEMPLATE SETTINGS
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',
    'lingcod.openid.context_processors.authopenid',
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

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

#Celery and djkombu settings (for server-side asynchronous process handling)
CARROT_BACKEND = "django"
CELERY_RESULT_BACKEND = "database"
CELERY_TRACK_STARTED = True
BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
# Make sure to add any modules containing tasks
#CELERY_IMPORT = ('myapp.tasks',)

import djcelery
djcelery.setup_loader()

#The following is used to determine whether the async app (and celery) should be used 
ASYNC_IS_DISABLED = False

AWS_USE_S3_MEDIA = False  # Set true IF you want to use S3 to serve static media. 
                          # If true, need to set AWS_ACCESS_KEY, AWS_SECRET_KEY and AWS_MEDIA_BUCKET and MEDIA_URL

OPENID_ENABLED = False
LOG_FILE = None # write log to stdout

PRIVATE_KML_ROOT = '/mnt/EBS_superoverlays/display'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'example',
        'USER': 'postgres',
     }
}

# UNIX username which owns the wsgi process.
# Used to set ownership of MEDIA_ROOT 
# None = MEDIA_ROOT is owned by whoever runs the install_media command
WSGI_USER = None

CACHES = {
    'default': {
        #'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        #'LOCATION': '/tmp/django-cache',
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

HELP_EMAIL = 'help@marinemap.org'

STATICMAP_AUTOZOOM = True

TITLES = {
    'self': 'Attributes',
}

# Do you want bookmarks to show up in the kmleditor (True) or just the tool panel (False)?
BOOKMARK_FEATURE = False
