.. _deployment:

Deployment
==========

See the instructions for deploying a django project on the 
`django deployment page <http://docs.djangoproject.com/en/dev/howto/deployment/modwsgi/>`_

.. note::

    You'll need to add the path of your project to the python path just as you
    did lingcod. 

Apache Configuration
--------------------

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


Nginx/Gunicorn Configuration
--------------------------------
nginx is an alternate high-performance, low memory footprint web server. It can use gunicorn to serve django wsgi apps.

Installation
++++++++++++
With Ubuntu::

    sudo apt-get install nginx
    sudo pip install gunicorn

    # If you use eventlet
    sudo pip install eventlet

    # or gevent 
    sudo apt-get install libevent-dev
    sudo pip install gevent

Configuration
+++++++++++++

/etc/nginx/nginx.conf::

    worker_processes 1;

    user www-data gisdev;

    events {
        worker_connections 1024;
        accept_mutex off;
    }

    http {
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        types_hash_max_size 2048;
        include /etc/nginx/mime.types;
        default_type application/octet-stream;
        gzip on;
        gzip_buffers 32 8k;
        gzip_types
            text/html
            application/javascript
            text/javascript
            text/css
            text/xml
            application/atom+xml
            application/json
            application/xml;

        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

        include /etc/nginx/sites-enabled/*;
    }

/etc/nginx/sites-enabled/app::

    upstream app_server {
        server localhost:8000 fail_timeout=0;
    }

    server {
        server_name server.org;
        access_log /var/log/nginx/app.access.log;
        error_log /var/log/nginx/app.error.log info;
        keepalive_timeout 5;
        client_max_body_size 20M; # file upload size
        root /var/www/;
        
        location /media/admin {
            alias /usr/local/src/django/django/contrib/admin/media/;
        }

        location /media {
            alias /usr/local/media/app/; 
        }

        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_redirect off;

            if (!-f $request_filename) {
                proxy_pass http://app_server;
                break;
            }
        }

    }

Next start the application server listening on the specified host:port (in this example, `localhost:8000`). 
You can technically just run the django development server::

    python manage.py runserver 127.0.0.1:8000

But that's not a good practice for deploying production sites. Instead we can use a gunicorn wsgi server with an asynchronous event handler::

    gunicorn_django --log-file=/tmp/app.log -w 3 -k gevent /usr/local/src/project/app/settings.py -u www-data -b 127.0.0.1:8000 --daemon

Finally, in order to ensure that the gunicorn process starts automatically, create an init script; A fairly comprehensive solution for managing multiple gunicorn servers can be found at `gunicorn-init <https://github.com/spack/gunicorn-init>`_. If you need to manage mutiple servers in different virtual environments, take a look at `this init script <http://thomas.pelletier.im/2010/05/gunicorn-django-debian-init-script/>`_ for some ideas. 
