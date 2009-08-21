.. _getting_started:

Getting Started
===============
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

    * A working installation of `GeoDjango <http://geodjango.org>`_
    * `django-compress <http://code.google.com/p/django-compress/>`_ (requires CSSTidy, look @ the 1.2 release for binaries)
    * `elementtree <http://effbot.org/zone/element-index.htm>`_
    * `django-maintenancemode <http://pypi.python.org/pypi/django-maintenancemode>`_
    
.. note::
    MarineMap development tends to follow django trunk. It may work on the 
    point releases but it's safer to just start from source.

In addition, you should be familiar with programming in Python, how web 
application are structured in `Django <http://djangoproject.com>`_, and using 
a `Subversion <http://subversion.tigris.org/>`_ client.

Installation
************
First you will need to checkout a copy of trunk from the `project page <http://code.google.com/p/marinemap/source/checkout>`_. 
Next you'll need to add some MarineMap modules to your site-packages 
directory. This way all the appropriate modules will automatically be in your
python path. Rather than physically moving them there, you can instead create 
a symlink. On Linux or OS X, you can use the following command to find your
site-packages directory::

    python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"
    
Once you have that directory, create the symlink::
    
    ln -s `pwd`/marinemap-trunk/lingcod SITE-PACKAGES-DIR/lingcod

Test that you can now import modules without throwing an exception. Go into a
shell such as ipython and type the following::

    from lingcod import layers
    
Using the Sample App
********************

Inside the example-projects/ directory there are sample applications built
using the MarineMap components. These serve as useful documentation as well as
practical tests. We'll be starting up ``example-projects/simple`` here.

using settings.py and settings_local.py
---------------------------------------

Take a look at ``example-projects/simple/settings_local.template`` and 
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
    
Grab a `Google Maps API key <http://code.google.com/apis/maps/signup.html>`_ and put it into the proper setting (not needed for localhost)::

    GOOGLE_API_KEY = 'ABQIAAAAbEBR9v0lqBFdTfOcbe5WjRSwtTT5GAxiJqzQ69gC1VuJs9XrFRSHtkp9BFyAR6_lVVfY3MBP3uA7Mg'

setup the database
------------------

Create a database accessible by the connection settings above using a tool
like `pgAdmin <http://www.pgadmin.org/>`_. It is very important that this
database be created from a template with all the PostGIS functions installed.
After doing so, to setup the database schema all you'll need to do is run the 
django syncdb command from within the ``example-projects/simple`` directory::

    python manage.py syncdb
    
.. note::
    
    If syncdb fails and you get an error related to importing settings.py 
    failing, you are likely missing a python dependency. Double-check 
    :ref:`the dependencies <dependencies>`, and if none are missing jump into a python shell from
    ``example-projects/simple``, ``import settings``, and look for any errors.

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

Both the :ref:`Study Region <study_region>` and :ref:`Data Layers <layers>` apps are 
configured to load sample data when ``syncdb`` is run. This is great to get 
started but you'll want to read the documentation for each of these apps to
learn how to specify your actual study region and public data layers.


useful documentation
--------------------

.. toctree::
   :maxdepth: 1
   
   study_region
   layers
   managing_users