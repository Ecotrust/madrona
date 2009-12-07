.. _manipulators:

Manipulators
============

What is a Manipulator?
**********************

There are many cases in which a user-defined geometry, whether MPA or other, 
needs to be modified by an automated process. This process can either be 
initiated by the user as a tool or context action, or as a part of the initial 
creation of a new object. Typically, the user is provided an opportunity to review 
the changes to their geometry and given the chance to accept or reject the changes
or modify the parameters that went into the manipulations.

Use cases might include clipping an MPA to the study region or to a specified 
graticule.  Both of these manipulations are already included in MarineMap and 
can easily be accessed by additional applications.  Instructions for 
accessing such built-in manipulators follow, as do instructions for adding your 
own manipulators.  

Specifying or Changing the Manipulators
***************************************

Any number of manipulative actions can be assigned to an MPA.  

Typically, when a shape is drawn, a series of manipulations is executed on that 
shape.  This list of manipulations is requested from the client-side manipulators 
application via a URL named ``'manipulators-list'``.  Your project will want a 
handler for this request.  An example of such can be found by looking in the 
``views.py`` file in ``example_projects/simple``.  Here we can see that the 
view associated with that URL executes a redirect to the manipulators app.  
That redirect, ``'/manipulators/list/simple_app/mpa/'``, must provide the 
appropriate application name, ``simple-app``, and model name, ``mpa``, 
which a manipulator handler will use to access the Options class in that model.  
The Options class should in turn contain the actual list of manipulators to be 
executed.  In the ``simple_app/models.py`` file we can see that 2 manipulators 
are being requested, ``ClipToStudyRegionManipulator``, and ``EastWestManipulator``.  

.. code-block:: python 

    class Options:
        manipulators = [ ClipToStudyRegionManipulator, EastWestManipulator ]

The first of these is a predefined manipulator, the second is more of a sample 
manipulator that is provided within the simple_app application to demonstrate how you 
might create your own manipulators (see next section for more details on creating your own 
manipulators).  All manipulators will be executed in the order given.  

To recap, all that needs to be done in order to specify the manipulators or change which manipulations are performed:

  * make sure there is a url pattern for ``'manipulators-list'`` in your project's ``urls.py``
  
.. code-block:: python 

    urlpatterns = patterns(
        (r'^manipulators-list/', 'manipulatorList'),
        ...
    )
..

  * provide a related view with a redirect to ``manipulators/list`` that includes the 
    `app name` and `model name` where the manipulators list can be found
    
.. code-block:: python 

    def manipulatorList(request):
        return redirect('/manipulators/list/<app-name>/<model name>/')
..

  * assign a list of manipulators, in the desired sequence, to ``Options.manipulators`` in 
    the model mentioned in the redirect
    
.. code-block:: python 

    class Options:
        manipulators = [ YourManipulator1, YourManipulator2 ]
..


Creating a New Manipulator 
**************************

The basic manipulators provided by Lingcod may not provide all the necessary 
manipulations for your needs.  Creating your own manipulators is somewhat 
straightforward and we have provided a sample manipulator, ``EastWestManipulator``, 
in ``example_projects/simple_app/manipulators.py`` to get you started.  

To create your own manipulator, you'll want to add a ``manipulators.py`` file to your base 
application (server-side).  This file will house your manipulators as well as ``manipulatorsDict`` 
dictionary entries that serve to notify the manipulators app of your manipulators.  

Things to keep in mind as you create your own manipulators:

  * Your manipulator should inherit from ``BaseManipulator``
      * this inheritance will provide various helper functions, templates, and Exceptions, as well 
        as helping your manipulator to work seemlessly within the Lingcod application
        
.. code-block:: python
  
    class YourManipulator(BaseManipulator):
..
        
  * Your manipulator should expect at least one parameter, which will be the target shape geometry in 
    the client-side projection/srid (in the case of a Google Earth client, the srid will be 4326).  
  * Your manipulator should provide a definition for a ``manipulate()`` function (overriding the empty definition in ``BaseManipulator``).  
      * This function will be called automatically when your manipulator class is included 
        in the ``Options.manipulators`` list.  
      * This function should return a call to self.result() with required parameter ``'clipped_shape'``,
        a geometry in the projection/srid of the client -- 4326 in the case of Google Earth.  This function 
        also allows two optional parameters, ``'html'`` and ``'success'``.  The former being a template generally used
        to explain the manipulative action to the client, and the latter an indication of success (either '1' or '0').
  * Three Exceptions are provided by the ``BaseManipulator`` class.  Their use will trigger relevant templates to be rendered by the manipulators app.  
      * ``InternalException`` should be raised when an unexpected error out of your control occurs, 
        such as when code that is not yours raises an exception. 
      * ``InvalidGeometryException`` should be raised when the user-drawn geometry is not a 
        valid geometry.  Such situations are automatically handled for you when you use 
        the ``BaseManipulator.target_to_valid_geom()`` function to generate a geometry from 
        the target shape parameter.
      * ``HaltManipulations`` is typically raised when your function recognizes that it is no 
        longer necessary for additional manipulations to take place (such as when the 
        clipped shape is reduced to an empty geometry).  
  * ``BaseManipulator`` provides the following useful functions:
      * ``target_to_valid_geom(self, shape)``, is used to build a valid geometry from the target 
        shape.
      * ``do_template(self, key, internal_message='', extra_context{})``, which uses as context, 
        the ``internal_message`` and any ``extra_context``, in rendering a particular template 
        (identified by ``'key'``) in ``Options.html_templates`` (inherited or not).  The result of 
        this function can be used as the second argument to the ``result()`` function which 
        we'll describe next.
      * ``result(self, clipped_shape, html="", success="1")``, should be used as the return 
        result for your ``manipulators()`` function.  It ensures that the required keys are 
        provided, and suitable default values are given.
        
.. code-block:: python

    def manipulate(self):
        target_shape = self.target_to_valid_geom(self.target_shape)
        ...
        #target_shape is manipulated in some way
        ...
        status_html = self.do_template("1")
        return self.result(manipulated_shape, status_html)
..
   
      * Finally, ``BaseManipulator`` provides access to some useful templates in ``Options.html_templates``.  
        Providing such a dictionary in your manipulators Options class will allow you to seamlessly use the 
        inherited ``do_template()`` function described earlier.  
        
.. code-block:: python
  
    class Options:
        name = 'Your Manipulator Class'
        html_templates = {
            '1':'manipulators/template1.html',
            '2':'manipulators/template2.html',
            '3':'manipulators/template3.html',
        }
..

  * As mentioned earlier, each manipulator class in your ``manipulators.py`` should provide 
    a dictionary entry for ``manipulatorsDict``.  This allows your manipulator to be seen from 
    the manipulators application.  

.. code-block:: python
  
    manipulatorsDict[YourManipulator.Options.name] = YourManipulator
..

We invite you to use the manipulator provided by simple_app (or any of our manipulators defined in 
``lingcod/manipulators``) as a template for generating your own manipulators.  