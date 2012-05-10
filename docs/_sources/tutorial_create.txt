.. _create_new_project:

Creating your first Madrona project
=============================================

These instructions will walk you through developing a basic implementation of
Madrona. This includes installing the dependencies, setting
up a sample app, testing that everything installed smoothly, then doing some
simple customization. By the end you'll have a basic Madrona application and a
sense how to customize it for your needs.

Overview: example Madrona project 
##################################
In this example, we'll set up a new Madrona instance for the state of Oregon. 

We will set up the following example feature types:

    * Areas of Interest (polygons)
    * Collections of features (folders) 

as well as show you how to tweak certain aspects of the application such as:

    * Custom reports
    * Visual styling
    * Validation and manipulation of user-drawn geometries
    * Basemaps and KML datasets


Install Dependencies
---------------------

You will need to install madrona's dependencies and madrona itself. For detailed instructions, please follow the :ref:`Installation <installation>` guide.

.. note:: If you are using the Madrona Virtual Machine, all of the necessary software is pre-installed. 

Database
----------

Next we'll create a new postgis-enabled database for this project and use django's syncdb command to create the necessary tables. 
Assuming you installed postgis according to the installation instructions, this is as simple as::

    sudo su postgres
    createdb example -U postgres   # you may want to use a different database user depending on your postgres configuration
    exit

Networking
-----------
Before you begin, you'll need to know the hostname or IP Address and port at which your server will be accessible.

.. important:: In the examples below, you must replace ``<HOST_OR_IP_ADDRESS>`` and ``<PORT>`` with values appropriate for your networking setup.

Create new madrona project
--------------------------
In order to jumpstart the coding process, Madrona provides a script, ``create-madrona-project.py``, which auto-generates the boring parts of the codebase for you. First we'll need to decide on some basic parameters of our project.

Our study region will be defined (roughly) by the following polygon in WKT format::

    SRID=4326;POLYGON ((-125.0 41.8, -125.0 46.4, -116.4 46.4, -116.4 41.8, -125.0 41.8))

Choose a directory to store your project and run the ``create-madrona-project.py`` script::

    cd /usr/local/userapps 
    create-madrona-project.py \
        --project "Example" \
        --app example \
        --domain "<HOST_OR_IP_ADDRESS>:<PORT>" \
        --connection "dbname='example' user='postgres'" \
        --studyregion "SRID=4326;POLYGON ((-125.0 41.8, -125.0 46.4, -116.4 46.4, -116.4 41.8, -125.0 41.8))" \
        --aoi "My Areas of Interest"  \
        --folder "Collection of Features"  \
        --kml "Global Marine|http://ebm.nceas.ucsb.edu/GlobalMarine/kml/marine_model.kml"

Now enter the project directory where the new code lives::

    cd exampleproject/exampleproject/

Finally, create a `superuser` account to manage the site::

    python manage.py createsuperuser --username=madrona --email=madrona@ecotrust.org
    # You'll be prompted to enter a password twice


Examining Features 
----------------------------------------

First, we want to examine the ``Features`` models. Open ``example/models.py`` and find the definition for the AOI Feature::

    @register
    class MyAreasOfInterest(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'example.forms.MyAreasOfInterestForm'

This defines the `MyAreasOfInterest` polygon feature, adds a `description` attribute and defines the `form` used to edit it. 

.. warning:: The python convention is to name your model classes using CapsCase. Whatever you do, don't use underscores _ in the feature class name.

Next, open the file containing the forms called ``example/forms.py`` ::

    from models import MyAreasOfInterest
    class MyAreasOfInterestForm(SpatialFeatureForm):
        class Meta(SpatialFeatureForm.Meta):
            model = MyAreasOfInterest

Here we define the form or editing interface for our feature. Notice that the classes are inherited from the ``SpatialFeatureForm class``. Right now, we are just accepting the defaults and linking it to our `MyAreasOfInterest` model.

FeatureCollections
----------------------------------------

Similarly, we could group features into collections. We can inherit from the base ``FeatureCollection`` and specify the mandatory ``valid_children`` Option to configure which feature types can be placed in a folder.

Again, from ``examples/models.py``::

    @register
    class CollectionOfFeatures(FeatureCollection):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'example.forms.CollectionOfFeaturesForm'
            valid_children = (
                ('example.models.MyAreasOfInterest'),  
                ('example.models.CollectionOfFeatures')
            )

Here, we've specified that ``CollectionOfFeatures`` can contain our AOI feature type as well as other collections (nested).  
This is all that is necessary to begin managing features and organizing them into Collections. With a few lines of code, we've defined the features and aspects of our application's behavior. One of our goals is to make the customization and configuration of madrona as easy as possible - and its almost entirely driven by the model configurations you see above. There are few other things you need to do in order to get a fully functional application. 


Trying it out
--------------
Now that we've examined the models and forms, we can run the development server to confirm everything is running::

    manage.py runserver 0.0.0.0:<PORT>

And visit your web server at ``http://<HOST_OR_IP_ADDRESS>:<PORT>`` and explore. 

.. image:: screen1.png

.. include:: tutorial_customize.rst
