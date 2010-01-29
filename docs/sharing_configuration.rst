.. _sharing_configuration:

Sharing MPAs and Arrays between Users
======================================

Introduction
***************************
The lingcod.sharing app is a django application that allows for the sharing of arbitrary django model instances between groups. The most common use case would be: A user creates an MPA and wants others to comment on it. This user is a member of several groups. They can choose to share (make available read-only) their MPA to any one of the groups which has MPA sharing permissions. 

.. note::
    Though the lingcod.sharing app is configured to be a generic django-object sharing app,
    we'll use the example of Marine Protected Areas (MPA) and Arrays as it is the primary use case 
    and is the only one we've really implemented and tested on. 

Setup
**********************
In order to make content shareable through the lingcod.sharing app, a number of requirements must be met in the django model.
 
    * model Meta must expose a can_share* permission
    * model must have a 'user' field denoting ownership (Foreign Key to Users)
    * model must have a 'sharing_groups' (ManyToMany field to Group)
    * managers must implement the all_for_user() method (ie the model must have object = ShareableGeoManager() or manager which inherits it)
    * model's content type is registered as a ShareableContent instance

All but the last step are built into lingcod for MPAs and Arrays. Because content_types primary keys are not consistent across deployments, we can't really add fixtures for this. But it is simple enough to go into /admin/sharing/shareablecontent/ and add the MPA and array content types. 

Additionally,to make sharing functional, you must have one or more groups with the can_share* permission and have some users belonging to those groups.

Containers
**********************
The sharing app also has the concept of sharing "containers" - shareable objects which imply that the objects "contained" within them are also implicitly shared. For example, MPAs belong to an Array container so that when an Array is shared, all MPAs contained by that Array appear as shared (whether the MPA objects themselves are individually shared or not).

In order to so this, the container field in shareablecontent must point to the appropriate content_type AND a property on the container model which returns a queryset of all contained objects must be specified. For example, Arrays contain a property called 'mpa_set' which returns a queryset of all MPAs belonging to that array. The string 'mpa_set' must be specified in the shareablecontent in order to define the relationship between container and contained. Finally, the container content type must also be registered as shareablecontent. 

Sharing UI
***********
The sharing app provides a form and views for editing an object's sharing status. A GET request to /sharing/<content_type_id>/<object_pk> will give access to this form (assuming that content_type is shareable), while a POST request to the same URL with the groups parameter specified will attempt to share the object with the specified groups. Appropriate error messages and status response codes are used and will hopefully be helpful and smooth things over in the case of errors.   

Using the sharing functionality
********************************
Once the models have been configured for sharing, the application or project must implement the handling of the shared content. For instance, the default MarineMap interface implements atom links and UI components which allow sharing to be configured on each object and KML representations of shared objects. The sharing app provides a number of helpful hooks for implementing these types of functionality.

    * The all_for_user() method on the shared object's manager allows you to get a set of objects that have been shared to the given user but are owned by other users. 
    * The get_shareables() function which exposes all the objects in the current project which are shareable (ie meet all of the sharing requirements listed in Setup)
    * The share_object_with_group() and share_object_with_groups() functions which provide a safe shortcut to the actual sharing
    * The groups_users_sharing_with() function which returns the groups and users which are currently sharing objects with a given user. 
    * The get_content_type_id() function which is just a conveinience shortcut for determining the content_type of a given model class. 

You can look at the kmlapp.views.get_mpas_shared_by and kmlapp.views.create_shared_kml for an example of how sharing code can be used by another application.
