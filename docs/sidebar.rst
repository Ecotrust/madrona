.. _sidebar:

Authoring Sidebar Content
=========================

Most of the information in MarineMap is exposed via panels displayed in the 
sidebar. While the layout of the home tabs is mostly fixed, dynamic loading of
content within sidebar panels provides many options for extensibilty. The 
content and behavior of these panels can be defined entirely via server-side 
templates and :ref:`behaviors`, minimizing the amount of client-side scripting 
necessary to make information dynamic and engaging.

The following topical guide will detail how content can be added to the 
"Attributes" panel of spatial features. The details are also relevant for 
a sidebar panel created via the javascript API. If you need to create a panel
via the javascript API refer to the :ref:`rest` or 
`lingcod.common.panel <http://maps11.msi.ucsb.edu/marinemap-docs/jsdocs/symbols/lingcod.panel.html>`_
documentation.

Information Architecture
************************

The primary pathway for users to find information is to select a feature, then 
view that feature's attributes. The attributes panel for a feature can be at 
it's simplest a single page. More commonly though, content will be divided 
into seperate tabs.

By convention the first tab should contain metadata-type information like the
feature author and creation date. It should contain additional information, 
but an effort should be made to load this content quickly so do not include 
any long-running reports. Other tabs can hold this type of information and 
should be loaded asynchronously once the user clicks on them.

Each tab can also have sub-tabs, but this hierarchy is limited to just two 
levels deep for simplicity's sake. These sub tabs have been used to split the 
same report data into a data visualization tab and a data grid tab. 

Configuring Templates
*********************

a simple panel
--------------

Lets start with a simple example of a feature with a tab-less attributes 
panel. You'll first need find (or create) the template used to render 
attributes for the feature class of interest. In the case of :ref:`mpas`, this 
template can be found in ``<your_project>/templates/mpa/show.html``.

.. code-block:: django

    {% extends 'common/panel.html' %}
    {% block title %}{{instance.name}}{% endblock title %}
    {% block panel %}
        <h1>{{instance.name}}</h1>
        <p>{{instance.description}}</p>
    {% endblock panel %}

This most basic of templates is extending ``common/panel.html``, defining some
basic markup, and setting the title of the page. It is important to extend the
base template so that client-side modules can correctly parse your content. 

.. note::

    What if your view template doesn't extend ``common/panel.html``? 
    It should. This will improve consistency and in the future we can make 
    enhancements to simultaneously provide both panel content and print pages.
    Extending ``common/panel.html`` will also enable analytics on ajax content 
    in the future. If it's not possible to extend this template, you will have 
    to ensure that your view returns an html fragement 
    (as opposed to a whole document), with a single top-level div containing 
    all content.

.. _sync_tabs:

synchronous tabs
----------------


To add multiple tabs to this sidebar panel we have to add more markup:

.. code-block:: django

    {% extends 'common/panel.html' %}
    {% block title %}{{instance.name}}{% endblock title %}
    {% block panel %}
        <h1>{{instance.name}}</h1>
        <div class="tabs">
            <ul>
                <li><a href="#Attributes"><span>Information</span></a></li>
                <li><a href="#Report"><span>Report</span></a></li>
            </ul>
            <div id="Attributes">
                <p>....</p>
            </div>
            <div id="Report">
                <img class="chart" href="..." />
                <p>....</p>
            </div>
        </div>
    {% endblock panel %}

This example would create two tabs, one named "Information" and the other 
"Report". A list above references div tags with appropriate anchor links to 
form navigational elements. The MarineMap client modules will parse this 
markup and javascript event listeners to manage user interaction. This will 
only work if the markup is correct and the container div has a ``tabs`` class.

Notice that no header tags are defined within the content divs. The tabs 
themselves will serve as headers.


.. _async_tabs:

asynchronous tabs
-----------------

In the previous example the content for both tabs is available immediately 
without doing any ajax calls because the tab contents are defined within one
template. If the Report tab requires a lot of processing it may slow down 
access to the "Information" tab.

.. code-block:: django

    {% extends 'common/panel.html' %}
    {% block title %}{{instance.name}}{% endblock title %}
    {% block panel %}
        <h1>{{instance.name}}</h1>
        <div class="tabs">
            <ul>
                <li><a href="#Attributes"><span>Information</span></a></li>
                <li><a href="/path/to/report/"><span>Report</span></a></li>
            </ul>
            <div id="Attributes">
                <p>....</p>
            </div>
        </div>
    {% endblock panel %}

In this example we've simply removed the tab content div for "Report" and 
changed to url from an anchor link to one that points to a separate view. When 
the user clicks on that tab the view will be fetched and displayed within the 
panel.

The markup of the "Report" template can either be a simple panel or contain
synchronous and/or asynchronous tabs. Just be sure to limit the tabs to
two levels deep. The client-side tab handling will break down (purposely) for
anything more extensive.

.. code-block:: django

    {% extends 'common/panel.html' %}
    {% block title %}{{instance.name}} Report{% endblock title %}
    {% block panel %}
        <img class="chart" href="..." />
        <p>...</p>
    {% endblock panel %}

