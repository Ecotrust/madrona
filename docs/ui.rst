.. _ui:

User Interface
==============

What you can do
***************

MarineMap's UI framework makes it easy to create an application that looks 
good and behaves consistently without having to write lots of javascript or 
css. Using a combination of standard styles, templatetags, and simple 
javascript shortcuts, one should be able to:
    
* Work new pages into the One-Window Drilldown panel and access them via simple links
* Define panel pages that have complimentary printable and hyperlink-able pages
* Maintain a consistent appearance across the following types of content
    * block content such as headings, footers, lists, etc
    * forms
    * custom javascript tools
* Create histograms and other data visualizations for use in reports
* Include static maps of Marine Protected Areas and Arrays via template tags

design philosophy
-----------------

* Default stylesheets should produce a pleasing and consistent look when applied to simple markup.
* Stylesheets should specifically target markup produced by the django APIs such as `forms <http://docs.djangoproject.com/en/dev/topics/forms/>`_.
* Complex markup, like linking to a static map in a template, should be made easy via custom `template tags <http://docs.djangoproject.com/en/dev/ref/templates/builtins/>`_.
* Where effects such as rounded corners or drop shadows are desired, css3 should be used. Markup should not be complicated to support older browsers to marginally improve aesthetics.
* Great pains should not be made to replace native form widgets and buttons to be consistent across browsers. There is nothing wrong with a native look and feel.
* It is better to create an awesome tool that works on most browsers than a less useful one that works on all of them.
* It's not always better for a web application to behave like a desktop one.

.. _map_view:

The Map View
************

The MarineMap application interface consists primarily of a map view coupled
with a sidebar implementing the `One-Window Drilldown <http://www.time-tripper.com/uipatterns/One-Window_Drilldown>`_
pattern. It imposes a limit to the amount of information that can
be presented in a single view, but also allows for more information to be 
exposed via links without overwhelming novice users. One goal of using this UI
pattern is to reduce the cognitive overhead of managing multiple drag-able 
windows.

home panel
----------
The home panel is multi-tabbed, consisting of a set number of categories. 
Links and content can be added to these tabs using template blocks such as
`tools`, `data_layers_footer`, `after_my_shapes`, etc.

It's not intended that implementation of MarineMap can easily add tabs or 
make drastic modifications to the home screen. This interface should remain 
fairly consistent across projects.

creating new panels
-------------------

To create a new panel, you must create a url, view, and template to render 
your content via django. Within the template, you have access to template tags
to help style your content. Template tags are used rather than special classes
or markup structures because they can be hard to remember. Changes to 
presentation or additional features may also require a change in markup 
sometime in the future.

.. _example_panel:

example panel
^^^^^^^^^^^^^

.. code-block:: django

    {% extends 'common/panel.html' %}
    {# Load all the tags seen here (printable, panel, etc) #}
    {% load layout_tags %}
    
    {% printable %}
    {% home_link %}
    
    {% block panel %}
        {% panel "My Title" %}
            {% footer %}
                <h3>I am a header for the footer</h3>
                <p>
                    Blah blah footer...
                </p>
            {% endfooter %}
        {% endpanel %}        
    {% endblock %}

Note the :ref:`tag_printable` tag for specifying a link to the page-based view, and
the :ref:`tag_home_link` tag for specifying where the back button should lead.

example tabbed panel
^^^^^^^^^^^^^^^^^^^^

.. code-block:: django

    {% extends 'common/panel.html' %}
    {% load layout_tags %}
    
    {% url mpa_attributes mpa.pk as backurl %}
    {% back_link "Back to MPA Attributes" backurl "Attributes" %}
    {# "Attributes" is the title of the tab that will be displayed #}
    
    {% block panel %}
        {% tabpanel "My Tab Panel" %}
            {% tab "My Tab One" %}
                <p>Tab one content</p>
            {% endtab %}
            {% tab "My Tab Two" %}
                <p>
                    Tab two content
                </p>
                {% footer %}
                    <h3>My footer</h3>
                    <p>...</p>
                {% endfooter %}
            {% endtab %}
        {% endtabpanel %}
    {% endblock %}            

See documentation for all template tags here: :ref:`templatetags`

showing the panel
-----------------

Show panels by linking to them from other panels.

.. code-block:: django

    {# Link will slide in from the right #}
    <a href="{% url new_mpa %}" class="forward" title="Create a Marine Protected Area">create mpa</a>

    {# Link will slide in from the left, as if returning to the previous panel #}
    <a href="{% url mpa_attributes mpa.pk %}" class="backward" title="back to attributes">create mpa</a>
    
    {# Link will appear without any implied spatial relationship to the current panel #}
    {# Switch is currently not implemented #}
    <a href="{% url wave_detail wave.pk %}" class="switch" title="view discussion">create mpa</a>

how panels are reloaded
-----------------------

As a user moves to the right, opening more and more panels, they build up a 
trail of panels that are hidden to the left. If they hit the back button, 
those panels are brought back up, as they were when first seen. Panels that 
are hidden to the right are actually removed and can be considered closed. If 
a user travels back to that panel it is refreshed from the server.

In order to refresh all panels, the javascript api should be used *(not 
implemented)*.

.. code-block:: javascript

    lingcod.refreshPanels();


adding javascript to a panel
----------------------------

*Not implemented*. Some sort of api here like this:

.. code-block:: javascript

    <script>
        lingcod.onPanelShown(function(){
            // initialize some widgets
            // ...
            // setup event listeners.
        });
        
        lingcod.onPanelHide(function(){
            // deactivate some widgets to improve performance
        });
        
        lingcod.onPanelUnhide(function(){
            // re-enable components
        });
        
        lingcod.onPanelDestroy(function(){
            // permanently remove widgets, avoid memory leaks
        });
    </script>


Linking to other Pages
**********************

To open a link in a new window or the current window, set the link target to 
`_self` or `_blank`.

complimentary printable pages for panels
----------------------------------------
*Not Implemented*. Use the :ref:`tag_printable` template tag as seen in the 
:ref:`example_panel`.