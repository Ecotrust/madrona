.. _layer_manager:

``madrona.layer_manager`` 2D Data Layer Management
====================================================

This document outlines data layers are handled in 2D/OpenLayers versions of Madrona. 

Server side data model
**************************
The data layers are configured through django models: `layer_manager.model.Layer` and `layer_manager.model.Theme`. 

Layers describe a 2D data source from one of the following sources:

* XYZ tiles
* WMS
* Geojson
* UTFGrid json

These can be organized into one or more Themes. 

All configuration can be done through the django admin interface at `/admin/layer_manager/`. If you want to load up the full catalog of data layers found in the demo, there is a fixture which can be loaded::

    python manage.py loaddata base_layers

Client side elements
*************************
The client side of the layer_manager app includes five UI elements that can be added to the page:

* `data` list; Accordion-style list of themes and layers
* `search` box; Allows type-ahead search of all data layers
* `active` list; opacity, z-layer and visibility controls for active layers
* `legend`: legend images for active layers
* `description`: brief abstract of selected info layer

Client side configuration
**************************
In order to incorportate the nice 2D layer management interface, you'll need to follow some simple setup guidelines on the client side.

The functionality depends on OpenLayers, Bootstrap, jQuery and knockout.

Include the css::

    <link href="{{MEDIA_URL}}common/bootstrap/css/bootstrap.css" rel="stylesheet">
    <link href="{{MEDIA_URL}}common/css/jquery-ui.css" rel="stylesheet" type="text/css" media="all" />
    <link href="{{MEDIA_URL}}common/css/ui.theme.css" rel="stylesheet" type="text/css" media="all" />
    <link href="{{MEDIA_URL}}common/js/theme/default/style.css" rel="stylesheet" type="text/css" media="all" />

Include the required javascript sources::

    <script type="text/javascript" src="{{MEDIA_URL}}common/js/jquery.min.js"></script>
    <script type="text/javascript" src="{{MEDIA_URL}}common/js/jquery-ui.min.js"></script>
    <script type="text/javascript" src="{{MEDIA_URL}}common/bootstrap/js/bootstrap.min.js"></script>
    <script type="text/javascript" src="{{MEDIA_URL}}common/js/knockout-2.0.0.js"></script>
    <script type="text/javascript" src="{{MEDIA_URL}}common/js/knockout.mapping-latest.js"></script>
    <script type="text/javascript" src="{{MEDIA_URL}}common/js/jPaq.min.js"></script>
    <script type="text/javascript" src="{{MEDIA_URL}}common/js/amplify.min.js"></script>
    <script type="text/javascript" src="{{MEDIA_URL}}common/js/json2.js" charset="utf-8"></script>
    <script type="text/javascript" src="{{MEDIA_URL}}common/js/OpenLayers.js"></script>

Create an OpenLayer.Map object::

    <script> 
        var map = new OpenLayers.Map({
            div: "map",
            projection: "EPSG:900913",
            displayProjection: "EPSG:4326",
            controls: [
                new OpenLayers.Control.Navigation(),
                new OpenLayers.Control.Zoom(),
                new OpenLayers.Control.Attribution()
            ],
            minZoomLevel: 3,
        });

        var terrain = new OpenLayers.Layer.XYZ( "Base Map", { /* must have one base layer here */});
        map.addLayers([terrain]);  // must have at least one base layer
    </script>

And add the elements of the user interface to your page using `include` tags::

    <div>{% include "layer_manager/active.html" %}</div>
    <div>{% include "layer_manager/legend.html" %}</div>
    <div>{% include "layer_manager/search.html" %}</div>
    <div>{% include "layer_manager/data.html" %}</div>
    <div>{% include "layer_manager/description.html" %}</div>

Finally, and most importantly, you must set up a global javascript namespace, load the layer_manager javascript files and bind the viewModel to the entire DOM::

    <script type="text/javascript">
        var app = {
            viewModel: {},
            utils: {},
            updateUrl: function() { /* change url hash */ },
        };
    </script>
    <script src="{{MEDIA_URL}}layer_manager/js/map.js"></script>
    <script src="{{MEDIA_URL}}layer_manager/js/models.js"></script>
    <script src="{{MEDIA_URL}}layer_manager/js/load.js"></script>
    <script src="{{MEDIA_URL}}layer_manager/js/knockout-bindings.js"></script>
    <script src="{{MEDIA_URL}}layer_manager/js/demo_fixture.js"></script>
    <script>
        $(document).ready(function () {
            ko.applyBindings(app.viewModel);
            app.utils.initMap(map);
            app.viewModel.layers.loadLayersFromServer(); 
        });
    </script>

Example interface
***************************
See `layer_manager/templates/layer_manager/demo.html` for a minimal example of the javascript, css and html markup required to set up the client side. 

