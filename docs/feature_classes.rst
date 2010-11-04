The Features App
################

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
    ``PolygonFeature``, or ``3dModelFeature``, including the attributes to be
    stored with it.
  * Creating a Options inner-class, and using it to specify a form to use when 
    creating or editing this Feature Class.
  * Creating a template to use when displaying this Feature Class' attributes
  * Specifying links to downloads or services related to the Feature Class.
  * Specifying any optional parameters on the Options inner-class
  
Look at this crap example::

    class Mpa(PolygonFeature):
        ext = models.CharField(max_length="12")

        class Options:
            verbose_name = 'Folder'
            form = 'myproject.forms.MpaForm'
            links = (
                alternate('mlpa.views.shapefile', 'Shapefile', 
                    select='single', 
                    type='application/shapefile'),

                alternate('mlpa.views.kml_export', 'KMZ (Google Earth)', 
                    select='single multiple', 
                    type='application/vnd.google-earth.kmz',
                    generic=True),

                related('mlpa.views.spreadsheet', 'MPA Spreadsheet',
                    select='single',
                    type='application/excel'),

                edit('mlpa.views.delete_w_grids', 'Delete w/Grids', 
                    confirm="Are you sure you want to delete with grids?", 
                    select="single multiple",
                    args=[MpaArray],
                    kwargs={'keyword_argument': True}),

                edit_form('mlpa.views.tag', 'Tags',
                    select='single multiple',
                    generic=True,
                    models=(MpaArray, MlpaMpa)),
            )

Base Classes
************

Spatial Types
=============

PointFeature
------------

LineStringFeature
-----------------

PolygonFeature
--------------

3dModelFeature
--------------
Subclass of PointFeature, but with orientation and a 3d model representing it.

FeatureCollection Base Class
============================
Subclasses of FeatureCollection have a one-to-many relationship with one or 
more Feature Classes. One could create a Marine Protected Area Network class 
that can only contain MPAs, or a Folder class that can contain any combination
of FeatureClasses or even other Folders and FeatureCollections.

.. code-block:: python

    class Folder(FeatureCollection):
        class Options:
            # default options, can contain anything
            pass

    class MPANetwork(FeatureCollection):
        class Options:
            child_classes = ('mlpa.models.Mpa', )


The Options inner-class
**********************


required properties
===================

form (required)
---------------
Specifies a `ModelForm <http://docs.djangoproject.com/en/dev/topics/forms/modelforms/>`_
that will be used to create and edit features of this class. The form must
be a subclass of lingcod.features.forms.FeatureForm, and the path to the form
must be provided as a *string*. Otherwise you'll cause circular reference 
issues.

optional properties
===================

verbose_name
------------
Provide your feature class with a human readable name to be used within 
the interface. For example, this name determines the name used in the 
"Create" menu. If not specified, the CamelCase model name will be used. 
Even though it is optional, this property is obviously highly recommended.

show_template
-------------
By default, will look for the template at ``{{modelname}}/show.html`` when 
rendering shape attributes. For example, the template for a model named 
MpaArray  would be ``mpaarray/show.html``. You can specify a different 
template location with this option.

form_template
-------------
Use this option to specify a custom template to be shown when creating or 
editing a feature. By default, looks for a template under ``rest/form.html``.

form_context
------------
Specify a base context to use for rendering templates when creating and 
editing features.

show_context
------------
Specify a base context to use when rendering feature attributes.

shareable
---------
Enabled by default, set to False to disable sharing functionality.

copy
----
Enabled by default, set to False to disable copy functionality.

copy_method
-----------
By default, MarineMap will look for a method named ``copy`` on the model that 
will be called to create copies. If none is found, and copying is enabled, a
generic copy method will be used. This option can be used to specify a 
function of another name::

  class Options:
    copy_method = 'duplicate'

.. note::
  copy functions must return the copied instance
  
manipulators
------------
fucking manipulators, `how do they work? <http://www.youtube.com/watch?v=_-agl0pOQfs>`_



Specifying a Template for Feature Attributes
********************************************

Linking to Downloads and Services
*********************************

