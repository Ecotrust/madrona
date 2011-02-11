.. _sharing_configuration:

Sharing Features and Collections
================================

Introduction
***************************
Users can create Features and FeatureCollections, perform analyses on them, etc. But the ability for the user to share these ideas to various groups is where the true collaborative value lies.

The most common use case would be: A user creates a Feature and wants others to comment on it. This user is a member of several groups. They can choose to share the Feature (i.e. to make the feature available read-only) to any one of the groups which has sharing permissions. If a user decides to organize their Features into FeatureCollections, those collections can be shared as well.

The rules are as follows:
    * Any user can create any type of Feature or FeatureCollection. 
    * All Features and FeatureCollections are shareable.
    * If a user belongs to a group or groups with sharing permissions, they can share any of their features to those groups.
    * If a user organizes their features into collections and shares those collections, all features in the heirarchy are implictly shared.

Out-of-the-box Setup
*********************
By default, new users are not assigned to any groups nor are groups assigned sharing permissions. Adding a user to a group is currently not automated and requests for group memebership must be made directly to the site administrator.

Groups can be given sharing permissions through the admin interface

    * Navigate to Home › Auth › Groups 
    * Select the Group
    * Add the 'auth | group | Can Share Features' permission

Or through python::

    from lingcod.common.utils import enable_sharing
    from django.contrib.auth.models import Group

    mygroup = Group.objects.get(name="My Group")
    enable_sharing(mygroup)

Collections
**********************
Consider the following heirarchy of Features/FeatureCollections::

            folder1
             |-array1
               |-pipeline
               |-mpa1

If a user were to share folder1, array1, pipeline and mpa1 would all implicitly be shared as well. Even if mpa1 were explicitly unshared, it would still be viewable by group members by virtue of it's belonging to array1 (which in turn belongs to folder1 which is shared).

Sharing UI
***********
The sharing app provides a form and views for editing an object's sharing status. The url for a feature can be determined by::

    url = Folder.get_options().get_share_form(folder1.pk)
    # /features/folder/1/share/

A GET request to this URL will give access to this form (assuming that a user with the appropriate permissions is logged in), while a POST request to the same URL with the sharing_groups parameter specified will attempt to share the object with the specified groups. Appropriate error messages and status response codes are used and will hopefully be helpful and smooth things over in the case of errors.   

Using the sharing functionality
********************************
This section describes the various components of the lingcod API related to sharing.

First, there is the object manager which allows you to quickly obtain a queryset of all objects that have been shared with a user::

    from myapp.models import MyFeature
    features = MyFeature.objects.shared_with_user(user1)

The groups_users_sharing_with() utility function returns the groups and users which are currently sharing feature instances with a given user::

    from lingcod.features import groups_users_sharing_with
    sharing_with_me = groups_users_sharing_with(user1)

To find out which groups a user can potentially share with, use the user_sharing_groups() utility function::

    from lingcod.features import user_sharing_groups
    my_sharing_groups = user_sharing_groups(user1)

A common use case will be to determine if an object is readable by a user. In other words, is the object owned by OR shared with a given user. You can use the is_viewable() Feature method which returns two items: A boolean indicating if the user has read access and an appropriate HttpResponse object. It's up to the implementation whether or not you return the HttpResponse or not but the common scenario would be to check if the object were readable by the user and, if not, return the HttpResponse. For example::

    def some_view(request, pk):
        feature1 = get_object_or_404(MyFeature, pk)

        viewable, response = feature1.is_viewable(request.user)
        if not viewable:
            return response
        else:
            do_stuff()

In order to control sharing of an object with a given group using python code, you can use the share_with Feature method::

    feature1 = MyFeature.objects.create(name="Feature 1")
    # By default this overrides all previous sharing groups
    feature1.share_with(mygroup)
    # You can choose to append it
    feature1.share_with(mygroup, append=True)
    # You can also pass a list of groups
    feature1.share_with([group1,group2])
    # To remove all sharing groups, pass None
    feature1.share_with()


Special Cases
******************

The sharing app provides two groups which are handled differently in that the sharing is one-way:
    * Share with Public : Allows selected staff members the ability to make an object available to the public. This means everyone, including non-authenicated users, can view it but only the short list of staff members can actually make it available. 
    * Share with Staff : Allows selected users the ability to share objects with staff. Only staff can view the shared objects but any user in this type of group can submit something.

The groups which belong to these cases are defined by a list of group names in the settings by:
    * settings.SHARING_TO_PUBLIC_GROUPS
    * settings.SHARING_TO_STAFF_GROUPS

Just like any other sharing group, these groups must exist and have the appropriate permissions. The only difference with normal bi-directional sharing is that the viewing of shared object is more tightly controlled (in the case of sharing to staff) or the viewing is made available to anyone (in the case of sharing to public). Other than that, they are shared to the specified groups in the exact same way.
