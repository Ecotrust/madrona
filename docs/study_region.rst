.. _study_region:

The Study Region
================

What is the Study Region?
*************************

The Study Region is a `multipolygon <http://geodjango.org/docs/geos.html#multipolygon>`_
that refers to all areas within which new Marine Protected Areas may be 
proposed. Often this is based on a combination of factors including the 
administrative jurisdiction of the agency implementing the MPAs, biogeography,
and the logistics of running a design process across a wide area. For example,
the `Marine Life Protection Act Initiative <http://www.dfg.ca.gov/mlpa/>`_ 
proceeded with establishing MPAs by breaking up the state of California into 5 
study regions. Each study region was addressed in series, and the study region
was limited to state waters because the process was backed by state
legislation.

The Study Region is the fundamental unit that defines a MarineMap installation.
To support the `California MLPA Initiative <http://www.dfg.ca.gov/mlpa/>`_, 
5 instances of MarineMap would need to be built and run. MarineMap clips all 
Marine Protected Areas to the Study Region boundaries. It also uses the Study 
Region bounds to determine the default extent of the map.

Specifying or Changing the Study Region
***************************************

The ``lingcod.layers`` project includes an ``initial_data`` fixture that will
setup an example Study Region when the database is first setup using the 
syncdb management command. 

Changing the Study Region boundaries on a deployed application presents many 
problems.
  * All Marine Protected Areas affected by the Study Region geometry changes will need to be re-clipped.
  * Any reports associated with those MPAs will need to be regenerated.
  * Some cached data structures such as the network graph used for calculating Array spacing will need to be regenerated.

MarineMap is designed to make this process work as smoothly as possible, but
the steps to change a Study Region must be followed exactly to avoid any 
problems.


Create a New Study Region
-------------------------

To create a new study region a shapefile (or other `LayerMapping <http://geodjango.org/docs/layermapping.html>`_ compatible datasource)
that contains a single multipolygon representing the Study Region bounds is 
needed. One way to create such a file would be to use a tool like `QGis <http://www.qgis.org/>`_
to export the current Study Region in the database to a shapefile and modify
the boundaries as needed.

It is highly recomended that the study region shapefile be created in the same spatial reference system
as the application SRID.  

.. note::

    Do not modify the Study Region in-place in the database. Modifications to
    a Study Region geometry will not be detected by the application this way,
    leaving Marine Protected Areas clipped to the wrong shape in the system.
    Always use the management commands.
    
Once a shapefile is ready and sitting on the server, the next step is to use
the ``create_study_region`` management command.

.. code-block:: bash

    $ python manage.py create_study_region ~/Desktop/study_region2.shp
    
    Study region created: Sample Study Region - Southern California MLPA, primary key = 18
    To switch to this study region, you will need to run 'python manage.py change_study_region 18'
    
If the study region shapefile does not contain a field named 'name', you can specify the name on the command
line using the --name option.

.. code-block:: bash

    $ python manage.py create_study_region --name "new study region" ~/Desktop/study_region2.shp

    Study region created: new study region, primary key = 3
    To switch to this study region, you will need to run 'python manage.py change_study_region 3'

The Study Region should then be accessible via the admin tool.
    
Suspend the Application
-----------------------

Changing the Study Region on a live application is not recommended. Either 
shutdown the server or put MarineMap into :ref:`maintenance_mode`.

Switch to the new Study Region
------------------------------

Currently, the change_study_region command simply sets specified region as the current active study region. It does *not* do any re-clipping, re-configuration, etc. If run on a working installation, this will require a lot more manual work. However, it is sufficient to initally set up the study region for a brand new project.  

.. code-block:: bash
    
    $ python manage.py change_study_region.py 18

Switch to the new Study Region (Future Plans)
----------------------------------------------

.. note::

    The following steps are not implemented, but this documentation can serve 
    as a specification for the future tools.


The ``change_study_region`` command will walk one through the process of 
changing from one study region to another. The primary key of an existing 
study region is the only argument needed to start.

.. code-block:: bash
    
    $ python manage.py change_study_region.py 18
    
    This process should not be done when the MarineMap application is publicly 
    accessible. Please shutdown the server or redirect users to a maintenance page

    Type 'yes' to continue, or 'no' to cancel: yes

    calculating difference between the specified study region and the one currently active...

                current study region: Sample Study Region - Southern California MLPA
                    area: 6088792658.45

                new study region: Sample Study Region - Southern California MLPA
                    area: 6087778804.81
    
                difference between study regions:
                    area: 1013853.63735
                    sections: 1

                User Shapes Affected:
                Mpas: 12

    Are you sure you would like the switch to the new study region?
    Type 'yes' to continue, or 'no' to cancel: yes

Changing to a new study region means re-clipping and processing Marine 
Protected Area geometries, and will take a significant amount of time.

.. code-block:: bash

    Processing shapes:
    |---------------------------------------          |  84% | ETA:  00:00:12

When the process is over there is the option to send a summary email to users
who have had shapes modified by the process.

.. code-block:: bash

    Done processing shapes.
    Would you like to send an email notifying users that their shapes have changed?
    Type 'yes' or 'no': yes
    sending emails...
    This process is complete. You can now resume public access to the application.    

Resume the Application
----------------------

Restart the server or take the application out of :ref:`maintenance_mode`.

Cross-Study Region Support
**************************

There are use cases where it makes sense to have integration across multiple
study regions. For example, in California it makes sense for work in the 
southern study region to be informed by work in the central one. It would be
desirable to report on the Marine Protected Areas in multiple study regions as
a network. Such integration cannot happen within a single app, and will need
to be supported by webservices. The actual implementation details of these 
services have yet to be worked out.
