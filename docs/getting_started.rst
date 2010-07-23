.. _getting_started:

Getting Started
===============

Introduction
************
MarineMap is a framework for building web-based spatial decision support tools. 
Originally designed to support the :ref:`California Marine Life Protection Act Initiative<background>`, 
MarineMap has evolved into a reusable platform for marine and terrestrial applications. 
If your problem involves spatial data and multi-user collaboration, MarineMap is the premier tool. 

This documentation is aimed at developers/programmers who want to
implement a MarineMap based project of their own. You should be familiar with

    * programming in Python
    * how web application are structured in `Django <http://djangoproject.com>`_
    * the command line interface in a unix-style operating system
    * the basics of `Mercurial <http://mercurial.selenic.com/>`_ source control

These instructions will walk you through developing a basic implementation of
MarineMap. This includes installing from the development repository, setting
up a sample app, testing that everything installed smoothly, then doing some
basic customization. By the end you'll have an application that will perform
all the `basic functions <http://code.google.com/p/marinemap/wiki/FeaturesAndRequirements>`_ 
needed to start drawing MPAs on a map.

.. _dependencies:

Dependencies
************
You need the following installed on your system in order to start running
MarineMap.

    * A working installation of `GeoDjango <http://geodjango.org>`_ (which has it's own set of dependencies including proj, gdal and postgres/postgis)
    * `django-compress <http://code.google.com/p/django-compress/>`_ (requires CSSTidy, look @ the 1.2 release for binaries)
    * `elementtree <http://effbot.org/zone/element-index.htm>`_
    * `django-maintenancemode <http://pypi.python.org/pypi/django-maintenancemode>`_
    * `sphinx <http://sphinx.pocoo.org/>`_ is used for generating documentation
    * `mapnik <http://mapnik.org/>`_ generates static maps for reports
    * `feedvalidator <http://www.feedvalidator.org/docs/howto/install_and_run.html>`_ for testing KML
    * `beautiful soup 3.0 <http://www.crummy.com/software/BeautifulSoup/>`_ is necessary for running tests. Be sure you have version >= 3.0
    * `xlwt <http://pypi.python.org/pypi/xlwt/>`_ for handling Excel spreadsheets
    * `django-registration <http://pypi.python.org/pypi/django-registration>`_ provides the user account managment and registration (Version 0.8+ is required - v0.7 wont work so don't use easy_install! Use `0.8alpha1 <http://bitbucket.org/ubernostrum/django-registration/downloads/django-registration-0.8-alpha-1.tar.gz>`_ instead.)
    * `south <http://south.aeracode.org/>`_ for database schema migrations
    * `networkx <http://networkx.lanl.gov/>`_ for graph networks in the spacing app
    * `pip <http://pip.openplans.org/>`_ for package management (optional)
    * `celery <http://celeryproject.org/>`_ for asynchronous task management (optional)
    * `ghettoq <http://pypi.python.org/pypi/ghettoq/>`_ as a task queue for celery (optional)

Most of the dependencies are well-behaved python packages; They can be installed using standard python package management tools such as `pip <http://pip.openplans.org/>`_. 
We have created a `pip requirements file <http://marinemap.googlecode.com/hg/marinemap_requirements.txt>`_ which can be used to install most of the dependencies::

    cd /usr/local # Assuming you want to put stuff in /usr/local/src
    pip install -r http://marinemap.googlecode.com/hg/marinemap_requirements.txt    

Some dependencies are a bit trickier and take additional installtion steps. Specifically geodjango, postgis and mapnik are not easily installed so refer to the links above. 

.. note::
    MarineMap development tends to follow django trunk. It may work on the 
    point releases but it's safer to just start from source.

Project Structure
*****************

It is important to understand how a MarineMap application is structured. There are essentially two codebases:

    * lingcod - a python module providing a set of django apps that contain the core functionality common to all MarineMap instances.
    * the project code - a django project which implements and extends the functionality provided by lingcod (specific to the particular project's needs).

By seperating the two codebases, we can more easily maintain multiple MarineMap projects while continuing to improve the underlying core functionality.
If you are creating your own project from scratch, you will likely only need to work on the project-specific code; the lingcod library can be installed 
just like any other python module and you should't need to mess with any lingcod code.

Installing Lingcod
*******************

First you will need to checkout a copy of the default branch of lingcod from the `project page <http://code.google.com/p/marinemap/source/checkout>`_ ::

     cd ~/src
     hg clone https://marinemap.googlecode.com/hg/ marinemap  

.. note::
     Though the top-level directory name is 'marinemap', the python module provided by this code is called 'lingcod'

To install, use the setup.py script provided. We recommend using the 'develop' command instead of 'install' as this
allows you to alter the lingcod code in place without reinstalling.::

    cd marinemap
    python setup.py develop

Finally, confirm that we can import the lingcod module. This example simply prints out the release number::

    python -c "from lingcod.common import default_settings; print default_settings.RELEASE"
    
Using the Sample App
********************

Inside the example-projects/ directory there are sample applications built
using the MarineMap components. These serve as useful documentation as well as
practical tests. We'll be starting up ``example-projects/test_project`` here.

using settings.py and settings_local.py
---------------------------------------

Take a look at ``example-projects/test_project/settings_local.template`` and 
``settings.py``. MarineMap uses a simple splitsetting scheme as described 
`here <http://code.djangoproject.com/wiki/SplitSettings#Multiplesettingfilesimportingfromeachother>`_. What this enables is the ability to specify standard 
settings in settings.py and commit them to a public repository, but these
don't correspond to any particular machine. You then create a 
settings_local.py file on the machine for deployment or development from the
template, and it contains your passwords and such.

Lets do that now. Copy settings_local.template to settings_local.py, then
uncomment the following line::

    # SECRET_KEY = '6c(kr8r%aqf#r8%arr=0py_7t9m)wgocwyp5g@!j7eb0erm(2+sdklj23'

Alter ``SECRET_Key`` to make it unique. Next uncomment and alter the following
lines as needed to allow this application to connect to your local database::

    # DATABASE_NAME = 'simple_example'
    # DATABASE_USER = 'postgres'
    # DATABASE_PASSWORD = 'my-secret-password'
    
handling media
--------------
Because a MarineMap instance is split between lingcod (core functionality) and the project-specific code, static media files such as html, javascript, css, images, etc. may exist in both. Django, however, expects all the static media to be in a single directory. In order to merge the lingcod media with the project media, you need to create a third (empty) media directory and set it as your MEDIA_ROOT in the project settings_local.py ::

    mkdir /tmp/test_media
    cd ~/src/marinemap/example_projects/test_project/
    echo "MEDIA_ROOT='/tmp/test_media'" >> settings_local.py

Then use the 'install_media' management command to merge all the media files into the MEDIA_ROOT directory::

    python manage.py install_media


setup the database
------------------

Create a database accessible by the connection settings above using a tool
like `pgAdmin <http://www.pgadmin.org/>`_. It is very important that this
database be created from a template with all the PostGIS functions installed. One approach
is to set up postgis in the default postgres database called template1::

   #run as postgres superuser
   POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib
   createlang -d template1 plpgsql # Adding PLPGSQL language support.
   psql -d template1 -f $POSTGIS_SQL_PATH/postgis.sql # Loading the PostGIS SQL routines
   psql -d template1 -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
   psql -d template1 -c "GRANT ALL ON geometry_columns TO PUBLIC;" # Enabling users to alter spatial tables.
   psql -d template1 -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"

Once the template is spatially enabled, create your project database::

   createdb simple_example -U postgres

To setup the database schema and populate with some initial data, run the 
django syncdb command from within the ``example-projects/test_project`` directory::

    python manage.py syncdb

And then use the migrate command which will handle creating the schemas and populating the database
for those applications which are under `migration control <http://south.aeracode.org/docs/about.html>`_::

    python manage.py migrate
    
.. note::
    
    If syncdb fails and you get an error related to importing settings.py 
    failing, you are likely missing a python dependency. Double-check 
    :ref:`the dependencies <dependencies>`, and if none are missing jump into a python shell from
    ``example-projects/test_project``, ``import settings``, and look for any errors.

verify and run the dev server
-----------------------------

Confirm that everything is working as expected by running the tests::
    
    python manage.py test
    
.. note::

    Django creates a test database that is different than the database specified 
    in ``settings_local.py``. Depending on your database setup, PostGIS 
    functions may not be added to this new database and cause errors at this
    step related to the geometry columns. See the guide to using :ref:`django_test_database_and_postgis`.
    
    
If everything looks good, turn on the dev server::
    
    python manage.py runserver
    
Hit http://localhost:8000/admin/ in a browser and use the authentication
credentials specified when syncdb was run.

At http://localhost:8000/ the interface should render with sample data.

Next Steps
**********
Now that you have installed lingcod and tested it out using the pre-built example project, 
You'll want to visit :ref:`Creating a New Project<create_new_project>` to find out how to 
build your own customized MarineMap instance.

