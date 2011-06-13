`lingcod.features`: Spatial Content Management  
##############################################

The ``lingcod.features`` app works along with other MarineMap apps to create a 
system that is best described as a content management system for user-designed
spatial features. This system can be configured quickly to support a range of 
management options such as marine protected areas, hydrokinetic generators, 
wind turbines, or undersea cables. With one model definition it's possible to
define the data schema for storing these features, as well as what behaviors 
and actions they support within the MarineMap interface. I high degree of 
customization can be achieved with a MarineMap project with this declarative 
format, without having to customize the view or client-side javascript 
components.

Feature Classes can be configured to:

  * Represent various management scenarios as Point, LineString or Polygon 
    data
  * Collect attributes from users using forms generated from the model 
    definition (or customized forms)
  * Pre-process and validate user-defined geometries with Manipulators
  * Enable sharing of features among users
  * Add custom downloads, like Shapefile or Excel files
  * Support custom editing actions
  
In addition, FeatureCollection Classes can be created that are collections of
Feature Class instances with their own attributes. These can be used to 
represent simple Folders to help users organize their designs, or represent 
management concepts such as Marine Protected Area Networks.

Creating a Spatial Feature Class
********************************

Lets walk through the basics of creating a simple Feature Class. The basic 
process involves:

  * Defining a subclass of ``PointFeature``, ``LineStringFeature``, 
    ``PolygonFeature``, including the attributes to be
    stored with it.
  * Creating an Options inner-class, and using it to specify a form to use 
    when creating or editing this Feature Class.
  * Creating kml and kml_style properties that define it's KML representation
  * Specifying links to downloads or services related to the Feature Class.
  * Specifying any optional parameters on the Options inner-class
  * Creating a template to use when displaying this Feature Class' attributes
  
Look at this example::

    from lingcod.features import register
    from lingcod.features.models import PolygonFeature
    from lingcod.features.forms import FeatureForm

    @register
    class Mpa(PolygonFeature):
        ext = models.CharField(max_length="12")

        class Options:
            verbose_name = 'Marine Protected Area'
            form = 'myproject.forms.MpaForm'
            links = (
                alternate('Shapefile',
                    'mlpa.views.shapefile', 
                    select='single', 
                    type='application/shapefile'),

                alternate('KMZ (Google Earth)', 
                    'mlpa.views.kml_export', 
                    select='single multiple', 
                    type='application/vnd.google-earth.kmz',
                    generic=True),

                related('MPA Spreadsheet',
                    'mlpa.views.spreadsheet', 
                    select='single',
                    type='application/excel'),

                edit('Delete w/Grids', 
                    'mlpa.views.delete_w_grids', 
                    confirm="Are you sure you want to delete with grids?", 
                    select="single multiple",
                    args=[MpaArray],
                    kwargs={'keyword_argument': True}),

                edit_form('Tags',
                    'mlpa.views.tag', 
                    select='single multiple',
                    generic=True,
                    models=(MpaArray, MlpaMpa)),
            )

    class MpaForm(FeatureForm):
        class Meta:
            model = Mpa 

Defining the Model
==================

Must be a subclass of one of the ``Feature`` subclasses (``PointFeature``, 
``PolygonFeature``, ``LineStringFeature``)

.. note::
    *Keep the model name to under 30 characters in length*. 
    When creating a Feature model, django will automatically add permissions with a verbose name (e.g. "Can share Your Model Name") 
    which must be < 50 chars. Keeping the model name to around 30 chars or less will prevent SQL errors when creating the model. 

.. note::
    *When creating a model for your unit tests, define the model outside of your TestCase class*. 
    Otherwise the feature class gets destroyed when the test finishes but it is never 'unregistered'
    which can lead to very difficult SQL/ORM debugging problems later in the tests.

Specifying a Form
=================

All Feature Classes must have an ``Options`` inner-class that contains a 
property specifying the ``FeatureForm`` subclass that can be used to edit it.
All :ref:`other properties <optional-properties>` on the Options inner-class 
are optional.

