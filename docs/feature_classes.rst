Feature Classes
===============

MarineMap supports adding new *Feature Classes*, useful for collecting both 
spatial and non-spatial designs from users that can be represented in the user
interface with a KML file. These can be used to represent Folders, MPAs, MPA 
Networks, Undersea Cables, Wind Farms, etc.

Configuring Feature Class Capabilities - The Config Inner-Class
***************************************************************

The capabilities of each feature class can be configured using a declarative
syntax on an inner class called `Config`. This can be used to enable and 
disable features such as shape sharing, specify a form to use when creating 
new instances, and provide links to alternative representations such as 
Shapefiles that appear in the Export menu.

Look at this crap example::

    class Folder(Feature):
        ext = models.CharField(max_length="12")

        class Config:
            verbose_name = 'Folder'
            form = 'myproject.forms.FolderForm'

Config inner-class properties
-----------------------------

required
^^^^^^^^

form
""""
Specifies a `ModelForm <http://docs.djangoproject.com/en/dev/topics/forms/modelforms/>`_
that will be used to create and edit features of this class. The form must
be a subclass of lingcod.features.forms.FeatureForm, and the path to the form
must be provided as a *string*. Otherwise you'll cause circular reference 
issues.

optional
^^^^^^^^

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

