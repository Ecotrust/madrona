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

We will set up an example feature types:

    * Areas of Interest (polygons)
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

Database
----------

Next we'll create a new postgis-enabled database for this project and use django's syncdb command to create the necessary tables. 
Assuming you installed postgis according to the installation instructions, this is as simple as::

    createdb example -U postgres  

Networking
-----------
Before you begin, you'll need to know the hostname or IP Address at which your server will be accessible. This will be refered to throughout this document as ``<HOST_OR_IP_ADDRESS>`` and your should replace with values appropriate for your networking setup.

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
        --domain "<HOST_OR_IP_ADDRESS>:8000" \
        --connection "dbname='example' user='postgres'" \
        --studyregion "SRID=4326;POLYGON ((-125.0 41.8, -125.0 46.4, -116.4 46.4, -116.4 41.8, -125.0 41.8))" \
        --aoi "My Areas of Interest"  \
        --folder "Collection of Features"  \
        --kml "Global Marine|http://ebm.nceas.ucsb.edu/GlobalMarine/kml/marine_model.kml"
    
    cd exampleproject 
    ls

Finally, create a `superuser` account to manage the site::

    cd exampleproject/exampleproject/
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

.. note:: The python convention is to name your model classes using CapsCase. Whatever you do, don't use underscores _ in the feature class name.


Next, open the file containing the forms called ``examples/forms.py`` ::

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

    manage.py runserver 0.0.0.0:8000

And visit your web server at ``http://<HOST_OR_IP_ADDRESS>:8000`` and explore. 

.. image:: screen1.png

.. _tutorial_customizing:

Customizing the Madrona project 
##################################

While the above shows the basic layout of a simple madrona app, we'll now dive in and begin customizing it.

