Customizing the Madrona project 
##################################

The following sections will expose you to the django admin, django templates and models, and basic KML.

Group Collaboration
---------------------------------

Madrona provides a robust mechanism for sharing features between users. By default, all features you create under a single account are accessible by that user alone. But `users` can be made members of `groups` and can choose to share features with group members who can then view them, copy them, share them back with revisions, etc. This allows for truely collaborative multi-user workflows while maintaining privacy of data. 

The first step is to use Django's admin site to create users and groups.

1. Navigate to  ``http://madrona:81/admin/auth/`` and click ``+ Add`` next to Groups. Give the group a name, "My Group", and add the "madrona" user to it, and click ``Save``:

.. image:: add_group.png

2. Of course you, the "madrona" user, are the only member of this group at the moment! Go back to  ``http://madrona:81/admin/auth/`` and click ``+ Add`` next to `Users` and follow the instructions on-screen to create another user and add them to the ``My Group`` group.

3. Finally, at the command line prompt (in the LXTerminal), enable sharing for "My Group" by this command::

    python manage.py enable_sharing --all

Back in the application, you should now be able to share features with other users through the ``Edit`` > ``Share`` menu item and view shapes that others have shared in the ``Shared with Me`` tab.

.. note::  TODO: Improve this section (more details, re-order?, etc)

About page
-----------
Open the ``/usr/local/userapps/testappDemoProject/testappdemoproject/templates/news/about.html`` page. The default landing page is just a placeholder; here you can put any 
html description of your project or high-level documentation that you want the user to see when they first view the site::

    {% load appname %}
    <h1> About {% appname %}</h1>
    <p> This app exists as an example to highlight some of the functionality
    of the Madrona framework. </p>