This is a simple example but it could also look more like the asynchronous 
tabs example above to create sub-tabs.

tab behavior when switching features
------------------------------------

Sidebar panels have the ability to "sync" with each other when the selected
spatial feature is changed. If a user has drilled down into sub-tabs for a 
particular feature, then without closing the panel selects another feature on
the map, those same tabs will be selected within the new content.

If this feature is not working properly make sure that the tab names 
(set in div.tabs > ul > li > a > span) match.

Inline <style> and <script> Tags
********************************

One way to style or alter the behavior of sidebar content is to add 
:ref:`project_assets` in ``settings.py``. These will load when
the application is first starts and is the best solution for including large 
libraries of code like a charting library or external dependency. It doesn't 
work that well for small snippets that only apply to sidebar content though.

For custom css and javascript that is tied to a specific panel, it's easier to 
implement and organize this code as inline tags within the panel template.

css
---

Style tags are very easy to include. The following will work perfectly well:

.. code-block:: django

    {% extends 'common/panel.html' %}
    {% block title %}{{instance.name}} Report{% endblock title %}
    {% block panel %}
    
        <style id="chartStyle" type="text/css" media="screen">
            .chart {
                border: solid black 1px;
            }
        </style>
    
        <img class="chart" href="..." />
        <p>...</p>
    {% endblock panel %}

.. warning::
    Be careful how you use css. Scope styles down to unique id or class names
    so that they don't interfere with application-wide styles. Sidebar content
    is not sandboxed in any way so if you set ``p {margin-left:50px}`` it will
    ruin the layout of the entire application.

There is one nuance to pay attention to here. Sidebar content is likely to be
loaded multiple times. The MarineMap client-side modules will add any new 
style tags it finds to the page when sidebar content is rendered, but this 
could end up creating a lot of redundant tags. In this example, the style tag 
has an ID attribute of ``chartStyle``. This ID could be any value, and 
MarineMap will check if a panel includes style tags with an ID. If another 
style tag with this ID is already in the document, it will be ignored. 

It is highly recommended that you include ID attributes in style tags to 
reduce the number of style tags added to the main document.

The MarineMap client modules will handle multiple style tags in sidebar 
content, which can be useful for dynamic css. Say you have some generic styles
that apply to all panels that a view renders, but there are also some dynamic
styles that need to be added to the document each time. A solution is to 
provide the generic css rules as a style tag with an ID attribute and the 
dynamic rules in a separate tag:

.. code-block:: django


    {% extends 'common/panel.html' %}
    {% block title %}{{instance.name}} Report{% endblock title %}
    {% block panel %}

        <!-- generic rules, added to the document only once -->
        <style id="chartStyle" type="text/css" media="screen">
            .chart {
                border: solid black 1px;
            }
        </style>
        
        <!-- dynamic css rules, no ID attribute -->
        <style type="text/css" media="screen">
            #{{instance.div_id}} {
                background-color: #{{instance.color}};
            }
        </style>
        
        <img class="chart" href="..." />
        <span id="{{intance.div_id}}">{{instance.name}}</span>
        <p>...</p>
    {% endblock panel %}

When a panel is opened multiple times and for different features, the first 
style tag will only ever be added to the document once while the second tag 
will be added to the document every time a panel is opened.

inline javascript
-----------------

Inline javascript is supported through the setting of callback functions on 
the sidebar panel. You should only execute javascript within the scope of a 
callback function. If not, your javascript will execute at unpredictable 
times, possibly before the sidebar panel content is added to the document.

.. warning::
    
    It's worth repeating -- execute all of your javascript within a callback 
    function!

Here is a simple example of a callback that will run as soon as the panel 
content is rendered and shown to the user. It will execute only once:

.. code-block:: html

    {% extends 'common/panel.html' %}
    {% block title %}{{instance.name}}{% endblock title %}
    {% block panel %}
        
        <script type="text/javascript" charset="utf-8">
            
            lingcod.onShow(function(){
                $('p.description').click(function(){
                    alert('clicked description');
                });
            });
            
        </script>
        
        <h1>{{instance.name}}</h1>
        <p class="description">{{instance.description}}</p>
    {% endblock panel %}

Notice how in the example callback jQuery was used. jQuery is loaded as part 
of the main application and can be used in sidebar content along with other
:ref:`built_in_js`.

using inline javascript with tabs
---------------------------------

:ref:`onShow <lingcod.onShow>` callbacks can also be scoped to particular tabs 
when using :ref:`sync_tabs` by providing the anchor link a tab points to:

.. code-block:: html

    {% extends 'common/panel.html' %}
    {% block title %}{{instance.name}}{% endblock title %}
    {% block panel %}
        
        <script type="text/javascript" charset="utf-8">
            
            lingcod.onShow('#Report', function(){
                alert('you are viewing the report tab');
            });
            
        </script>
    
        <h1>{{instance.name}}</h1>
        <div class="tabs">
            <ul>
                <li><a href="#Attributes"><span>Information</span></a></li>
                <li><a href="#Report"><span>Report</span></a></li>
            </ul>
            <div id="Attributes">
                <p>....</p>
            </div>
            <div id="Report">
                <img class="chart" href="..." />
                <p>....</p>
            </div>
        </div>
    {% endblock panel %}