Creating a "Show" Template
==========================

The show template is used to render sidebar content for a feature within the
MarineMap interface, and can also be used to render a printable and 
bookmarkable page for it. This template can be placed in any template 
directory by default under ``{{slug}}/show.html``. Subdirectories are used to
allow for overriding templates as mentioned in the 
`django documentation <http://docs.djangoproject.com/en/1.2/ref/templates/api/#using-subdirectories>`_.
The default path to the show template can be changed using an optional 
`show_template`_ parameter to the Options inner-class.

Templates will be rendered with the following context:
    
    * ``instance`` - the feature class instance being being displayed
    * ...
    * ...

You can add to this list using the `show_context`_ Option property.

Customizing the Output Styling and KML Representation 
=====================================================

There are three primary visual representations of Features: KML, the KMLTree and static maps. 
While the base Feature classes define reasonable default styling, it's likely that you'll need to customize the look and feel for your implementation.

  * :ref:`Customizing the styling of the KML <kmlapp>`
  * :ref:`Customizing the Mapnik static map rendering <staticmap>`

Customizing the styling of the KMLTree
--------------------------------------
You can use css to style the representation of the Features in the KMLTree, specifically the small icon to the left of the Feature name. There are two mechanisms to do this. 

First you can specify an ``icon_url`` in the Options. This can be an absolute http URL or relative to the MEDIA_ROOT directory.

If you need more control over styling icons (such as specifying multiple styles or using scrolling sprites) you can use raw css by overriding the Feature.css() classmethod. For example::

    @classmethod
    def css(klass):
        return """ 
        li.KmlDocument > .icon { 
          background: url('%(media)s/sprites/kml.png?1302821411') no-repeat -566px 0px ! important;
        }
        li.%(uid)s > .icon { 
          background: url('%(media)s/sprites/kml.png?1302821411') no-repeat 0px 0px ! important;
        } 
        """ % { 'uid': klass.model_uid(), 'media': settings.MEDIA_URL }

Beyond the Basics
=================

Implementing a Custom Copy Method
---------------------------------
 
Some default copying behavior is provided with the built-in feature.copy method. Unless you want to reimplement/change all that logic (and maybe your application requires it) you can call the Super() function and just override the necessary bits::

    @register
    class Folder(FeatureCollection):
        
        def copy(self, user):
            copy = super(Folder, self).copy(user)
            copy.name = copy.name.replace(' (copy)', '-Copy')
            copy.save()
            return copy

Specifying Manipulators
-----------------------

You must specify a list of required manipulators; if no manipulators are required simply pass an empty list ``[]``. Optional manipulators can be specified as well::

    @register
    class TestMpa(PolygonFeature):
        ...
        class Options:
            manipulators = [ 'lingcod.manipulators.tests.TestManipulator' ]
            optional_manipulators = [ 'lingcod.manipulators.manipulators.ClipToGraticuleManipulator' ]

Base Classes
************

Feature
=======
.. autoclass:: lingcod.features.models.Feature
    :members:
    :exclude-members: __init__

Spatial Feature
===============
.. autoclass:: lingcod.features.models.SpatialFeature
    :members:
    :exclude-members: __init__

PointFeature
------------
.. autoclass:: lingcod.features.models.PointFeature
    :members:
    :exclude-members: __init__

LineStringFeature
-----------------
.. autoclass:: lingcod.features.models.LineFeature
    :members:
    :exclude-members: __init__

PolygonFeature
--------------
.. autoclass:: lingcod.features.models.PolygonFeature
    :members:
    :no-undoc-members:
    :exclude-members: __init__

FeatureCollection Base Class
============================
Subclasses of FeatureCollection have a one-to-many relationship with one or 
more Feature Classes. One could create a Marine Protected Area Network class 
that can only contain MPAs, or a Folder class that can contain any combination
of FeatureClasses or even other Folders and FeatureCollections.

