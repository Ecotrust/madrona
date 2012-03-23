.. _installation:

Installation
============

This documentation is aimed at developers/programmers who want to
implement a Madrona-based project of their own. You should be familiar with

    * programming in Python
    * the command line interface 
    * how web application are structured in `Django <http://djangoproject.com>`_

There are four primary steps to creating a Madrona-based project:
    #. Install :ref:`global dependencies<global_dependencies>`
    #. Install :ref:`python dependencies<python_dependencies>`
    #. Create a :ref:`sample project<sample_project>`
    #. :ref:`Setup and deploy<deploy>`

.. _global_dependencies:

Global Dependencies
********************
You need the following software installed on your system in order to start running Madrona.

    * `Mapnik <http://mapnik.org/>`_ version 2.0+ 
    * GDAL
    * Postgresql 
    * PostGIS 
    * GEOS
    * Proj
    * Python 2.6+ 
    * Pip
    * Git, Mercurial and Subversion
    * Apache with mod_wsgi (or other suitable web server and application server)

If you've already got these installed, proceed to the *python dependencies* section.

If not, please follow the guide for your platform:

.. toctree::
   :maxdepth: 2
   
   windows_deps 
   mac_deps 
   linux_deps 

.. _python_dependencies:

Python Dependencies
*******************

.. note::

    While you can install the python dependencies globally, we highly recomment :ref:`creating a 
    virtual environment<virtualenv>` and running these commands from within the activated virtualenv.
    (i.e. Use ``/path/to/env/`` instead of ``/usr/local``).
    This will allow you to isolate the python dependencies for multiple projects on the same
    server. 

First you will need to checkout a copy of the default branch of madrona from the `project page <http://github.com/Ecotrust/madrona>`_ ::

     cd /usr/local/src
     git clone http://github.com/Ecotrust/madrona.git

Most of the madrona python dependencies are well-behaved python packages; They can be installed using standard python package management tools such as `pip <http://pip.openplans.org/>`_. 
We have created the `pip requirements file <https://raw.github.com/Ecotrust/madrona/master/madrona_requirements.txt>`_ to automate the installation of most of the dependencies::

    cd /usr/local # Assuming you want to put stuff in /usr/local/src
    pip install -r src/madrona/madrona_requirements.txt

To install madrona itself, use the setup.py script provided. We recommend using the 'develop' command instead of 'install' as this
allows you to alter the madrona code in place without reinstalling.::

    cd src/madrona
    python setup.py develop

Finally, confirm that we can import the madrona module. This example simply prints out the release number::

    python -c "from madrona.common import default_settings; print default_settings.RELEASE"
    
.. _sample_project:

Create a Sample Project
************************

Inside the ``examples`` directory there are sample applications built
using the Madrona components. These serve as useful documentation as well as
practical tests. We'll be starting up ``example-projects/test_project`` here.

.. _deploy:

Setup and Deployment
*********************

using settings.py and settings_local.py
---------------------------------------

Take a look at ``example-projects/test_project/settings_local.template`` and 
``settings.py``. Madrona uses a simple splitsetting scheme as described 
`here <http://code.djangoproject.com/wiki/SplitSettings#Multiplesettingfilesimportingfromeachother>`_. What this enables is the ability to specify standard 
settings in settings.py and commit them to a public repository, but these
don't correspond to any particular machine. You then create a 
settings_local.py file on the machine for deployment or development from the
template which contains your passwords and settings specific to your local machine.

Lets do that now. Copy settings_local.template to settings_local.py, then
uncomment the following line::

    # SECRET_KEY = '6c(kr8r%aqf#r8%arr=0py_7t9m)wgocwyp5g@!j7eb0erm(2+sdklj23'

Alter ``SECRET_KEY`` to make it unique. Next uncomment and alter the following
lines as needed to allow this application to connect to your local database::

    #DATABASES = {
    #    'default': {
    #        'ENGINE': 'django.contrib.gis.db.backends.postgis',
    #        'NAME': 'example',
    #        'USER': 'postgres',
    #    }
    #}
    
handling media
--------------
Because a Madrona instance is split between madrona (core functionality) and the project-specific code, static media files such as html, javascript, css, images, etc. may exist in both. Django, however, expects all the static media to be in a single directory. In order to merge the madrona media with the project media, you need to create a third (empty) media directory and set it as your MEDIA_ROOT in the project settings_local.py ::

    mkdir /tmp/test_media
    cd ~/src/madrona/example_projects/test_project/
    echo "MEDIA_ROOT='/tmp/test_media'" >> settings_local.py

Then use the 'install_media' management command to merge all the media files into the MEDIA_ROOT directory.:: 

    python manage.py install_media


setup the database
------------------


like `pgAdmin <http://www.pgadmin.org/>`_. It is very important that this
database be created from a template with all the PostGIS functions installed. One approach
is to set up postgis in the default postgres database called template1::

   #run as postgres superuser
   sudo su postgres
   POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/postgis-1.5
   createlang -d template1 plpgsql # Adding PLPGSQL language support.
   psql -d template1 -f $POSTGIS_SQL_PATH/postgis.sql # Loading the PostGIS SQL routines
   psql -d template1 -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
   psql -d template1 -c "GRANT ALL ON geometry_columns TO PUBLIC;" # Enabling users to alter spatial tables.
   psql -d template1 -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
   exit # back to regular user

Next we'll need to install a postgresql stored procedure for geometry handling::

    psql -d template1 -U postgres -f /usr/local/src/madrona/madrona/common/cleangeometry.sql

Once the template is spatially enabled, create your project database::

   createdb example -U postgres

Install the cleangeometry stored procedure in the database::

    python manage.py install_cleangeometry 

To setup the database schema and populate with some initial data, run the 
django syncdb command from within the ``example-projects/test_project`` directory::

    python manage.py syncdb

Use the migrate command to handle creating the schemas and populating the database
for those applications which are under `migration control <http://south.aeracode.org/docs/about.html>`_::

    python manage.py migrate
    
Enable sharing globally for the site::

    python manage.py enable_sharing

Set up the site to run under a particular domain, in this case just on localhost port 8000::

    python manage.py site localhost:8000

verify and run the dev server
-----------------------------

Confirm that everything is working as expected by running the tests::
    
    python /usr/local/src/madrona/utils/run_tests.py
    
.. note::

    Django creates a test database that is different than the database specified 
    in ``settings_local.py``. Depending on your database setup, PostGIS 
    functions may not be added to this new database and cause errors at this
    step related to the geometry columns. See the guide to using :ref:`django_test_database_and_postgis`.
    
If everything looks good, turn on the dev server::
    
    python manage.py runserver
    
Go to http://localhost:8000/admin/ in a browser and use the authentication
credentials specified when syncdb was run.

At http://localhost:8000/ the interface should render with sample data.

Next Steps
**********
Now that you have installed madrona and tested it out using the pre-built example project, 
You'll want to visit the :ref:`Tutorial <tutorial>` to find out how to 
build your own customized Madrona instance.
