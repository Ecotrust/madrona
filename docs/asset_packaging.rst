Javascript and CSS Assets
=========================

Packaging
*********

It's difficult to maintain a large web application without breaking the 
javascript and css components into multiple files. The problem with this 
approach is that http requests are costly and loading many css and js files 
increases the loading time of the app.

MarineMap utilizes the `django-compress <http://code.google.com/p/django-compress/>`_ 
app not only to concatenate these files but compress them by removing 
comments and whitespace.

Where to put files
******************
Each django app in the ``lingcod`` module has a folder under ``media/``, that 
contains folders for javascript, css, and images. Also there is a folder for 
external libraries called ``lib``, and a folder for testing javascript::

    media/<app-name>/
      css/
      lib/
      js/
        test/
      images/

This can of course be expanded and will likely need to incorporate a folder
for test fixtures.
      
      
How to add files to the build
*****************************
To include your files in the main javascript and css packages, you'll need to
add them to ``js_includes.xml`` and ``css_includes.xml``.

``media/css_includes.xml``

.. code-block:: xml
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!--
    	includes.xml
        List all css files that should be aggregated into the main marinemap.css
        file here. Be mindful of the order.
    -->
    <stylesheets>
        <file path="common/css/typography.css" />
        <file path="common/css/application.css" />
    </stylesheets>
    
``media/js_includes.xml``

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <!--
    	includes.xml
        Edit this file to add javascript files that need to be included in the
        main marinemap.js distribution, as well as point to appropriate tests.
        Please avoid adding third party libs where they are available from a CDN        
        like Google's ajaxlibs
    -->
    <javascripts>
        <file path="common/js/lib/tmpl.js" />
        <!-- note the inclusion of tests -->
        <test path="common/js/test/lib/tmpl.js" />
    </javascripts>

Note that this diverges significantly from the standard way one configures
`django-compress <http://code.google.com/p/django-compress/>`_. The reason for
this is that static html files can then parse these xml files and run tests
on the client code without a server running.

*Do not* include project-specific javascript and css files using this method.
For implementations of MarineMap for specific geographies, keep these files in 
a media folder in the project file tree. The `standard instructions <http://code.google.com/p/django-compress/wiki/Configuration>`_
for configuring django-compress can then be used for packaging up those files::

    COMPRESS_JS = {
        'application': {
            'source_filenames': assets.get_js_files(),
            'output_filename': 'marinemap.r?.js'
        },
        'tests': {
            'source_filenames': assets.get_js_test_files(),
            'output_filename': 'marinemap_tests.r?.js'
        },
        'mlpa-project-javascript': {
            'source_filenames': ('media/mlpa/js/foo.js', 'media/mlpa/js/bar.js'),
            'output_filename': 'mlpa_js.r?.js'
        }
    }

Including assets in your pages
------------------------------
Use the standard `django-compress <http://code.google.com/p/django-compress/>`_
template tags:

.. code-block:: django

    <head>
        <meta http-equiv="Content-type" content="text/html; charset=utf-8">
        <title>MarineMap Decision Support Tool</title>
        {% load compressed %}
        {% compressed_css 'application' %}
        {% compressed_js 'application' %}
    </head>
    <body>

Testing Javascript Code
***********************

defining unit tests
-------------------
Unit tests are defined using `QUnit <http://docs.jquery.com/QUnit>`_. Simply
create a test js file and then add a reference to it in ``js_includes.xml`` 
and it can be run using the methods defined in the following sections.

**Example unit test**

.. code-block:: javascript

    module('micro-templating')

    test("list template", function(){
        template = [
            "<ul>",
                "<% for (var i=0; i < users.length; i++) { %>",
                    "<li><%= users[i].name %></li>",
                "<% } %>",
            "</ul>"
        ];
        template = template.join("");
        list_users = tmpl(template);
        data = {users: [{name:'me'}, {name: 'myself'}]}
        equals(list_users(data), "<ul><li>me</li><li>myself</li></ul>");
    });

**Inclusion in** ``media/js_includes.xml``

.. code-block:: xml

    ...
    <file path="common/js/lib/tmpl.js" />
    <test path="common/js/test/lib/tmpl.js" />
    ...
    
testing unpackaged javascript
-----------------------------
It's possible to test the client javascript code without a running server by
simply opening ``media/tests.html``. Because it's a static file, one could even
run the tests by opening ``tests.html`` directly from the online svn repository.

This page loads all the same files that django-compress packages, but loads
each file individually and dynamically, so you don't need a server running. In
fact, one can simple browse to the svn repository and run tests from there!

`<http://marinemap.googlecode.com/svn/trunk/media/tests.html>`_

This method *will not test whether the code runs after packaging*. For that
reason it is suitable for quick use during development but cannot adequately
test code for use in a production environment.

The most likely bugs not caught without packaging are forgotten trailing 
semi-colons. Fortunately, these bugs immediately cause parse errors when 
tested using the server-side method so they are easy to catch.

testing packaged files
----------------------
In order to test that javascript code runs properly after packaging and 
compression, you'll need a running server. See :ref:`getting_started` for 
instructions on how to run the server, then point a browser to `<http://localhost:8000/tests>`_. This
will run the same tests, but using django-compress to load assets. 

*In order to test these files both concatenated and compressed you must have 
one of the following settings set*::

    COMPRESS = True

or::
    
    DEBUG = False

Testing and Documenting Reusable CSS Styles
*******************************************
``media/styles.html``