One important note about the sharing behavior of FeatureCollections - If a user shares a 
collection, all the features/collections contained within it are implicitly shared.

.. code-block:: python

    class MPANetwork(FeatureCollection):
        class Options:
            valid_children = ('mlpa.models.Mpa', )

.. autoclass:: lingcod.features.models.FeatureCollection
    :members:
    :exclude-members: __init__, url_name, parent_slug, reverse, json

The Options inner-class
***********************


.. py:attribute:: form (required)

    Specifies a `ModelForm <http://docs.djangoproject.com/en/dev/topics/forms/modelforms/>`_
    that will be used to create and edit features of this class. The form 
    must be a subclass of lingcod.features.forms.FeatureForm, and the path
    to the form must be provided as a *string*. Otherwise you'll cause 
    circular reference issues.

.. py:attribute:: verbose_name

    Provide your feature class with a human readable name to be used 
    within the interface. For example, this name determines the name used 
    in the "Create" menu. If not specified, the CamelCase model name will 
    be used. Even though it is optional, this property is obviously highly 
    recommended.

.. py:attribute:: show_template

    By default, will look for the template at ``{{modelname}}/show.html`` 
    when rendering shape attributes. For example, the template for a model 
    named MpaArray  would be ``mpaarray/show.html``. You can specify a 
    different template location with this option.

.. py:attribute:: form_template

    Use this option to specify a custom template to be shown when creating
    or editing a feature. By default, looks for a template under 
    ``features/form.html``.

.. py:attribute:: form_context

    Specify a base context to use for rendering templates when creating and 
    editing features.

.. py:attribute:: show_context

    Specify a base context to use when rendering feature attributes.

.. py:attribute:: copy

    Enabled by default, set to False to disable copy functionality. Calls the
    copy method of Feature, which can be overriden by subclasses to customize
    this functionality.

.. py:attribute:: manipulators

    Defaults to clipping features to the study region. Set to ``[]`` to 
    disable.

.. py:attribute:: optional_manipulators

    Optional list of manipulators that users can choose to apply to any digitized 
    features. 

.. py:attribute:: links

    Specify links associated a Feature Class that point to related downloads, 
    export tools, and editing actions that can be performed.

Specifying Links
================

Links allow developers to extend the functionality of features by specifying
downloads, actions, or related pages that should be made available through the
interface. There are 4 types of Links:

  * ``alternate`` links specify alternative representations of features that 
    should be made available through the Export menu.
  * ``related`` links specify related downloads or pages that are also made 
    available in the Export menu but in a downloads section.
  * ``edit`` links specify items that should appear in the Edit menu and 
    modify a selected feature, create a copy, or some other 
    `non-idempotent <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html>`_
    action.

Here's an example of links in use::
    
    @register
    class RenewableEnergySite(Feature):
        type = models.CharField(max_length=1, choices=TYPE_CHOICES)
        class Options:
            verbose_name = 'Renewable Energy Site'
            form = 'lingcod.features.tests.RenewableEnergySiteForm'
            links = (
                alternate('Export KML',
                    'lingcod.features.tests.kml',
                    select='multiple single'
                ),
                related('Viewshed Map',
                    'lingcod.features.tests.viewshed_map',
                    select='single',
                    type='image/png'
                ),
                edit('Delete w/related cables',
                    'lingcod.features.tests.delete_w_cables',
                    select='single multiple',
                    confirm="""
                    Are you sure you want to delete this site and associated 
                    undersea cables? 
                    This action cannot be undone.
                    """
                )
            )

creating compatible views
-------------------------

Views that are wired up to features using links must accept a second argument
named ``instance`` or ``instances`` depending on whether they can work on 
single or multiple selected features. 

The features app will handle requests 

Generic views will handle cases where a user is not authorized to view or edit
a feature, requests related to features that cannot be found, and improperly 
configured views. 

link properties
---------------

.. autoclass:: lingcod.features.Link
    :members:
    :no-undoc-members:
    :exclude-members: __init__, url_name, parent_slug, reverse, json
