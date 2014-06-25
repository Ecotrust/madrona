# Django settings for oregon project.
from madrona.common.default_settings import *

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

TEMPLATE_DIRS = (os.path.realpath(os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/')),)

INSTALLED_APPS += (
    'madrona.raster_stats', 
    'madrona.heatmap', 
    'madrona.analysistools',
    'madrona.xyquery',
    'madrona.group_management',
    'mlpa',
)

KML_EXTRUDE_HEIGHT = 700

import os
MEDIA_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__),'mediaroot'))

POSTGIS_TEMPLATE = 'template1'

try:
    from settings_local import *
except:
    pass

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# If no starspan, don't bother testing raster_stats
import subprocess
try:
    subprocess.check_call(STARSPAN_BIN, stdout=open(os.devnull,'w'), stderr=subprocess.STDOUT, shell=True)
except subprocess.CalledProcessError:
    print "Couldn't find starspan executable; not testing `madrona.raster_stats`"
    EXCLUDE_FROM_TESTS.append('madrona.raster_stats')
