.. _create_new_project:

Creating your first Madrona project
=============================================

These instructions will walk you through developing a basic implementation of
Madrona. This includes installing from the development repository, setting
up a sample app, testing that everything installed smoothly, then doing some
basic customization. By the end you'll have an application that will perform
all the `basic functions <http://code.google.com/p/madrona/wiki/FeaturesAndRequirements>`_ 
needed to start drawing MPAs on a map.

Overview: example Madrona project 
##################################
In this example, we'll set up a new Madrona instance for the state of Oregon. 

We will set up four example feature types:

    * Areas of Interest (polygons)
    * Lines of Interst
    * Points of Interest
    * Collections of features (folders) 

as well as show you how to tweak certain aspects of the application such as:

    * Generating custom reports
    * Customizing styling
    * Handling geometries through manipulators
    * Managing basemaps and KML datasets


Install Dependencies
---------------------

You will need to install madrona's dependencies and madrona itself. For detailed instructions, please follow the :ref:`Installation <installation>` guide.

.. note:: If you are using the Madrona Virtual Machine, all of the necessary software is pre-installed. 

Databases
----------

Next we'll create a new postgis-enabled database for this project and use django's syncdb command to create the necessary tables. Assuming you installed postgis functions, etc into your postgres template1, this is as simple as::

    createdb example -U postgres  


Create new madrona project
--------------------------
In order to jumpstart the coding process, Madrona provides a script, ``create-madrona-project.py``, which auto-generates the boring parts of the codebase for you. First we'll need to decide on some basic parameters of our project.

Our study region will be defined (roughly) by the following polygon in WKT format::

    SRID=4326;POLYGON ((-125.0 41.8, -125.0 46.4, -116.4 46.4, -116.4 41.8, -125.0 41.8))

Choose a directory to store your project and run the ``create-madrona-project.py`` script::

    cd /usr/local/userapps 
    create-madrona-project.py \
        --project "Example Project" \
        --app example \
        --domain "localhost:8000" \
        --connection "dbname='example' user='postgres'" \
        --studyregion "SRID=4326;POLYGON ((-125.0 41.8, -125.0 46.4, -116.4 46.4, -116.4 41.8, -125.0 41.8))" \
        --aoi "My Areas of Interest"  \
        --poi "My Points of Iterest"  \
        --loi "My Lines of Interest"  \
        --folder "Collection of Features"  \
        --kml "Global Marine|http://ebm.nceas.ucsb.edu/GlobalMarine/kml/marine_model.kml"
    
    cd exampleproject 
    ls

You should see the following directory structure::

    oregon
    |-- __init__.py
    |-- manage.py
    |-- settings.py
    `-- urls.py


Editing Features and FeatureCollections
----------------------------------------


We can ignore the tests and views for now; for now we'll focus on creating the Mpa and Folder models. Open ``omm/models.py`` and add::

    from madrona.features.models import PolygonFeature, FeatureCollection
    from madrona.features import register

    @register
    class Mpa(PolygonFeature):
        class Options:
            form = 'oregon.omm.forms.MpaForm'

.. note::

   The python convention is to name your model classes using CapsCase. Just don't use underscores _ in the feature class name.

Next create a file to hold the forms called ``forms.py`` ::

    from madrona.features.forms import FeatureForm, SpatialFeatureForm
    from omm.models import Mpa, Folder

    class MpaForm(SpatialFeatureForm):
        class Meta(SpatialFeatureForm.Meta):
            model = Mpa

The above is a barebones MPA feature inherited from the ``PolygonFeature`` base class. All the basic attributes are included by default. A form for creating and editing Mpas is also provided; again inheriting from a ``SpatialFeatureForm`` base class so the default behavior takes only a few lines of code. The only additional information required is the Options class with a form property specifying the full python path to the associated Form (mandatory). Finally the @register decorator at the top of the class is required to register the Mpa feature class with madrona. 

Similarly, we could group Mpas into collections; let's call them "Folders" for now. We can inherit from the base ``FeatureCollection`` and specify the mandatory ``valid_children`` Option to configure which feature types can be placed in a folder.

So, adding to ``models.py`` ::

    @register
    class Folder(FeatureCollection):
        class Options:
            form = 'oregon.omm.forms.FolderForm'
            valid_children = (
                'oregon.omm.models.Mpa', 
                'oregon.omm.models.Folder', 
            )

and adding to ``forms.py`` ::
 
    class FolderForm(FeatureForm):
        class Meta(FeatureForm.Meta):
            model = Folder

This is all that is necessary to begin managing MPA features and organizing them into Folders. With a few lines of code, we've defined the features and aspects of our application's behavior. One of our goals is to make the customization and configuration of madrona as easy as possible - and its almost entirely driven by the model configurations you see above. There are few other things you need to do in order to get a fully functional application. 


Trying it out
--------------
Runserver::

    manage.py runserver

While the above shows a minimal bare-bones project, it's not a very interesting example.

Verbose name and icon
---------------------

Generating custom reports
-------------------------

About page
-----------

Customizing styling
--------------------

Handling geometries through manipulators
----------------------------------------

Managing basemaps and KML datasets
------------------------------------

Custom Views
--------------
custom links to the Options::

    @register
    class Mpa(PolygonFeature):
        designation = models.CharField()
        class Options:
            verbose_name = 'Marine Protected Area'
            form = 'oregon.omm.models.MpaForm'
            manipulators = [ 'madrona.manipulators.manipulators.ClipToStudyRegion' ]
            optional_manipulators = [ 'madrona.manipulators.manipulators.ClipToGraticuleManipulator' ]
            links = (
                related('Habitat Spreadsheet',
                    'oregon.omm.views.habitat_spreadsheet',
                    select='single',
                    type='application/xls'
                ),
            )

.. note::
    
    The above `Mpa` feature has a custom link for a Habitat Spreadsheet; the oregon.omm.views.habitat_spreadsheet view would need to be written for this to function properly. For more info see documentation on Creating Link Views TODO.

See the documentation in the following sections to customize Madrona as 
needed:

.. toctree::
   :maxdepth: 1
   
   features
   studyregion
   deployment
   layers
   managing_users
   migration
   manipulators
   staticmap
   sharing_configuration
   kml_configuration
   template_customization
   
The setup this guide has walked through only specifies how to run the django
development server. To setup a public facing website using Apache, consult the
:ref:`deployment` notes.
