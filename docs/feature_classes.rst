The Features App
================

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

  * Represent various management scenarios as Point, Linestring or Polygon data
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
================================

Lets walk through the basics of creating a simple Feature Class. The basic 
process involves:

  * Defining a subclass of ``PointFeature``, ``LinestringFeature``, 
    ``PolygonFeature``, or ``3dModelFeature``, including the attributes to be
    stored with it.
  * Creating a Config inner-class, and using it to specify a form to use when 
    creating or editing this Feature Class.
  * Creating a template to use when displaying this Feature Class' attributes
  * Specifying links to downloads or services related to the Feature Class.
  * Specifying any optional parameters on the Config inner-class
  
Look at this crap example::

    class Folder(Feature):
        ext = models.CharField(max_length="12")

        class Config:
            verbose_name = 'Folder'
            form = 'myproject.forms.FolderForm'

Base Classes
============

Spatial Types
^^^^^^^^^^^^^

FeatureCollection Base Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Config inner-class
======================

form
^^^^
Specifies a `ModelForm <http://docs.djangoproject.com/en/dev/topics/forms/modelforms/>`_
that will be used to create and edit features of this class. The form must
be a subclass of lingcod.features.forms.FeatureForm, and the path to the form
must be provided as a *string*. Otherwise you'll cause circular reference 
issues.


optional parameters
^^^^^^^^^^^^^^^^^^^

verbose_name
""""""""""""
Provide your feature class with a human readable name to be used within 
the interface. For example, this name determines the name used in the 
"Create" menu. If not specified, the CamelCase model name will be used. 
Even though it is optional, this property is obviously highly recommended.

show_template
"""""""""""""
By default, will look for the template at ``{{modelname}}/show.html`` when 
rendering shape attributes. For example, the template for a model named 
MpaArray  would be ``mpaarray/show.html``. You can specify a different 
template location with this option.

form_template
"""""""""""""
Use this option to specify a custom template to be shown when creating or 
editing a feature. By default, looks for a template under ``rest/form.html``.

form_context
""""""""""""
Specify a base context to use for rendering templates when creating and 
editing features.

show_context
""""""""""""
Specify a base context to use when rendering feature attributes.

shareable
"""""""""
Enabled by default, set to False to disable sharing functionality.

copy
""""
Enabled by default, set to False to disable copy functionality.

copy_method
"""""""""""
By default, MarineMap will look for a method named ``copy`` on the model that 
will be called to create copies. If none is found, and copying is enabled, a
generic copy method will be used. This option can be used to specify a 
function of another name::

  class Config:
    copy_method = 'duplicate'

.. note::
  copy functions must return the copied instance



Specifying a Template for Feature Attributes
============================================

Linking to Downloads and Services
=================================

