.. _flatblocks:

Managing content with flatblocks
====================================

The ``django-flatblocks`` app is installed by default. This allows you to put snippets of text into your templates which can be managed and edited 
through the admin interface.

Adding a flatblock to your template
------------------------------------

When creating a project, keep an eye out for textual content in the templates that may need revisions. These sections can be replaced with flatblock template tags::

    {% load flatblock_tags %}
    <p>{% flatblock "intro paragraph" %}</p>

Creating flatblock content
---------------------------

Through the admin interface, ``/admin/flatblocks/flatblock/``, you can add and edit the flatblocks. The only two fields we use are the slug or short description used in the template tag (e.g. "intro paragraph") and the content itself.

.. warning::
 
    Content text is delivered directly to the html template without modification. This means that you *can* insert html tags. But keep in mind you are editing a live site and any html tags have the potential to alter the layout!

Permissions
-----------

You can select certain groups and/or users who are able to add, change or delete flatblocks. Since the developers will be controlling the templates (thus inserting the templatetags and formatting them, etc.) it doesn't make sense for content managers to add or delete. 
To allow change-only permissions, go to ``/admin/auth/user/`` or ``/admin/auth/group/``, select the user or group, and add the permission ``flatblocks | Flat block | Can change Flat block``.

