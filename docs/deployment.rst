.. _deployment:

Deployment
==========

See the instructions for deploying a django project on the 
`django deployment page <http://docs.djangoproject.com/en/dev/howto/deployment/modwsgi/>`_

.. note::

    You'll need to add the path of your project to the python path just as you
    did lingcod. 

Apache Configuration
====================

Using Apache2, you can configure your project as an apache virtual host using the following::

    <VirtualHost *:80>
            ServerName your.server.org

            Alias /media/admin/ /src/django/django/contrib/admin/media/
            <Location /media/admin>
            Order allow,deny
            Allow from all
            </Location>

            Alias /media/ /src/marinemap/media/
            <Location /media>
            Order allow,deny
            Allow from all
            Options -ExecCGI
            Options -Indexes
            </Location>

            <Location /media/upload>
            Order Allow,Deny
            Deny from all
            </Location>

            WSGIScriptAlias / /src/project/project_wsgi.py
            WSGIDaemonProcess project user=gisdev group=gisdev processes=10 threads=1
            WSGIProcessGroup project
    </VirtualHost>

    WSGIRestrictStdin Off

This file is typically placed in /etc/apache2/sites-available/project and then made available using the apache utilities::

    a2ensite project

This configuration allows admin media and standard media to be served by apache. It also locks down the media/upload directory which is where user-uploaded files will be placed; we control access to these files through django views in order to leverage authentication and security.

The wsgi script is a python file similar to this::

    #!/usr/bin/env python
    import sys
    import os

    sys.stdout = sys.stderr

    # If django is not already in python site-directories
    sys.path.append('/src/django')

    # Project specific 
    sys.path.append('/src/project')

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()
