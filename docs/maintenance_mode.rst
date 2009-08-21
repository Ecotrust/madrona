.. _maintenance_mode:

Maintenance Mode
================

When performing maintenance on the server, application, or datasets within the
application, it may be necessary to redirect users away from the application.
To facilitate this, MarineMap utilizes the `django-maintenancemode <http://pypi.python.org/pypi/django-maintenancemode>`_
app. More information can be found at that app's homepage, but usually it's as
simple as adding the following setting to settings_local.py and restarting the
server.

.. code-block:: django

    MAINTENANCE_MODE = True