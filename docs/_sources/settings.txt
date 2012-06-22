Default Settings
================

Default settings can be found under madrona/common/default_settings.py
Include it **at the top** of your project's settings.py file like so to 
simplify setup::
  
    from madrona.common.default_settings import *

Once these settings are included you can override them in the projects 
settings.py or settings_local.py file.

Madrona Settings
------------------

.. _SUPEROVERLAY_ROOT:
``SUPEROVERLAY_ROOT``
    Directory path containing access-restricted/private superoverlay kmls.  

.. _LOG_FILE:
``LOG_FILE``
    Location of the madrona log file output. Used for debugging. Defaults to `/tmp/madrona.log` 

.. _GEOMETRY_DB_SRID:

``GEOMETRY_DB_SRID``
    Defines the projection that will be used for storing data in the 
    database. Default is California teale albers, you will likely want to
    change it.
      
.. _GEOMETRY_CLIENT_SRID:

``GEOMETRY_CLIENT_SRID``
    Defines the projection that is produced and consumed by the client. The
    default is 4326, compatible with the Google Earth Plugin.

.. _GOOGLE_API_KEY:

``GOOGLE_API_KEY``
    Default key works for localhost:8080.
    Obtain new keys from `Google <http://code.google.com/apis/maps/signup.html>`_

.. _GROUP_REQUEST_EMAIL:

``GROUP_REQUEST_EMAIL``
    When user requests group membership, send email to this address (``None`` = no email sent) 

.. _GROUP_REGISTERED_BY_WEB:

``GROUP_REGISTERED_BY_WEB`` 
    Group name assigned to users who register using the web interface. Defaults to 'registered_by_web'

.. _ENFORCE_SUPPORTED_BROWSER:

``ENFORCE_SUPPORTED_BROWSER``
    Boolean. Should the view check the user agent string to ensure a valid browser? Default is ``True``.

.. _KML_SIMPLIFY_TOLERANCE:

``KML_SIMPLIFY_TOLERANCE``
    Tolerance argument to the postgis simplify command used when generating viewable KMLs. Defaults to ``20``.

.. _KML_EXTRUDE_HEIGHT:

``KML_EXTRUDE_HEIGHT``
    KML output is extruded to produce 3D shapes; This setting determines the height in meters. Defaults to ``100``.

.. _KML_ALTITUDEMODE_DEFAULT:
``KML_ALTITUDEMODE_DEFAULT``
    Sets the default KML altitudeMode (usually one of: `absolute`, `clampToGround`, `relativeToGround`). 

.. _SHARING_TO_PUBLIC_GROUPS:
``SHARING_TO_PUBLIC_GROUPS``
    List of groups which have the ability to make arrays publically viewable. Defaults to ``['Share with Public']``

.. _SHARING_TO_STAFF_GROUPS:
``SHARING_TO_STAFF_GROUPS``
    List of groups which have the ability to submit mpas/arrays to staff for approval. Defaults to ``['Share with Staff']``

.. _SCREENCASTS:
``SCREENCASTS``
    Directory to store screencast movies

.. _SCREENCAST_IMAGES:
``SCREENCAST_IMAGES``
    Directory to store thumbnails and other supporting images for screencasts

.. _VIDEO_PLAYER:
``VIDEO_PLAYER``
    Path to .swf flash video player for streaming screencast videos

.. _RASTER_DIR:
``RASTER_DIR``
    Absolute filepath to a directory containing raster files. Used with the `madrona.raster_stats` app. (Optional; defaults to `madrona/raster_stats/test_data`)

.. _STARSPAN_BIN:
``STARSPAN_BIN``
    Location of the starspan executable. Used with the `madrona.raster_stats` app. (Optional; defaults to `starspan`)

.. _HELP_EMAIL:
``HELP_EMAIL``
    Email address used in templates for users to contact in case of problems. defaults to help@madrona.org

.. _APP_NAME:
``APP_NAME``
    Name of the application to be used in templates as the title. defaults to 'Madrona'

