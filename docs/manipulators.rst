.. _manipulators:

Manipulators
============

What is a Manipulator?
**********************

There are many cases in which a user-defined geometry, whether MPA or other, 
needs to be modified by an automated process. This process can either be 
initiated by the user as a tool or context action, or as part of the initial 
creation of a new object. Typically, the user is provided an opportunity to review 
any changes made to their geometry and given the chance to accept or reject those 
changes or to modify the parameters that went into the manipulations.

Use cases might include clipping an MPA to the study region or to a specified 
graticule.  Both of these manipulations are already included in MarineMap and 
can easily be accessed by additional applications.  Instructions for 
accessing such built-in manipulators follow, as do instructions for adding your 
own manipulators.  

Specifying or Changing the Manipulators
***************************************

Any number of manipulative actions can be assigned to an MPA.  

Typically, when a shape is drawn, a series of manipulations is executed on that 
shape.  Which manipulators are executed, and the order in which those manipulators 
are executed are determined by an assignment in the Options class for a given model.  
Within the Model, the Options class should contain a line similar to the following:

.. code-block:: python 

    class Options:
        manipulators = [ ClipToStudyRegionManipulator, EastWestManipulator ]
 
In the above example from the ``simple_app/models.py`` file, we can see that 2 manipulators 
are listed for the Mpa model, ``ClipToStudyRegionManipulator``, and ``EastWestManipulator``.  


The first of these is a predefined manipulator, the second is more of a sample 
manipulator that is provided within the simple_app application to demonstrate how you 
might create your own manipulators (see the next section for more details on creating your own 
manipulators).  These manipulators will be executed in the same order given in the
``manipulators`` assignment statement.  

To summarize, both built-in and user-defined manipulators can be designated to a model by assigning a list of manipulators, 
in the desired sequence, to ``Options.manipulators`` within the model that contains the shape to be manipulated.

.. code-block:: python 

    class Options:
        manipulators = [ YourManipulator1, YourManipulator2 ]
..


Creating a New Manipulator 
**************************

The basic manipulators provided by Lingcod may not provide all the necessary 
manipulations for your needs.  Creating your own manipulators is somewhat 
straightforward and we have provided a sample manipulator, ``EastWestManipulator``, 
in ``example_projects/simple/simple_app/manipulators.py`` to get you started.  

To create your own manipulator, you'll want to add a ``manipulators.py`` file to your base 
application (server-side).  This file will house your newly defined manipulators, each accompanied by a
``manipulatorsDict`` dictionary entry that serves to notify the manipulators app of your manipulators.  

Things to keep in mind as you create your own manipulators:

  * Your manipulator should inherit from ``BaseManipulator``
      * this inheritance will provide various helper functions, templates, and Exceptions, as well 
        as enabling your manipulator to work seemlessly within the Lingcod application
        
.. code-block:: python
  
    class YourManipulator(BaseManipulator):
..
  
  * Your manipulator constructor should expect at least one parameter, which will be the target shape geometry in 
    the client-side projection/srid (this srid value is defined by settings.GEOMETRY_CLIENT_SRID).  
    
.. code-block:: python

    def __init__(self, target_shape, **kwargs):
        self.target_shape = target_shape
..

  * The inherited ``BaseManipulator`` class provides the following commonly used Exceptions, each of which 
    triggers a relevant template when raised
    
      * ``InternalException`` can be raised when an unexpected error out of your control occurs, 
        such as when code that is not yours raises an exception. 
      * ``InvalidGeometryException`` can be raised when the user-drawn geometry is not a 
        valid geometry.  Such situations are automatically handled for you when you use 
        the ``BaseManipulator.target_to_valid_geom()`` function to generate a geometry from 
        the target shape parameter.
      * ``HaltManipulations`` is typically raised when your function recognizes that it is no 
        longer necessary for additional manipulations to take place (such as when the 
        clipped shape is reduced to an empty geometry).  
        
  * ``BaseManipulator`` also provides the following inherited functions
  
      * ``target_to_valid_geom(self, shape)``, is used to build a valid geometry from the target 
        shape.
      * ``do_template(self, key, internal_message='', extra_context{})``, which uses as context, 
        the ``internal_message`` and any ``extra_context``, in rendering a particular template 
        (identified by ``'key'``) in ``Options.html_templates`` (inherited or not).  The result of 
        this function can be used as the second argument to the ``result()`` function which 
        we'll describe next...
      * ``result(self, clipped_shape, html="", success="1")``, should be used as the return 
        value for your manipulator's ``manipulate()`` function (talked about next).  
        This function ensures that the required keys are provided, and suitable default values are given.  
            
  * Your manipulator should provide a definition for a ``manipulate()`` function (overriding the empty 
    definition in ``BaseManipulator``).  
    
      * This is the function that will be called by the manipulators app to execute your manipulator.  
      * This function should return a call to self.result() (inherited from BaseManipulator) with required parameter 
        ``'clipped_shape'``, a geometry in the projection/srid of the client (defined by GEOMETRY_CLIENT_SRID in settings).  
        This function also allows two optional parameters, ``'html'`` and ``'success'``.  The former being a template 
        generally used to explain the manipulative action to the client, and the latter an indication of success 
        (either '1' or '0').
        