That example makes sense for synchronous tabs, but what about 
:ref:`async_tabs`? It makes more sense organization-wise to have inline style 
and javascript tags within the template that renders the tab content. Making 
an :ref:`onShow <lingcod.onShow>` call with a url as the target argument will 
not work. This is how we would implement the previous example for an 
asynchronous report:

.. code-block:: html

    <!-- first template -->
    {% extends 'common/panel.html' %}
    {% block title %}{{instance.name}}{% endblock title %}
    {% block panel %}
        
        <h1>{{instance.name}}</h1>
        <div class="tabs">
            <ul>
                <li><a href="#Attributes"><span>Information</span></a></li>
                <li><a href="/path/to/view/"><span>Report</span></a></li>
            </ul>
            <div id="Attributes">
                <p>....</p>
            </div>
        </div>
    {% endblock panel %}

.. code-block:: html

    <!-- template at /path/to/view/ -->
    {% extends 'common/panel.html' %}
    {% block title %}{{instance.name}} Report{% endblock title %}
    {% block panel %}
        
        <script type="text/javascript" charset="utf-8">
            
            lingcod.onShow(function(){
                alert('you are viewing the report tab');
            });
            
        </script>
    
        <img class="chart" href="..." />
        <p>...</p>
    {% endblock panel %}

Note that the remote tab template uses an :ref:`onShow <lingcod.onShow>` call 
without the target argument. The callback will still be assigned to the 
appropriate tab. 

.. _target_or_not:

.. note::
    Just remember that when assigning callbacks to synchronous tabs you must 
    provide the target argument to scope it to that tab. Callbacks bound to 
    whole panels or asynchronous tabs do not need to be set with this argument

available callbacks
-------------------

You can do more than assign callbacks for when a tab or panel is first shown. 
You can also run javascript whenever content is temporarily hidden, revealed, 
or right before it is permanently removed from the document.

.. warning::
    The implementation of this functionality in trunk diverges from the 
    documentation right now. Expect the API to work as documented here by 
    milestone 1.1

.. _lingcod.onShow:

lingcod.onShow([target], callback)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assigns a callback to be executed when content is first shown. It will be 
executed only once. See :ref:`lingcod.onUnhide <lingcod.onUnhide>` to assign
callbacks whenever content is shown again after being hidden.

If binding the callback to a synchronous tab, give that tab's anchor link as 
the optional ``target`` argument. Omit it if assigning the callback to the 
entire panel or an asynchronous tab. 
:ref:`More on this argument <target_or_not>`.

.. _lingcod.onHide:

lingcod.onHide([target], callback)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assigns a callback to be executed whenever content in a tab is hidden from the
user because another tab or sub-tab has been opened.

If binding the callback to a synchronous tab, give that tab's anchor link as 
the optional ``target`` argument. Omit it if assigning the callback to the 
entire panel or an asynchronous tab. 
:ref:`More on this argument <target_or_not>`.

.. _lingcod.onUnhide:

lingcod.onUnhide([target], callback)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Callback will be executed whenever content is revealed to the user, even after
hiding. It *will* be executed when content is first shown as well, right after
any :ref:`onShow <lingcod.onShow>` callbacks.

If binding the callback to a synchronous tab, give that tab's anchor link as 
the optional ``target`` argument. Omit it if assigning the callback to the 
entire panel or an asynchronous tab. 
:ref:`More on this argument <target_or_not>`.

.. _lingcod.beforeDestroy:

lingcod.beforeDestroy(callback)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Callbacks will be executed before content is removed from the document when
a user closes the panel or it is closed by an API call. There is no need to 
provide a ``target`` argument, the whole panel with tabs is destroyed at once.
    
.. _behaviors:

Built-In Behaviors and Styles
*****************************

By using special markup within sidebar content you can take advantage of 
built-in widgets to implement dynamic behavior without having to resort to 
inline style and script tags. This reduces the workload for incorporating new
content and provides users with a more consistent user interface.

The following is a list of the built-in behaviors you can take advantage of in
sidebar content.

links
-----

Links with a class of ``panel_link`` will open the specified view within the
same sidebar, replacing the current content. This functionality is used in 
:ref:`news`. 

Be sure to think about navigation when using this functionality. Content 
loaded via these links will probably need a "back button" link with the 
``panel_link`` class to open the previous page.

Example markup:

.. code-block:: html

    <a class="panel_link" href="/path/to/panel/content/">my link</a>

data grids
----------

``todo``

data visualization
------------------

``todo``

linking to related spatial features
-----------------------------------

``todo``

turning on data layers
----------------------

``todo``

controlling map state
---------------------

``todo``

.. _built_in_js:

built-in javascript libraries
-----------------------------

These libraries are included in the main application and can be used within 
sidebar content.

  * `jQuery <http://jquery.com/>`_

Providing Print Links
*********************

``todo``

Integration with Google Analytics
*********************************

``todo``
