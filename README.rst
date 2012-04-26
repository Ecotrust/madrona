Madrona
-------

Overview
========
Madrona is a framework for creating tools for decision support and spatial planning at any geography and scale.  

Madrona provides a set of building blocks and design patterns for software developers 
to quickly create tools to meet unique decision making and spatial planning challenges. 
They can be for individual use or support of a large group in a collaborative planning process.

Madrona is based on the Python programming language and the Django web framework.  It leverages server-side technology such as PostGIS, Mapnik and GDAL and client-side technology including JQuery.  Madrona provides robust support for 3D mapping using KMLtree and the Google Earth API. The architecture is modular and can be integrated with many third party applications, both proprietary and open-source.

Examples
========

* `Oregon MarineMap <http://oregon.marinemap.org/>`_
* `Washingtion Marine Planner <http://washington.marineplanning.org/>`_
* `Bioregional Discovery Tool <http://bioregions.apps.ecotrust.org/>`_         
* `USFWS Aquatic Prioritization Tool <http://aquatic-priorities.apps.ecotrust.org/>`_
* `Forest Management Scenario Planner <https://github.com/Ecotrust/land_owner_tools>`_
* `Mid-Atlantic Regional Council on the Ocean Marine Planner <https://github.com/Ecotrust/marco-portal>`_
* `North Pacific Landscape Conservation Cooperative Prioritization Tool <https://github.com/Ecotrust/nplcc>`_

Quick Start
===========

(Option 1) Install on your system
***********************************

#. Install system requirements::

    * Mapnik 2.0+ 
    * GDAL 1.7+
    * Postgresql 9.1+
    * PostGIS 1.5+
    * GEOS 3.2+
    * Proj
    * Python 2.6+ 
    * Pip
    * CSSTidy
    * Virtualenv
    * Apache2 with mod_wsgi (or other web/application server such as nginx and gunicorn)

   The procedure will differ depending on your operating system; see `docs <http://ecotrust.github.com/madrona/docs/installation.html#system-requirements>`_ for details.

#. Create a virtualenv (optional)::

    virtualenv --system-site-packages test_environment
    cd test_environment
    source bin/activate
    
#. Install the latest madrona release from PyPi::

    pip install madrona

   Alternately, checkout the development code::

    mkdir src; cd src
    git clone https://github.com/Ecotrust/madrona.git
    cd madrona
    python setup.py develop

For more detail, visit the `installation docs <http://ecotrust.github.com/madrona/docs/installation.html>`_

(Option 2) Download a preconfigured system
********************************************

A pre-installed `Virtual Machine <https://github.com/Ecotrust/madrona/wiki/Madrona-Virtual-Machine>`_ is available to 
help you get up and running quickly. 

Create your Project 
=========================

Once you've got madrona installed, you're ready to start developing your new planning tool! 
Depending on your style you may want to:

* Hit the ground running with an `example application <https://github.com/Ecotrust/madrona/tree/master/examples/test_project/>`_.

* Walk through the entire process with our `guided tutorial <http://ecotrust.github.com/madrona/docs/tutorial.html>`_.

Learn more
===========

* Visit the `project documentation <http://ecotrust.github.com/madrona/docs/>`_ for more details.
* Questions? Check out the `mailing list <http://groups.google.com/group/madrona-users>`_ or the ``#madrona`` IRC channel.
* Check us out at `the cheeseshop <http://pypi.python.org/pypi/madrona>`_.