Verbose name 
---------------------
The first obvious step is to change how our feature name appears on screen. We can supply custom text using ``verbose_name`` in the feature's Options class::

    @register
    class AOI(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'testapp.forms.AOI'
            verbose_name = 'Areas of Interest'


For other options, see the :ref:`Feature options docs<feature_options>`.

.. note::  TODO:  At some point we should talk about using ``runserver 0.0.0.0:8000`` (and viewing from ``madrona:8000``) to prevent the need to touch the ``wsgi`` file or similar strategies.

Generating custom reports
-------------------------
The default template for the AOI feature just prints out some basic details. In order to customize it, open ``/usr/local/userapps/testappDemoProject/testappdemoproject/templates/aoi/show.html``. There you will see a django html template responsible for creating the attributes page. 

Each feature gets passed to the template as the variable ``instance``. Any attributes, properties and methods that exist on the feature model instance can be accessed through this template variable. 
For example, the polygon area is currently being reported through the following template variable::

    {{instance.geometry_final.area}}

You could also define a custom property on your ``AOI`` model (``/usr/local/userapps/testappDemoProject/testappdemoproject/testapp/models.py``) that returns the acreage...::

    @register
    class AOI(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'testapp.forms.AOI'
            verbose_name = 'Areas of Interest'

        @property
        def acres(self):
            area_meters = self.geometry_final.area 
            conversion = 0.000247105381 
            area_acres = area_meters * conversion
            return area_acres

... and add the following to your feature's show template (``/usr/local/userapps/testappDemoProject/testappdemoproject/templates/aoi/show.html``)::

    <p>Acreage is {{instance.acres}}</p>

Now when you view the attributes panel for your AOI, you will see that the acreage is reported.  
    
The reporting can get as detailed and complex as your needs require and can leverage GeoDjango geometry operations as well as any spatial analysis supported by Python. 

Customizing KML styling
-------------------------

Every feature class has a default ``kml`` and ``kml_style`` properties which defines the KML representation of that feature. If you want to customize the look and behavior of your map features, you can override the kml property in your feature model. In ``testapp/models.py``::

    @register
    class AOI(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'testapp.forms.AOI'
            verbose_name = 'Areas of Interest'

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
                self.name, self.date_modified, self.acres,
                self.geom_kml)

        @property
        def kml_style(self):
            return """
            <Style id="%s-default">
                <PolyStyle>
                    <color>ffc00000</color>
                </PolyStyle>
                <BalloonStyle>
                    <bgColor>ffeeeeee</bgColor>
                    <text> <![CDATA[
                        <font color="#1A3752"><strong>$[name]</strong></font>
                        <p>Area: $[acres] acres</p>
                        <p>$[desc]</p>
                    ]]> 
                    </text>
                </BalloonStyle>
            </Style>
            """ % self.model_uid()

The above will change the color and transparency of the polygon and modify the contents of the KML placemark balloon (showing Name, Description and Acres). 

Ultimately, whatever you can do with `KML <https://developers.google.com/kml/documentation/kmlreference>`_ , you can do with your feature's KML representation. 
However, there are some important guidelines to follow;  For more information, see the :ref:`kmlapp documentation <kmlapp>`.


Handling geometries through manipulators
----------------------------------------

The :ref:`manipulators <manipulators>` app provides ways to validate user-drawn geometries and make sure they conform to rules that you define. 
For example, you may want to limit user-drawn shapes to be within the study region. For this case, there is a built in manipulator called ``ClipToStudyRegion`` which will, as the name suggests, clip a user-drawn shape to the coundary of the study region::

    @register
    class AOI(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'testapp.forms.AOI'
        verbose_name = 'Areas of Interest'
        manipulators = [ 'madrona.manipulators.manipulators.ClipToStudyRegion' ]

You can also choose from several other built-in manipulators, define custom manipulators or make them optional. For more information, see the :ref:`manipulators documentation <manipulators>`.


Managing basemaps and KML datasets
------------------------------------
Base data layers are managed using a single KML file called the `public layers list`. If you defined KML layers 
when setting up your initial app, the layers list will be available at 
``http://madrona:81/layers/public/``. Download that file, save as ``public.kml``, 
and open for editing. You'll see that it is a standard KML file with `NetworkLink`s to the base data layers.  We can modify it by adding another KML NetworkLink ::

    <NetworkLink id="global-marine">
        <name>Global Marine</name>
        <visibility>0</visibility>
        <Link>
        <href>http://ebm.nceas.ucsb.edu/GlobalMarine/kml/marine_model.kml</href>
        </Link>
    </NetworkLink>

Once we've modified the public kml, browse to admin interface at ``http://madrona:81/admin/layers/publiclayerlist/add/`` and use it to upload the new KML file. After refreshing your browser cache, you should see the new KML avaible in the layers panel.

For more information, see the :ref:`layers documentation <layers>`.

Custom Links: Extending the API
---------------------------------
Many default API actions are defined out-of-box for Madrona Features (Create, Edit, Delete, KML download, etc.). If you want to provide other methods of accessing your features, Madrona provides a link option to extend the API. 

For example, let's say we want to provide a simple text file download for your area of interest. This would involve two steps: 

1. Add a link to your feature Options in ``testapp/models.py``::

    @register
    class AOI(PolygonFeature):
        description = models.TextField(null=True, blank=True)
        class Options:
            form = 'testapp.forms.AOI'
            verbose_name = 'Areas that interest me'
            manipulators = [ 'madrona.manipulators.manipulators.ClipToStudyRegion' ]
            links = (
                related('Text file',
                    'testapp.views.aoi_text',
                    select='single multiple',
                    type='text/csv'
                ),
            )

2. Create a view to handle the creation of text files for one or more features. Open ``testapp/views.py`` and add the following function::
   
    def aoi_text(request, instances):
        text = "Name, Description, Acres\n"
        for f in instances:
            text += "%s, %s, %f\n" % (f.name, f.description, f.acres)
        return HttpResponse(text)

Now restart the application, clear the cache and you should see ``Text File`` as an option in the download menu.

.. note:: There are many :ref:`default links <default_links>` provided by madrona - just think of all the work you'd have to do to a) manually create the views and urls to handle them and b) tweak the javascript and html to handle all of those views. Madrona just does it for you... nice, huh!  

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
