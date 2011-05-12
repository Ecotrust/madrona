Default Settings
================

Default settings can be found under lingcod/common/default_settings.py
Include it **at the top** of your project's settings.py file like so to 
simplify setup::
  
    from lingcod.common.default_settings import *

Once these settings are included you can override them in the projects 
settings.py or settings_local.py file.

MarineMap Settings
------------------

.. _SUPEROVERLAY_ROOT:
``SUPEROVERLAY_ROOT``
    Directory path containing access-restricted/private superoverlay kmls. 

.. _LOG_FILE:
``LOG_FILE``
    Location of the marinemap log file output. Used for debugging. Defaults to `/tmp/marinemap.log` 

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


.. _MPA_CLASS:

``MPA_CLASS``
    Set to the class representing Marine Protected Areas in your project. The 
    default for this setting is ``None``, and will cause an exception if it is
    not set.

.. _ARRAY_CLASS:

``ARRAY_CLASS``
    Set to the class representing Arrays in your project. The default for this 
    setting is ``None``, and will cause an exception if it is not set.

.. _MPA_FORM:

``MPA_FORM``
    Set to a ModelForm class for editing MPAs. Defaults to 
    ``'lingcod.mpa.forms.MpaForm'``

.. _ARRAY_FORM:

``ARRAY_FORM``
    Set to a ModelForm class for editing Arrays. Defaults to 
    ``'lingcod.mpa.forms.ArrayForm'``

.. _RELEASE:

``RELEASE``
    The next milestone or major revision number (ie ``'1.1'``)

.. _GROUP_REQUEST_EMAIL:

``GROUP_REQUEST_EMAIL``
    When user requests group membership, send email to this address (``None`` = no email sent) 

.. _GROUP_REGISTERED_BY_WEB:

``GROUP_REGISTERED_BY_WEB`` 
    Group name assigned to users who register using the web interface. Defaults to 'registered_by_web'


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
    Absolute filepath to a directory containing raster files. Used with the `lingcod.raster_stats` app. (Optional; defaults to `lingcod/raster_stats/test_data`)

.. _STARSPAN_BIN:
``STARSPAN_BIN``
    Location of the starspan executable. Used with the `lingcod.raster_stats` app. (Optional; defaults to `starspan`)

.. _HELP_EMAIL:
``HELP_EMAIL``
    Email address used in templates for users to contact in case of problems. defaults to help@marinemap.org

.. _APP_NAME:
``APP_NAME``
    Name of the application to be used in templates as the title. defaults to 'MarineMap'

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
    The `lingcod.google-analytics <http://code.google.com/p/django-google-analytics/>`_ app
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
    Contains all marinemap apps and contrib.auth, contenttypes and other
    django apps critical to marinemap functionality.

    Add new apps in your settings like so::

        INSTALLED_APPS += (
            'path.to.my.app',
        )

.. _MEDIA_ROOT:

``MEDIA_ROOT``
    Set to a default relative to trunk/media

.. _MEDIA_URL:

``MEDIA_URL``
    defaults to /media/

.. _LOGIN_URL:

``LOGIN_URL``
    set to /login/

.. _LOGIN_REDIRECT_URL:

``LOGIN_REDIRECT_URL``
    Set to the map view at the root ( ``/`` )

.. _CACHES:
``CACHES``
    see the `django docs <http://docs.djangoproject.com/en/dev/ref/settings/#caches>`_ for details on cache setup. defaults to local memory caching.
