.. _installation:

Installation
============

This documentation is aimed at developers/programmers who want to
implement a Madrona-based project of their own. You should be familiar with

    * programming in Python
    * the command line interface 
    * how web applications are structured in `Django <http://djangoproject.com>`_

There are four primary steps to creating a Madrona-based project:
    #. Install :ref:`system requirements<system_requirements>`
    #. Install :ref:`python dependencies<python_dependencies>`
    #. Setup Postgres :ref:`database<database>`
    #. Create and deploy your project

.. _system_requirements:

System Requirements
********************
You need the following software installed on your system in order to start running Madrona.

    * Mapnik 2.0+ 
    * GDAL 1.7+
    * Postgresql 9.1+
    * PostGIS 1.5+
    * GEOS 3.2+
    * Proj
    * Python 2.6+ 
    * Pip
    * CSSTidy
    * Virtualenv and virtualenvwrapper
    * Apache2 with mod_wsgi (or other suitable web server and application server)

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

    While you can install the python dependencies globally, we highly recommend creating a 
    *virtual environment*. Running these commands from within a `virtualenv`
    will allow you to isolate the python dependencies from other projects on the same
    server. :ref:`Read more<virtualenv>`.

Start by navigating to an appropriate base directory and creating a virtual python environment. You can skip this step if installing the python libraries globally:: 

    virtualenv --system-site-packages madrona-env
    cd madrona-env
    source bin/activate

There are two options to get madrona and it's supporting python libraries:

1. Use PyPi package; the latest version of madrona and all of it's dependencies will be installed (note: compiling can make this a time-consuming step so grab a cup of coffee or take fido for a walk)::

    pip install madrona

2. Use the development master branch. Choose this option if you're thinking about working on the core madrona source code::

    cd src
    git clone https://github.com/Ecotrust/madrona.git
    cd madrona
    python setup.py develop

Finally, confirm that we can import the madrona module.::

    python -c "import madrona; print madrona.get_version()"
    
.. _database_setup:

Database setup
****************

It is very important that the postgres databases
be created from a template with all the PostGIS and spatial functions installed. Our approach
is to set up postgis in the default postgres database called template1::

   #run as postgres superuser
   sudo su postgres
   POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/postgis-1.5
   createlang -d template1 plpgsql # Adding PLPGSQL language support.
   psql -d template1 -f $POSTGIS_SQL_PATH/postgis.sql # Loading the PostGIS SQL routines
   psql -d template1 -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
   psql -d template1 -f /usr/local/src/madrona/madrona/common/sql/cleangeometry.sql
   psql -d template1 -c "GRANT ALL ON geometry_columns TO PUBLIC;" # Enabling users to alter spatial tables.
   psql -d template1 -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
   exit # back to regular user

Once the template is spatially enabled, create your project database from this template::

   createdb example -U postgres -T template1


Next Steps
**********
    #. Create a :ref:`sample project<tutorial>`
    #. :ref:`Setup and deploy<deploy>`
