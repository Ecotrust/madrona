.. _installation:

Installation
============

This documentation is aimed at developers/programmers who want to
implement a Madrona-based project of their own. You should be familiar with

    * programming in Python
    * the command line interface 
    * how web application are structured in `Django <http://djangoproject.com>`_

There are four primary steps to creating a Madrona-based project:
    #. Install :ref:`system requirements<system_requirements>`
    #. Install :ref:`python dependencies<python_dependencies>`
    #. Create a :ref:`sample project<sample_project>`
    #. :ref:`Setup and deploy<deploy>`

.. _system_requirements:

System Requirements
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
    * Virtualenv
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

    While you can install the python dependencies globally, we highly recommend :ref:`creating a 
    virtual environment<virtualenv>` and running these commands from within the activated virtualenv.
    This will allow you to isolate the python dependencies from other projects on the same
    server. 

Start by navigating to an appropriate base directory and creating a virtual python environment. You can skip this step if installing the python libraries globally:: 

    virtualenv madrona-env
    cd madrona-env
    source bin/activate

There are two options to get madrona and it's supporting python libraries:

1. Use PyPi package; the latest version of madrona and all of it's dependencies will be installed (note: compiling can make this a time-consuming step so grab a cup of coffee or take fido for a walk)::

    pip install madrona

2. Use the development master branch. Choose this option if you're thinking about working on the core madrona source code::

    cd src
    git clone http://github.com/Ecotrust/madrona.git
    pip install -r madrona/requirements.txt
    cd madrona
    python setup.py develop

To install madrona itself, use the setup.py script provided. We recommend using the 'develop' command instead of 'install' as this
allows you to alter the madrona code in place without reinstalling.::

    cd src/madrona
    python setup.py develop

Finally, confirm that we can import the madrona module. This example simply prints out the release number::

    python -c "from madrona.common import default_settings; print default_settings.RELEASE"
    
.. _sample_project:

Create a Sample Project
************************

You can download a sample application built using the Madrona components. 
This basic project template is useful as documentation as well as for 
practical tests. 

We'll be starting up ``examples/test_project`` here. Download, extract ... TODO

.. _deploy:

Setup and Deployment
*********************

Using settings.py and settings_local.py
---------------------------------------

Take a look at ``test_project/settings_local.template`` and 
``settings.py``. Madrona uses a simple splitsetting scheme as described 
`here <http://code.djangoproject.com/wiki/SplitSettings#Multiplesettingfilesimportingfromeachother>`_. What this enables is the ability to specify standard settings in settings.py and commit them to a public repository. 
You then create a settings_local.py file which contains your passwords and settings specific to your local machine.

.. important::

    It is very important for security that ``SECRET_KEY``, ``DATABASES``, passwords 
    and other sensistive local settings are kept private and never published.

Lets do that now. Copy settings_local.template to settings_local.py, then
replace the SECRET_KEY with your own randomly-generated key::

    SECRET_KEY = 'SOME_RANDOMLY_GENERATED_GOBBLYGOOK_VERY_SECRET'

Add the following lines, altering as needed to allow connection to your local postgres database::

    DATABASES = {
       'default': {
           'ENGINE': 'django.contrib.gis.db.backends.postgis',
           'NAME': 'example',
           'USER': 'postgres',
           'HOST': 'localhost',
       }
    }
    
Handling static media
----------------------
Because a Madrona instance is split between madrona (the core functionality) and the project-specific code, static media files such as html, javascript, css, images, etc. may exist in both. 
Django expects all the static media to be in a single directory. 
In order to merge the madrona media with the project media, 
you need to create an empty `mediaroot` directory and set it as your MEDIA_ROOT in the project settings_local.py ::

    mkdir /path/to/test_media

Now add the following to you ``settings_local.py``::

    MEDIA_ROOT = '/path/to/test_media'

Then use the 'install_media' management command to merge all the media files into the MEDIA_ROOT directory.:: 

    python manage.py install_media


Database setup
------------------

It is very important that the postgres databases
be created from a template with all the PostGIS and spatial functions installed. Our approach
is to set up postgis in the default postgres database called template1::

   #run as postgres superuser
   sudo su postgres
   POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/postgis-1.5
   createlang -d template1 plpgsql # Adding PLPGSQL language support.
   psql -d template1 -f $POSTGIS_SQL_PATH/postgis.sql # Loading the PostGIS SQL routines
   psql -d template1 -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
   psql -d template1 -f /usr/local/src/madrona/madrona/common/cleangeometry.sql
   psql -d template1 -c "GRANT ALL ON geometry_columns TO PUBLIC;" # Enabling users to alter spatial tables.
   psql -d template1 -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
   exit # back to regular user

Once the template is spatially enabled, create your project database from this template::

   createdb example -U postgres

To setup the database schema and populate with some initial data, run the 
django syncdb command from within the ``test_project`` directory::

    python manage.py syncdb

Use the migrate command to handle creating the schemas and populating the database
for those applications which are under `migration control <http://south.aeracode.org/docs/about.html>`_::

    python manage.py migrate
    
Enable sharing globally for the site::

    python manage.py enable_sharing

Set up the site to run under a particular domain, in this case just on localhost port 8000::

    python manage.py site localhost:8000

Test and run the development server
------------------------------------

Confirm that everything is working as expected by running the tests::
    
    python utils/run_tests.py
    
If everything looks good, turn on the dev server::
    
    python manage.py runserver
    
Go to ``http://localhost:8000/admin/`` in a browser and use the authentication
credentials specified when syncdb was run.  
At ``http://localhost:8000/`` the interface should render with sample data.

Next Steps
**********
Now that you have installed madrona and tested it out using the pre-built example project, 
You'll want to visit the :ref:`Tutorial <tutorial>` to find out how to 
build your own customized Madrona instance.
