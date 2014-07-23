# Django settings for tests
from madrona.common.default_settings import *

BASE_DIR = os.path.join(os.path.dirname(__file__), "examples", "test_project")
TEMPLATE_DIRS = (os.path.realpath(os.path.join(BASE_DIR, 'templates').replace('\\','/')),)
MEDIA_ROOT = os.path.realpath(os.path.join(BASE_DIR,'..','mediaroot'))

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
SECRET_KEY = 'IamthechromedinetteIamtheeggsofallpersuasion'
ROOT_URLCONF = 'test_project.urls'
KML_EXTRUDE_HEIGHT = 700
POSTGIS_TEMPLATE = 'template1'

INSTALLED_APPS += (
    'madrona.raster_stats', 
    'madrona.heatmap', 
    'madrona.analysistools',
    'madrona.xyquery',
    'madrona.group_management',
    'mlpa',
)
