# Django settings for oregon project.
from lingcod.common.default_settings import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'test_project'
DATABASE_USER = 'postgres'

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


MPA_CLASS = 'mlpa.models.NcMpa'
ARRAY_CLASS = 'mlpa.models.NcMpaArray'
MPA_FORM = 'mlpa.forms.MpaForm'
ARRAY_FORM = 'mlpa.forms.ArrayForm'

import os
MEDIA_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__),'mediaroot'))

try:
    from settings_local import *
except:
    pass
