Feature Classes
===============

MarineMap supports adding new *Feature Classes*, useful for collecting both 
spatial and non-spatial designs from users that can be represented in the user
interface with a KML file. These can be used to represent Folders, MPAs, MPA 
Networks, Undersea Cables, Wind Farms, etc.

Configuring Feature Class Capabilities - The Rest Inner-Class
*************************************************************

The capabilities of each feature class can be configured using a declarative
syntax on an inner class called `Rest`. This can be used to enable and disable
features such as shape sharing, specify a form to use when creating new 
instances, and provide links to alternative representations such as Shapefiles
that appear in the Export menu.

Look at this crap example::

    class Folder(Feature):
        ext = models.CharField(max_length="12")

        class Rest():
            verbose_name = 'Folder'
            form = FolderForm

Rest inner-class properties
---------------------------

required
^^^^^^^^

form
""""
Specifies a `ModelForm <http://docs.djangoproject.com/en/dev/topics/forms/modelforms/>`_
that will be used to create and edit features of this class. The form must
be a subclass of lingcod.features.forms.FeatureForm.

optional
^^^^^^^^

verbose_name
""""""""""""
Provide your feature class with a human readable name to be used within 
the interface. For example, this name determines the name used in the 
"Create" menu. If not specified, the camelcase model name will be used. 
Even though it is optional, this property is obviously highly recommended.

show_template
"""""""""""""
By default, MarineMap will use a naming convention to look for the template 
used to display a shapes attributes in the sidebar. The template for MpaArray 
would be ``mpa_array/show.html``. You can specify a different location by 
specifying the ``show_template`` option.