3rd Party App Settings
----------------------

.. _ACCOUNT_ACTIVATION_DAYS:
``ACCOUNT_ACTIVATION_DAYS``
    How many days do new users have to activate their account once they've registered. Default is ``7`` days.

.. _REGISTRATION_OPEN:
``REGISTRATION_OPEN``
    Boolean. Can users register themselves or not? Default is ``True``.

.. _COMPRESS:

``COMPRESS_CSS``, ``COMPRESS_JS``, ``COMPRESS_VERSION``, ``COMPRESS_AUTO``
    The `django-compress <http://code.google.com/p/django-compress/>`_ app
    is setup to compress css and js assets described in 
    ``media/css_includes.xml`` and ``media/js_includes.xml``
    
.. _GOOGLE_ANALYTICS:

``GOOGLE_ANALYTICS_MODEL``
    The `madrona.google-analytics <http://code.google.com/p/django-google-analytics/>`_ app
    (with alterations made to models.py and admin.py) 
    allows for managing of Google Analytics accounts from the Django admin page.
    
.. _BASE_DIR:

``BASE_DIR``
    Provides the path to the project codebase. 

.. _OPENID_ENABLED:

``OPENID_ENABLED``
    Boolean. Determines whether to expose OpenID authentication. False implies local user/pass authentication only. Defaults to False. 

.. _WSGI_USER:

``WSGI_USER``
    Username of the UNIX/system user which runs the wsgi process. This has implications for the ownership of the MEDIA_ROOT directory as it
    needs to be writeable by the WSGI process. Setting WSGI_USER will cause the install_media command to chown the MEDIA_ROOT directory 
    to this user. Defaults to None.

Django Settings
---------------

.. _MIDDLEWARE_CLASSES:

``MIDDLEWARE_CLASSES``
    Is defined in ``default_settings.py`` to include GZIP and Auth 
    middleware by default.

.. _INSTALLED_APPS:

``INSTALLED_APPS``
    Contains all madrona apps and contrib.auth, contenttypes and other
    django apps critical to madrona functionality.

    Add new apps in your settings like so::

        INSTALLED_APPS += (
            'path.to.my.app',
        )

.. _MEDIA_ROOT:

``MEDIA_ROOT``
    Set to a default relative to trunk/media

.. _MEDIA_URL:

``MEDIA_URL``
    This should be a full absolute path to the media directory (e.g. "http://northcoast.madrona.org/media/"). Defaults to /media/; application will work with a relative path but there may be some minor js errors to contend with.


.. _LOGIN_URL:

``LOGIN_URL``
    set to /login/

.. _LOGIN_REDIRECT_URL:

