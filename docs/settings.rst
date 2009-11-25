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

3rd Party App Settings
----------------------

.. _COMPRESS:

``COMPRESS_CSS``, ``COMPRESS_JS``, ``COMPRESS_VERSION``, ``COMPRESS_AUTO``
    The `django-compress <http://code.google.com/p/django-compress/>`_ app
    is setup to compress css and js assets described in 
    ``media/css_includes.xml`` and ``media/js_includes.xml``

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
    defaults to /media

.. _LOGIN_URL:

``LOGIN_URL``
    set to /login/

.. _LOGIN_URL:

``LOGIN_REDIRECT_URL``
    Set to the map view at the root ( ``/`` )

