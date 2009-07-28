.. _templatetags:

Built-in Template Tags
======================

footer
^^^^^^
Creates a footer section that will be attached to the very bottom of the panel
and appropriately styled.

.. code-block:: django
    
    {% footer %}
        This is <i>my</i> footer content
    {% endfooter %}


panel
^^^^^
Creates a content block that represents a "panel". A panel can be rendered 
both in its own page or within :ref:`map_view`.

Accepts one argument, the name of the panel. This will show up in the 
header, and can be a string(quoted) or a context variable.

.. code-block:: django

    {% panel "My Panel is Awesome" %}
        <p>Here are the reasons why:</p>
        <ul>...</ul>
        {% footer %}
            Notice I place the footer within panel tags
        {% endfooter %}
    {% endpanel %}


tabpanel
^^^^^^^^
Alternative to `panel <#panel>`_. Works in conjunction with `tab <#tab>`_ tags 
to create tabbed navigation within a single panel.

Accepts one argument, the name of the panel. This will show up in the
header, and can be a string(quoted) or a context variable.


tab
^^^
Defines a block of content that renders within it's own tab.

Accepts one argument, the name of the tab. This will show up in the tab
navigation element, and can be a string(quoted) or a context variable.

.. code-block:: django

    {% tabpanel "My TabPanel" %}
        {% tab "First Tab" %}
            <p>...</p>
        {% endtab %}
        {% tab "Second Tab" %}
            <p>...</p>
            {% footer %}
                Optional footer...
            {% endfooter %}
        {% endtab %}
    {% endtabpanel %}


.. _printable:

printable
^^^^^^^^^
Indicates that this panel should have a complementary page linked from the
panel, with a style suitable for printing and direct linking.

.. code-block:: django
    
    {% printable %}


.. _back_link:

back_link
^^^^^^^^^
Required for proper operation, this tag creates the link to go back to it's 
"parent". Note, this does not have to be the last panel shown. It could be
that the previous linked to this panel via a "switch" animation.

Accepts the same arguments as the built-in `url tag <http://docs.djangoproject.com/en/dev/ref/templates/builtins/#url>`_,
or a quoted string that represents the title of a tab on the home panel.

.. code-block:: django

    {% back_link mpa_attributes mpa.pk %}
    
    {% back_link "Data Layers" %}


.. _home_link:

home_link
^^^^^^^^^
Can be used rather than :ref:`back_link` for linking directly to the home 
panel.