Verbose name 
---------------------
The first obvious step is to change how our feature name appears on screen. We can supply custom text using the ``verbose_name`` option::

    @register
    class MyAreasOfInterest(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'example.forms.MyAreasOfInterestForm'
            verbose_name = 'Areas that interest me'


For other options, see the :ref:`Feature options docs<feature_options>`.

Generating custom reports
-------------------------
The default template for the AOI feature just prints out some basic details. In order to customize it, open ``templates/myareasofinterest/show.html``. There you will see a django html template responsible for creating the attributes page. 

Each feature get's passed to the template as the variable ``instance``. Any attributes, properties and methods that exist on the feature model instances can be accessed via template variables. For example, to get the polygon area, you could use the following template substitution::

    {{instance.geometry_final.area}}

You could also define a custom property on your AOI model...::

    @register
    class MyAreasOfInterest(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'example.forms.MyAreasOfInterestForm'
            verbose_name = 'Areas that interest me'

        @property
        def acres(self):
            area_meters = self.geometry_final.area 
            conversion = 0.000247105381 
            area_acres = area_meters * conversion
            return area_acres

... and use the following in your template::

    <p>Acreage is {{instance.acres}}</p>

The reporting can get as detailed and complex as your needs require and can leverage GeoDjango geometry operations as well as any spatial analysis supported by Python. 

About page
-----------
Open the ``templates/news/about.html`` page. The default landing page is just a placeholder; here you can put any 
html description of your project or high-level documentation that you want the user to see when they first view the site::

    {% load appname %}
    <h1> About {% appname %}</h1>
    <p> This app exists as an example to highlight some of the functionality
    of the Madrona framework. </p>


Customizing KML styling
-------------------------

Every feature class has a default ``kml`` and ``kml_style`` properties which defines the KML representation of that feature. If you want to customize the look and behavior of your map features, you can override the kml property in your feature model. In ``example/models.py``::

    @register
    class MyAreasOfInterest(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'example.forms.MyAreasOfInterestForm'
            verbose_name = 'Areas that interest me'

        @property
        def kml(self):
            return """
            <Placemark id="%s">
                <name>%s</name>
                <styleUrl>#%s-default</styleUrl>
                <ExtendedData>
                    <Data name="name"><value>%s</value></Data>
                    <Data name="dsc"><value>%s</value></Data>
                    <Data name="acres"><value>%s</value></Data>
                </ExtendedData>
                %s 
            </Placemark>
            """ % (self.uid, 
                self.name, 
                self.model_uid(),
                self.name, self.date_modified, self.acres
                self.geom_kml)

        @property
        def kml_style(self):
            return """
            <Style id="%s-default">
                <PolyStyle>
                    <color>ffc00000</color>
                </PolyStyle>
            </Style>
            """ % self.model_uid()

The above will give us KML placemarks with a different popup balloon (showing Name, Description and Acres) 
and change polygon styling to green fill. 

Ultimately, whatever you can do with KML, you can do with your feature's KML representation. 
However, there are some important guidelines to follow;  For more information, see the :ref:`kmlapp documentation <kmlapp>`.

Group Collaboration
---------------------------------

Madrona provides a robust mechanism for sharing features between users. By default, all features you create under a single account are accessible by that user alone. But `users` can be made members of `groups` and can choose to share features with group members who can then view them, copy them, share them back with revisions, etc. This allows for truely collaborative multi-user workflows while maintaining privacy of data. 

The first step is to use Django's admin site to create users and groups.

1. Navigate to  ``http://<HOST_OR_IP_ADDRESS>:8000/admin/auth/`` and click ``+ Add`` next to Groups. Give the group a name, "My Group", and add the "madrona" user to it, and click ``Save``:

.. image:: add_group.png

2. Of course you, the "madrona" user, are the only member of this group at the moment! Go back to  ``http://<HOST_OR_IP_ADDRESS>:8000/admin/auth/`` and click ``+ Add`` next to `Users` and follow the instructions on-screen to create another user and add them to the ``My Group`` group.

3. Finally, at the command line prompt, enable sharing for "My Group" by this command::

    python manage.py enable_sharing --all

Back in the application, you should now be able to share features with other users through the ``Edit`` > ``Share`` menu item and view shapes that others have shared in the ``Shared with Me`` tab.


Handling geometries through manipulators
----------------------------------------

The :ref:`manipulators <manipulators>` app provides ways to validate user-drawn geometries and make sure they conform to rules that you define. 
For example, you may want to limit user-drawn shapes to be within the study region. For this case, there is a built in manipulator called ``ClipToStudyRegion`` which will, as the name suggests, clip a user-drawn shape to the coundary of the study region::

    @register
    class MyAreasOfInterest(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'example.forms.MyAreasOfInterestForm'
        verbose_name = 'Areas that interest me'
        manipulators = [ 'madrona.manipulators.manipulators.ClipToStudyRegion' ]

You can also choose from several other built-in manipulators, define custom manipulators or make them optional. For more information, see the :ref:`manipulators documentation <manipulators>`.


Managing basemaps and KML datasets
------------------------------------
Base data layers are managed using a single KML file called the `public layers list`. If you defined KML layers 
when setting up your initial app, the layers list will be available at 
``http://<HOST_OR_IP_ADDRESS>:8000/layers/public/``. Download that file, save as ``public.kml``, 
and open for editing. You'll see that it is a standard KML file with `NetworkLink`s to the base data layers.  We can modify it by adding another KML NetworkLink ::

    <NetworkLink id="global-marine">
        <name>Global Marine</name>
        <visibility>0</visibility>
        <Link>
        <href>http://ebm.nceas.ucsb.edu/GlobalMarine/kml/marine_model.kml</href>
        </Link>
    </NetworkLink>

Once we've modified the public kml, browse to admin interface at ``http://<HOST_OR_IP_ADDRESS>:8000/admin/layers/publiclayerlist/add/`` and use it to upload the new KML file. After refreshing your browser cache, you should see the new KML avaible in the layers panel.

For more information, see the :ref:`layers documentation <layers>`.

Custom Links: Extending the API
---------------------------------
Many default API actions are defined out-of-box for Madrona Features (Create, Edit, Delete, KML download, etc.). If you want to provide other methods of accessing your features, Madrona provides a link option to extend the API. 

For example, let's say we want to provide a simple text file download for your area of interest. This would involve two steps: 

1. Add a link to your feature Options in ``example/models.py``::

    @register
    class MyAreasOfInterest(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'example.forms.MyAreasOfInterestForm'
            verbose_name = 'Areas that interest me'
            manipulators = [ 'madrona.manipulators.manipulators.ClipToStudyRegion' ]
            links = (
                related('Text file',
                    'examples.views.aoi_text',
                    select='single multiple',
                    type='text/csv'
                ),
            )

2. Create a view to handle the creation of text files for one or more features. Open ``example/views.py`` and add the following function::
   
    def aoi_text(request, instances):
        header = "Name, Description, Acres"
        lines = ["%s, %s, %f" % (f.name, f.description, f.acres) for f in instances]
        text = "%s\n%s" % (header, '\n'.join(lines)
        return HttpResponse(text)

Now restart the application, clear the cache and you should see ``Text File`` as an option in the download menu.

.. note:: There are many :ref:`default links<default_links>` provided by madrona - just think of all the work you'd have to do to a) manually create the views and urls to handle them and b) tweak the javascript and html to handle all of those views. Madrona just does it for you... nice, huh!  

For more information about extending the API through links and views, consult the :ref:`Features documentation <feature_links>` 

Next Steps
##############

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
