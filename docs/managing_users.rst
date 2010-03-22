.. _users:

Managing Users in MarineMap
===========================

users
*****
Users can be added in one of two ways:

    * Staff/Superuser can add the user manually through the admin interface.
    * Users can register themselves via web registration.

web registration
----------------
The web registration framework allows users to add themselves to an instance of MarineMap. After supplying the necessary info, an inactive user will be created and an email sent to the given email address. To activate the account, the user must visit the url contained in the email. At this time, user's can not add themselves to groups; that process requires moderator/admin approval and will be handled by email. 

All users registering through the web interface will be assigned to the group defined in settings.GROUP_REGISTERED_BY_WEB ('registered_by_web' is the default). This allows staff to track which users registered themselves versus were added manually. 

user profiles
-------------
Each user has access to a 'my profile' page where they are able to view and edit:

    * First and last name
    * Email address
    * About - and other additional fields extending the user information
    * Password
    * Their groups (read-only)

groups
******
Django groups are a convinient way to batch-assign permissions to many users. In MarineMap, groups have another function: they serve as the organizing unit for sharing of MPAs and Arrays. With a few exceptions, being a member of a group means that you can share your arrays with other group members and vice-versa. 

There are also two special groups which are exceptions: 
    * Share to public : Members of this group can make an array available to all users including non-authenticated users.
    * Share to staff : Members of this group can submit an array to the staff for approval; Only staff is able to view them but all group members can submit.

Access to the admin interface is not determined by groups; a special 'is_staff' field can be set on a per-user basis. 

permissions
***********
Permissions, in general, define who can add/edit/delete various objects in the admin interface. Currently we don't use this fine-grained permsission set, instead relying on the staff field for each user to allow unfettered access to the admin interface. 

There are several permissions related to sharing that can be useful if set on groups. For example can_share_mpas and can_share_arrays allow that group's members permission to share the specified object with one another. See :ref:`Sharing<sharing_configuration>` documentation for more detail.