.. code-block:: python

    def manipulate(self):
        target_shape = self.target_to_valid_geom(self.target_shape)
        ...
        #target_shape is manipulated in some way
        ...
        status_html = self.do_template("1") 
        return self.result(manipulated_shape, status_html)
..
    
  * ``BaseManipulator`` provides access to some error-related templates in ``Options.html_templates``, 
    and defining such a dictionary in your own manipulators Options class will enable your code to use the 
    inherited ``do_template()`` function described above.  
        
.. code-block:: python
  
    class Options:
        name = 'YourManipulatorClass'
        html_templates = {
            '1':'manipulators/template1.html',
            '2':'manipulators/template2.html',
            '3':'manipulators/template3.html',
        }
..

  * The manipulators.Options class can optionally specify a ``display_name`` and ``description`` which 
    will provide a nicer UI when using user-specified manipulators. If they are not specified, the ``name`` 
    will be shown verbatim in the html form. 
        
.. code-block:: python
  
    class Options:
        name = 'YourManipulatorClass'
        display_name = 'Your Manipulator Class'
        description = 'Check it out. This is my brand new manipulator.'
..
  * As mentioned earlier, for each manipulator class in your ``manipulators.py`` there should also  
    be a dictionary entry for ``manipulatorsDict``.  This allows your manipulator to be seen from 
    the manipulators application.  

.. code-block:: python
  
    manipulatorsDict[YourManipulator.Options.name] = YourManipulator
..

We invite you to use the manipulator provided by simple_app (or any of our manipulators defined in 
``lingcod/manipulators``) as a template for generating your own manipulators.  

.. note::

    In addition to ``BaseManipulator``, we also provide a ``ClipToShapeManipulator`` and a ``DifferenceFromShapeManipulator`` that can be subclassed to simplify your own manipulator.

    Both of these classes inherit from ``BaseManipulator`` while also providing a ready-made ``manipulate()`` method that will take the respective interesection of or difference from any two shapes.

    
Optional Manipulators
*********************

There may be cases where certain manipulators should be optional and user-selectable depending on the purpose of their MPA. 
In this case we can specify `optional_manipulators` in the MPA model Options.

.. code-block:: python 

    class Options:
        manipulators = [ ClipToStudyRegionManipulator, ]
        optional_manipulators = [ EastWestManipulator, ]

On the user-interface side, when a user creates or edits a shape, there will be a form with checkboxes allowing them to select from these optional manipulators. 

On the database side, the `active manipulators` that are applied to a given MPA are stored as a comma-separated string in the MPA table. 
When and if the geometry needs to be saved again, the previously selected manipulators will be applied.  
The required manipulators will always be applied regardless of the content of the MPA.manipulators field. 
In other words, the MPA.manipulators field serves only to trigger the application of optional manipulators. 

If there are no required manipulators, you must still provide an empty list for Options.manipulators

.. code-block:: python 

    class Options:
        manipulators = []
        optional_manipulators = [ ClipToStudyRegionManipulator, EastWestManipulator, ]

If the user doesn't select any other optional manipulators and there are none required, a special case is triggered. We can't allow any arbitrary input so the shape needs to be checked as a valid geometry at the very least. For this case, the `NullManipulator` is triggered which does nothing except ensure that the geometry is clean. Note that the NullManipulator should *not* appear in either your manipulators or optional_manipulators lists. 

.. note::

   There are several steps that a marinemap-based project must take in order to ensure that optional manipulators function correctly.

   First, make sure that the MPA superclass is migrated to reflect the MPA schema change.
   Secondly, make sure to run manage.py install_media
   Third, the superclass of MPAForm must include 'manipulators' in the fields list.
   Lastly, the map.html template must include the manipulators div as specified in the common/map.html template. 


Manipulator Models
******************

You may want to store a pre-defined shape in the database that will be used by your manipulator.  

For this purpose we provide an abstract model, ``BaseManipulatorGeometry``, that can be used to simplify your manipulator model building.

There are also two management commands that can be used to load a geometry from a shapefile into the database provided certain fields and methods are present in the model (all of which are provided by ``BaseManipulatorGeometry``).

First, create your own manipulator model such as the one below (be sure to inherit from ``BaseManipulatorGeometry``, as well as provide ``name`` and ``geometry`` fields):

.. code-block:: python 
  
    class MyClippingLayer(BaseManipulatorGeometry):
        name = models.CharField(verbose_name="My Clipping Layer Name", max_length=255, blank=True)
        geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="My Clipping Layer")

        def __unicode__(self):
            return "MyClippingLayer data, created: %s" % (self.creation_date)

Second, use ``syncdb`` or ``migrate`` to generate the associated database table.
            
Finally, load your own geometry layer with the following management commands:

.. code-block:: python 
  
    manage.py create_manipulator_geom <path to shapefile>/my_clipping_region.shp <module name>.models.MyClippingLayer 
    manage.py change_manipulator_geom 1 MyClippingLayer      

    