# Django settings for oregon project.
from lingcod.common.default_settings import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'test_project',
        'USER': 'postgres',
     }
}

TIME_ZONE = 'America/Vancouver'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True

SECRET_KEY = '=knpq2es_kedoi-j1es=$o02nc*v$^=^8zs*&s@@nij@zev%m2'
WAVE_ID = 'wavesandbox.com!q43w5q3w45taesrfgs' # Your Google Wave Account - may not be needed

ROOT_URLCONF = 'test_project.urls'

TEMPLATE_DIRS = ( os.path.realpath(os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/')), )

INSTALLED_APPS += ( 'lingcod.raster_stats', 'mlpa', )

# For some reason, running the raster_stats tests causes
# the xml test runner to fail to output the xml
EXCLUDE_FROM_TESTS.append('lingcod.raster_stats')

KML_EXTRUDE_HEIGHT = 700

import os
MEDIA_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__),'mediaroot'))

POSTGIS_TEMPLATE='template1'

try:
    from settings_local import *
except:
    pass
