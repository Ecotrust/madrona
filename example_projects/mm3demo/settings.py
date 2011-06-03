# Django settings for oregon project.
from lingcod.common.default_settings import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'demo',
        'USER': 'postgres',
     }
}

TIME_ZONE = 'America/Vancouver'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True

SECRET_KEY = '%$gy=knpq2essdfsfsdf_kedoi-j1es=$o02nc*v$^=^8zs*&s@@nij@zev%m2'

ROOT_URLCONF = 'mm3demo.urls'

TEMPLATE_DIRS = ( os.path.realpath(os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/')), )

INSTALLED_APPS += ( 'lingcod.raster_stats', 'mlpa', 'lingcod.analysistools')

# For some reason, running the raster_stats tests causes
# the xml test runner to fail to output the xml
EXCLUDE_FROM_TESTS.append('lingcod.raster_stats')

KML_EXTRUDE_HEIGHT = 700

import os
MEDIA_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__),'mediaroot'))

POSTGIS_TEMPLATE='template1'
APP_NAME = "MarineMap 3.0 Demo"

try:
    from settings_local import *
except:
    pass