``LOGIN_REDIRECT_URL``
    Set to the map view. (Either ``/`` or ``/map/`` depending on the ``LAUNCH_PAGE`` setting.

.. _LAUNCH_PAGE:

``LAUNCH_PAGE``
    Boolean to determine if the root url is a launch page. Default is False meaning ``/`` points directly to the map view.

.. _CACHES:
``CACHES``
    see the `django docs <http://docs.djangoproject.com/en/dev/ref/settings/#caches>`_ for details on cache setup. defaults to local memory caching.

 .. 

Full settings list
-------------------

Below is a complete list of settings for the test project::

    ACCOUNT_ACTIVATION_DAYS = 7  ###
    APP_NAME = 'Madrona'  ###
    ASYNC_IS_DISABLED = False  ###
    AWS_USE_S3_MEDIA = False  ###
    BASE_DIR = '/usr/local/src/madrona/examples/test_project'  ###
    BOOKMARK_ANON_LIMIT = (100, datetime.timedelta(0, 1800))  ###
    BOOKMARK_ANON_USERNAME = 'anonymous_bookmark_user'  ###
    BOOKMARK_FEATURE = False  ###
    BROKER_BACKEND = 'djkombu.transport.DatabaseTransport'  ###
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
    CARROT_BACKEND = 'django'  ###
    CELERY_RESULT_BACKEND = 'database'  ###
    CELERY_TRACK_STARTED = True  ###
    COMPRESS_AUTO = True  ###
    COMPRESS_CSS = {'application': {'source_filenames': ['closure/assets/common.css', 'closure/assets/menus.css', 'closure/assets/menubutton.css', 'closure/assets/toolbar.css', 'common/css/typography.css', 'common/css/application.css', 'common/css/tabs.css', 'common/css/layout.css', 'common/css/menu_items.css', 'common/css/buttons.css', 'common/css/forms.css', 'common/css/closure-fixes.css', 'common/css/table.css', 'geographic_report/css/geographic_report.css', 'common/css/jquery-widgets.css', 'bookmarks/css/bookmarks.css'], 'extra_context': {'media': 'all'}, 'output_filename': 'common/css/madrona.r?.css'}}  ###
    COMPRESS_JS = {'application': {'source_filenames': ['common/js/lib/extensions.js', 'common/js/lib/jquery.form.js', 'common/js/jquery/jquery.selText.js', 'common/js/madrona.js', 'common/js/lib/tmpl.js', 'common/js/lib/smartresize.js', 'common/js/lib/ge_utility_lib_patches.js', 'common/js/lib/raphael-js/raphael.js', 'common/js/lib/raphael_ext.js', 'common/js/tools/measure_tool.js', 'common/js/layout/layout.js', 'common/js/layout/panel.js', 'common/js/layout/shortTextArea.js', 'common/js/layout/menu_items.js', 'common/js/map/map.js', 'common/js/map/googleLayers.js', 'common/js/map/geocoder.js', 'common/js/lib/json2.js', 'common/js/jquery/jquery.ui.slider.js', 'common/js/jquery/jquery-callback-1.2.js', 'common/js/jquery/jquery.localscroll-1.2.7-min.js', 'common/js/jquery/jquery.scrollTo-1.4.2-min.js', 'common/js/tools/formats.js', 'manipulators/js/manipulators.js', 'common/js/graphics.js', 'common/js/ui/table.js', 'geographic_report/js/geographicReport.js', 'features/features.js', 'features/js/workspace.js', 'features/js/kmlEditor.js', 'bookmarks/js/bookmarks.js'], 'output_filename': 'madrona.r?.js'}, 'tests': {'source_filenames': ['common/js/test/lib/tmpl.js', 'common/js/test/lib/ge_utility_lib_patches.js', 'common/js/test/tools/measure_tool.js', 'common/js/test/layout/panel.js', 'common/js/test/map/googleLayers.js', 'common/js/test/map/geocoder.js', 'manipulators/js/test/manipulators.js'], 'output_filename': 'madrona_tests.r?.js'}}  ###
    COMPRESS_VERSION = True  ###
    DATABASES = {'default': {'ENGINE': 'django.contrib.gis.db.backends.postgis', 'TEST_MIRROR': None, 'NAME': 'test_project', 'TEST_CHARSET': None, 'TIME_ZONE': 'America/Vancouver', 'TEST_COLLATION': None, 'PORT': '', 'HOST': '', 'USER': 'postgres', 'TEST_NAME': None, 'PASSWORD': '', 'OPTIONS': {}}}
    DEBUG = True
    DISPLAY_AREA_UNITS = 'sq_mi'  ###
    DISPLAY_LENGTH_UNITS = 'mi'  ###
    ENFORCE_SUPPORTED_BROWSER = True  ###
    EXCLUDE_FROM_TESTS = ['south', 'registration', 'django.contrib.auth', 'django.contrib.admin', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.sites', 'django.contrib.gis']  ###
    GEOMETRY_CLIENT_SRID = 4326  ###
    GEOMETRY_DB_SRID = 3310  ###
    GOOGLE_ANALYTICS_MODEL = True  ###
    GOOGLE_API_KEY = 'ABQIAAAAu2dobIiH7nisivwmaz2gDhT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSLaQmJjJuOq03hTEjc-cNV8eegYg'  ###
    GROUP_REGISTERED_BY_WEB = 'registered_by_web'  ###
    GROUP_REQUEST_EMAIL = None  ###
    HELP_EMAIL = 'help@madrona.org'  ###
    INSTALLED_APPS = ('madrona.common', 'django.contrib.auth', 'django.contrib.admin', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.sites', 'django.contrib.gis', 'compress', 'madrona.shapes', 'madrona.google-analytics', 'madrona.layers', 'madrona.studyregion', 'madrona.simplefaq', 'madrona.help', 'madrona.staticmap', 'madrona.screencasts', 'madrona.news', 'madrona.manipulators', 'madrona.kmlapp', 'madrona.features', 'madrona.user_profile', 'madrona.unit_converter', 'madrona.openid', 'madrona.async', 'madrona.loadshp', 'madrona.bookmarks', 'registration', 'south', 'djcelery', 'djkombu', 'madrona.raster_stats', 'madrona.heatmap', 'madrona.analysistools', 'madrona.xyquery', 'madrona.group_management', 'mlpa')
    KML_ALTITUDEMODE_DEFAULT = 'absolute'  ###
    KML_EXTRUDE_HEIGHT = 700  ###
    KML_SIMPLIFY_TOLERANCE = 20  ###
    KML_SIMPLIFY_TOLERANCE_DEGREES = 0.0002  ###
    LOGIN_REDIRECT_URL = '/'
    LOGIN_URL = '/accounts/signin/'
    LOG_FILE = None  ###
    MEDIA_ROOT = '/usr/local/src/madrona/examples/test_project/mediaroot'
    MEDIA_URL = '/media/'
    MIDDLEWARE_CLASSES = ('django.middleware.gzip.GZipMiddleware', 'django.middleware.common.CommonMiddleware', 'madrona.common.middleware.IgnoreCsrfMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.contrib.messages.middleware.MessageMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.middleware.transaction.TransactionMiddleware', 'madrona.openid.middleware.OpenIDMiddleware')
    OPENID_ENABLED = False  ###
    POSTGIS_TEMPLATE = 'template1'  ###
    PRIVATE_KML_ROOT = '/mnt/EBS_superoverlays/display'  ###
    REGISTRATION_OPEN = True  ###
    ROOT_URLCONF = 'test_project.urls'  ###
    SCREENCASTS = 'screencasts/'  ###
    SCREENCAST_IMAGES = 'screencasts/images'  ###
    SECRET_KEY = '=knpq2es_kedoi-j1es=$o02nc*v$^=^8zs*&s@@nij@zev%m2'
    SETTINGS_MODULE = 'test_project.settings'  ###
    SHARING_TO_PUBLIC_GROUPS = ['Share with Public']  ###
    SHARING_TO_STAFF_GROUPS = ['Share with Staff']  ###
    SITE_ID = 1  ###
    SKIP_SOUTH_TESTS = True  ###
    SOUTH_TESTS_MIGRATE = False  ###
    STARSPAN_BIN = 'starspan'  ###
    STATICMAP_AUTOZOOM = True  ###
    STATIC_URL = '/media/admin/'
    TEMPLATE_CONTEXT_PROCESSORS = ('django.contrib.auth.context_processors.auth', 'django.core.context_processors.debug', 'django.core.context_processors.i18n', 'django.core.context_processors.media', 'django.contrib.messages.context_processors.messages', 'django.core.context_processors.request', 'madrona.openid.context_processors.authopenid')
    TEMPLATE_DEBUG = True
    TEMPLATE_DIRS = ('/usr/local/src/madrona/examples/test_project/templates',)
    TIME_ZONE = 'America/Vancouver'
    TITLES = {'self': 'View'}  ###
    USER_DATA_ROOT = '/mnt/EBS_userdatalayers/display'  ###
    VIDEO_PLAYER = '/media/screencasts/video_player/player-viral.swf'  ###
    WAVE_ID = 'wavesandbox.com!q43w5q3w45taesrfgs'  ###
