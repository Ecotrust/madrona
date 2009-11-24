REST Framework
==============

Overview
********

MarineMap includes server and client-side modules for managing user defined 
objects, such as Marine Protected Areas and Arrays. For a particular model 
this framework can provide RESTful web services, client modules to interact 
with those services, and a consistent user interface for create, update, and 
delete operations.

.. note::
  
  This framework is geared toward integrating new content types into the
  MarineMap application. While it could be extended in this sense, it is *not* 
  designed for creating web services aimed at 3rd party applications at this 
  time.

While Django makes it fairly easy to define urls and views to manage CRUD
operations on models, there are many disadvantages to handling this in an
ad-hoc fashion in MarineMap. Mostly it's boring and error prone, and difficult 
to provide a consistent UI this way.

Using this framework you can spend time worrying about defining your model,
crafting the form presented to users, and the KML representation of that 
model -- assuming the following constraints:

  * Instances of the model created by a user can be represented by a KML/KMZ
    listing service
    
  * Authentication for editing can be handled similarly to MPAs (Users can 
    only edit their own shapes, unless they are staff. Staff can edit anything.)

Once configured, MarineMap's user interface can be configured to display a 
listing of all user created objects for display on the map, as well as 
controls to add to the list and modify existing objects. :ref:`Manipulators<manipulators>`
can also be integrated for preprocessing spatial data.

Creating New Resources
**********************

First, you will need a `Model <http://docs.djangoproject.com/en/dev/topics/db/models/#topics-db-models>`_ and
`ModelForm <http://docs.djangoproject.com/en/dev/topics/forms/modelforms/#topics-forms-modelforms>`_. 
Creating these is beyond the scope of this documentation, but be sure to 
consider that you can configure :ref:`Manipulators<manipulators>` to enable 
some pre-processing on geographic features and subclass the 
:class:`Mpa <lingcod.mpa.models.Mpa>` model.

Once you have those two components, its time to setup the resources needed to
talk to the REST client. For the client-side components to work, the following
server-side pieces are needed:

  **Canonical URLs**
    One URL will represent each instance of your model. This primary resource 
    needs to support the following HTTP methods:
       
       * ``GET`` - Returns an HTML page that will be displayed in the sidebar 
         whenever the object is brought into focus. For Marine Protected Areas, 
         this is the attributes page.

       * ``POST`` - Updates the instance when form data in the request 
         validates. If it does not, the ModelForm is rendered to a page with 
         validation errors that the user can correct.

       * ``DELETE`` - Of course, deletes the resource.
       
  **Form Views**
    One view that returns a form to create new instances of the model, and 
    another for editing existing instances. Data from that update form can be
    posted to that instance's canonical URL.
    
  **Creation Service**
    There needs to be a url setup to receive form data to create new instances
    of the model.

  **KML Listing Service**
    A KML or KMZ service that lists all the instances of the model created by 
    a given user. This KML file must also have atom links described in the 
    next section that will control the behavior of the ``lingcod.rest`` 
    client module.

.. note::

  *What's with this creation service? Isn't that violating REST principals?*
  
  In a typical resource-oriented architecture, there might be a list or 
  collection resource that represents a type of resource, say a blog entry. 
  You post new entries to the collection resource, say an atom feed of 
  entries, to create new subordinate resources.
  
  That works great for a homogeneous collection of entries, but in the case of
  Marine Protected Areas and Arrays, these two resources are so interlinked 
  that it makes sense to expose them in one kml web service. This makes it 
  difficult to process incoming forms because it could be for either of those
  models.
  
  While this sort of collection->item convention can be helpfully clear, it is
  not a central tenant of REST. *Connectedness* is though, and since the 
  action attributes in the exposed forms link to the creation services, the
  client can know where to POST them.

canonical urls
--------------

To setup the canonical view for your model use ``lingcod.rest.views.resource``.

-- link to api docs --

form views and the creation service
-----------------------------------

use ``lingcod.rest.views.editing_resources``

the kml listing service
-----------------------

This resource is not addressed by the REST framework. The reason being that 
it can be difficult to provide a 
`generic view <http://docs.djangoproject.com/en/dev/ref/generic-views/>`_ that
covers all or even most use-cases. 

In the case of Marine Protected Areas and Arrays, separate listing services
could not be provided for these models since they are both so interrelated. 
Marine Protected Areas that belong to Arrays must show up in the interface
nested under those Arrays so it made sense to have multiple models associated
with a single service. In other cases, it may make sense to have a kml web 
service for each model.

For tips on how to implement a web service, you can look at the Marine 
Protected Area and Array kml service under ``lingcod/kmlapp/views.py``.

Connecting Your Resources
*************************

When you get to configuring your client, it will only need to be given a 
single url for your resources. This is because each of the previously 
described resources will contain links to other relevant parts of the service.

Forms have ``action`` attributes so the client knows where to POST them to. 
But the client also needs links in individual KML features to know where that 
resources URL is for DELETE, GET, and POST operations, and also where to find
a form to update it. This is where ATOM links come in.

You will need to add atom links that point to the previously described 
resources so the client module will know where to find new forms, where to 
submit them to, and what to display when an instance of your new model is
brought into focus.

Here are a couple examples:

.. code-block:: xml

  /** Document-level links */
  <atom:link rel="marinemap.create_form" title="Create a new Marine Protected Area" mm:icon="http://marinemap.org/path/to/icon.png" mm:model="simple_app_mpa" href="http://marinemap.org/path/to/form" />
  
  /** Feature-level links */
  <atom:link rel="marinemap.update_form" title="Edit" mm:icon="http://marinemap.org/path/to/icon.jpg" mm:model="simple_app_mpa" href="http://marinemap.org/path/to/form/1" />
  <atom:link rel="self" title="{{mpa.name}}" mm:model="simple_app_mpa" href="http://marinemap.org/path/to/mpa/attributes" />

document level links
--------------------

feature-level self links
------------------------

feature-level form links
------------------------



Configuring the Client
**********************

showing the listing
-------------------

Talk about lingcod.rest client-side API.

customizing the look and feel
-----------------------------

  * style kml
  * properly setup the atom links


customizing behavior
--------------------

  * register callback functions


Existing Resources - MPAs and Arrays
************************************

Some description here about how ``lingcod.rest`` is used for MPAs and Arrays

On the server side, the ``lingcod.rest`` app contains several generic views 
that can be used to expose 

REST modules can be found under ``/lingcod/rest`` and ``/media/rest``.

``lingcod.rest``

  intention
  what is rest
  describe how pieces fit together

Marine Protected Area and Array Services
****************************************

Creating New Resources
**********************

creating server-side services
-----------------------------

configuring the client
----------------------

customizing the interface
-------------------------
