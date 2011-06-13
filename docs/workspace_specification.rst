Workspace Documents
###################

Workspace documents are a json data structure passed to the client along with
KML files to specify how feature classes within that file can be interacted 
with. Primarily, this interaction takes the form of options available in the 
editing toolbar. Workspaces indicate for each feature class:

  * Alternative representations available within the Export menu, such as kml
    or shapefile downloads.
  * Related files that can be downloaded, such as spreadsheet or pdf reports.
  * Editing actions that can be performed
  * How to create, update, and delete instances
  * How to view feature attributes in the sidebar
  
.. note::

    Workspace documents are automatically created and embedded within kml 
    files by the features app. For project implementations, it should be 
    unnecessary to modify these files directly. This documentation is intended
    for MarineMap developers who may need to add generic features to the core
    framework.
    
example workspace document
**************************

.. code-block:: javascript

    {
      "feature-classes": [
        {
          "title": "Marine Protected Area",
          "id": "features_mpa", 
          "link-relations": {
            "self": {
              "uri-template": "/features/mpa/{id}/"
            }, 
            "create": {
              "uri-template": "/features/mpa/form/"
            }, 
            "related": [
              {
                "title": "Habitat Spreadsheet",
                "uri-template": "/features/mpa/links/habitat-spreadsheet/{id+}/", 
                "select": "single", 
                "rel": "related"
              }
            ], 
            "update": {
              "uri-template": "/features/mpa/{id}/form/"
            }
          }
        }, 
        {
          "title": "Renewable Energy Site",
          "id": "features_renewableenergysite", 
          "link-relations": {
            "self": {
              "uri-template": "/features/renewableenergysite/{id}/"
            }, 
            "create": {
              "uri-template": "/features/renewableenergysite/form/"
            }, 
            "related": [
              {
                "title": "Viewshed Map"
                "uri-template": "/features/renewableenergysite/links/viewshed-map/{id+}/", 
                "select": "single", 
                "rel": "related"
              }
            ], 
            "update": {
              "uri-template": "/features/renewableenergysite/{id}/form/"
            }
          }
        }, 
        {
          "title": "Folder",
          "id": "features_folder", 
          "collection": {
            "add-uri-template": "/features/collections/add/{id+}/",
            "remove-uri-template": "/features/collections/remove/{id+}/",
            "valid-children": [
              "features_folder", 
              "features_mpa", 
              "features_renewableenergysite"
            ]
          },
          "link-relations": {
            "edit": [
              {
                "title": "Delete folder and contents"
                "method": "POST", 
                "uri-template": "/features/folder/links/delete-folder-and-contents/{id+}/", 
                "select": "single multiple", 
                "rel": "edit"
              }
            ], 
            "self": {
              "uri-template": "/features/folder/{id}/"
            }, 
            "create": {
              "uri-template": "/features/folder/form/"
            }, 
            "update": {
              "uri-template": "/features/folder/{id}/form/"
            }
          }
        }
      ]
      "generic-links": [
        {
          "title": "Copy", 
          "uri-template": "/features/generic-links/links/copy/{id+}/", 
          "rel": "edit", 
          "method": "POST", 
          "select": "multiple single",
          "models": [
            "features_folder", 
            "features_mpa", 
            "features_renewableenergysite"
          ] 
        }, 
        {
          "title": "Export KML",
          "uri-template": "/features/generic-links/links/export-kml/{id+}/", 
          "select": "multiple single", 
          "rel": "alternate", 
          "models": [
            "features_folder", 
            "features_mpa", 
            "features_renewableenergysite"
          ]
        }
      ]
    }

Root
====

The root of the workspace is a javascript object with two properties, 
``generic-links`` and ``feature-classes``.

feature-classes
***************

``feature-classes`` contains an array of objects that represent every feature
class present in the kml document. Each of these objects describe how the 
feature should be displayed, crud operations can be performed, any related 
downloads or non-standard editing operations supported.

feature-class objects
=====================

Each contain the following properties:

title
-----
The title that this feature class should be referred to within the user 
interface. The most prominent use of this property is in the "Create New" 
menu.

id
--
The unique id for this feature class. Each instance of a feature class has an
id composed of ``{class.id}_{instance.pk}``. When instances are selected in 
the user-interface, the id of it's class can be derived by matching all 
characters preceding the final underscore ``_``.

link relations
--------------
Contains a dictionary of links keyed by their ``rel`` value. Each feature 
class must have single links of ``rel`` ``self``, ``create``, and ``update``.
They can also optionally have an array of links for relations ``alternate``, 
``related`` and ``edit``.

See the Links description for more info on how links are interpreted.

generic-links
=============

``generic-links`` contains an array of all links that can apply to multiple 
models. See below for a description of how these links are interpreted.


Links
=====

Links describe a path to a service or resource and have properties that 
describe how they should be used by the client.

rel
---

The link rel attribute is modeled after 
`link relations <http://www.iana.org/assignments/link-relations/link-relations.xhtml>`_
in html. Valid options are:

  * The ``self`` link supports GET requests to fetch feature attributes, and 
    DELETE requests to well, delete it.
  * ``create`` is the path to a form that can be used to create new features.
  * ``update`` is the link to a form for editing an instance.
  * ``alternate`` links link to alternative representations of the feature, 
    such a kml or shapefile download option that should appear in the *Export*
    menu.
  * ``related`` is for links to content related to the feature that should 
    also appear in the *Export* menu.
  * ``edit`` links are added to the *Edit* menu. The value of the method 
    property will determine whether a GET request should be sent to the url to
    grab a form, or just to POST directly to the url without user interaction.

title
-----
Each link that appears in a menu must have a title. This title will be used by
the user interface to identify it to the user. Doesn't need to be specified 
for ``create``, ``self``, or ``update`` links.

uri-template
------------
Specifies the path to the link. Since these links often must be changed to 
apply to one or more instances of a feature class, templates identify how 
their properties should be added to the path. Currently the only property that
is supported for templating are feature uids.

Ideally any templates covered by the 
`uri-templates <http://tools.ietf.org/html/draft-gregorio-uritemplate-04>`_
specification would work.

.. note::
    The client only supports the forms {id} and {id+} at this time. Lets keep 
    that our little secret okay?

Example:

.. code-block:: python

    "/features/generic-links/link/copy/{id+}/" 
    # applied to two features becomes:
    "/features/generic-links/link/copy/features_mpa_1,features_folder_3/"

select
------
Specifies whether this link can be requested for a single selected feature,
multiple selected features, or 1+ features. Valid values are ``single``, 
``multiple``, ``single multiple``, or ``multiple single``.

Defaults to ``single``.

method
------
When used in combination with links with a relation of ``edit``, specifies 
whether to GET a form from this link to present to the user for editing, or to
just POST to the link.

Acceptable values are ``GET`` and ``POST``. Defaults to ``GET``.

confirm
-------
When used in combination with rel=edit and method=POST, specifies a 
confirmation message to display before performing the action.

models
------
For ``generic-links``, defines what feature classes can be accepted.

collection
----------
Indicates that this is a FeatureCollection subclass, and can have other 
Feature and/or FeatureCollection instances nested under it. This is an object
containing the following properties:

  * ``valid-children``: a list of Feature classes that can be nested within 
    it.
  * ``add-uri-template``: uri-template to send a POST request to when adding 
    features to this collection.
  * ``remove-uri-template``: for removing features.
