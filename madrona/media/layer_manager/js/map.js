app.utils.initMap = function (map) {

    map.displayProjection = new OpenLayers.Projection("EPSG:4326");
    map.projection = "EPSG:3857";

    // TODO what is this? 
    // map.addControl(new SimpleLayerSwitcher());

    map.zoomBox = new OpenLayers.Control.ZoomBox();
    map.addControl(map.zoomBox);

    // only allow onetime zooming with box
    map.events.register("zoomend", null, function () {
        if (map.zoomBox.active) {
            app.viewModel.layers.deactivateZoomBox();
        }        
    });

    map.events.register("moveend", null, function () {
        // update the url when we move
        app.updateUrl();
    });
    

    // callback functions for vector attribution (SelectFeature Control)
    var report = function(e) {
        var layer = e.feature.layer.layerModel;
        
        if ( layer.attributes.length ) {
            var attrs = layer.attributes,
                title = layer.name,
                text = [];
            app.viewModel.layers.attributeTitle(title); 
            for (var i=0; i<attrs.length; i++) {
                if ( e.feature.data[attrs[i].field] ) {
                    text.push({'display': attrs[i].display, 'data': e.feature.data[attrs[i].field]});
                }
            }
            app.viewModel.layers.attributeData(text);
        }
    };
      
    var clearout = function(e) {
        app.viewModel.layers.attributeTitle(false);
        app.viewModel.layers.attributeData(false);
    };  
    
    map.vectorList = [];
    map.selectFeatureControl = new OpenLayers.Control.SelectFeature(map.vectorList, {
        hover: true,
        highlightOnly: false,
        renderIntent: "temporary",
        cancelBubble: false,
        eventListeners: {
            //beforefeaturehighlighted: report,
            featurehighlighted: report,
            //boxselectionend: report,
            featureunhighlighted: clearout
        }
    });
    map.addControl(map.selectFeatureControl);
    map.selectFeatureControl.activate();  
    
    //UTF Attribution
    map.UTFControl = new OpenLayers.Control.UTFGrid({
        //attributes: layer.attributes,
        layers: [],
        handlerMode: 'click',
        callback: function(infoLookup) {
            app.viewModel.layers.attributeTitle(false);
            app.viewModel.layers.attributeData(false);
            if (infoLookup) {
                var attributes;
                $.each(app.viewModel.layers.visibleLayers(), function (layer_index, potential_layer) {
                    if (!attributes) { //only loop if attributes has not yet been populated
                        for (var idx in infoLookup) {
                            if (!attributes) { //only loop if attributes has not yet been populated
                                var info = infoLookup[idx];
                                if (info && info.data) { 
                                    var newmsg = '',
                                        hasAllAttributes = true,
                                        parentHasAllAttributes = false;
                                    // if info.data has all the attributes we're looking for
                                    // we'll accept this layer as the attribution layer 
                                    if ( ! potential_layer.attributes.length ) {
                                        hasAllAttributes = false;
                                    }
                                    $.each(potential_layer.attributes, function (attr_index, attr_obj) {
                                        if ( !(attr_obj.field in info.data) ) {
                                            hasAllAttributes = false;
                                        }
                                    });
                                    if ( !hasAllAttributes && potential_layer.parent) {
                                        parentHasAllAttributes = true;
                                        if ( ! potential_layer.parent.attributes.length ) {
                                            parentHasAllAttributes = false;
                                        }
                                        $.each(potential_layer.parent.attributes, function (attr_index, attr_obj) {
                                            if ( !(attr_obj.field in info.data) ) {
                                                parentHasAllAttributes = false;
                                            }
                                        });
                                    }
                                    if (hasAllAttributes) {
                                        attributes = potential_layer.attributes;
                                    } else if (parentHasAllAttributes) {
                                        attributes = potential_layer.parent.attributes;
                                    }
                                    if (attributes) { 
                                        var attribute_objs = [];
                                        $.each(attributes, function(index, obj) {
                                            if ( potential_layer.compress_attributes ) {
                                                var display = obj.display + ': ' + info.data[obj.field];
                                                attribute_objs.push({'display': display, 'data': ''});
                                            } else {
                                                /*** SPECIAL CASE FOR ENDANGERED WHALE DATA ***/
                                                var value = info.data[obj.field];
                                                if (value === 999999) {
                                                    attribute_objs.push({'display': obj.display, 'data': 'No Survey Effort'});
                                                } else {
                                                    try {
                                                        value = value.toFixed(obj.precision);
                                                    }
                                                    catch (e) {
                                                        //keep on keeping on
                                                    }
                                                    attribute_objs.push({'display': obj.display, 'data': value});
                                                }
                                                
                                            }
                                        });
                                        app.viewModel.layers.attributeTitle(potential_layer.name);
                                        //app.viewModel.layers.attributeData([{'display': potential_layer.attributeTitle, 'data': newmsg}]);
                                        app.viewModel.layers.attributeData(attribute_objs);
                                    } 
                                } 
                            }
                        }
                    }
                });
            } 
        }
    });
    map.addControl(map.UTFControl);    

    app.map = map;
};

app.utils.addLayerToMap = function(layer) {
    if (!layer.layer) {
        var opts = {
            displayInLayerSwitcher: false,
            attribution: layer.dataSource
        };

        if (layer.utfurl || (layer.parent && layer.parent.utfurl)) {
            layer.utfgrid = new OpenLayers.Layer.UTFGrid({
                layerModel: layer,
                url: layer.utfurl ? layer.utfurl : layer.parent.utfurl,
                sphericalMercator: true,
                                 
                utfgridResolution: 4,
                displayInLayerSwitcher: false,
                useJSONP: false
            });
            app.map.addLayer(layer.utfgrid);           
            layer.layer = new OpenLayers.Layer.XYZ(
                layer.name, 
                layer.url,
                $.extend({}, opts, 
                    {
                        sphericalMercator: true,
                        isBaseLayer: false
                    }
                )
            );  
            app.map.addLayer(layer.layer);  
        } else if (layer.type === 'Vector') {
            var styleMap = new OpenLayers.StyleMap( {
                fillColor: layer.color,
                fillOpacity: layer.fillOpacity,
                strokeColor: layer.color,
                strokeOpacity: layer.defaultOpacity,
                pointRadius: 4,
                externalGraphic: layer.graphic,
                graphicWidth: 8,
                graphicHeight: 8,
                graphicOpacity: layer.defaultOpacity
            });
            if (layer.lookupField) {
                var mylookup = {};
                $.each(layer.lookupDetails, function(index, details) {                  
                    mylookup[details.value] = { strokeColor: details.color, 
                                                strokeDashstyle: details.dashstyle, 
                                                fill: details.fill,
                                                fillColor: details.color, 
                                                fillOpacity: 0.5,
                                                externalGraphic: details.graphic }; 
                });
                styleMap.addUniqueValueRules("default", layer.lookupField, mylookup);
            }
            layer.layer = new OpenLayers.Layer.Vector(
                layer.name,
                {
                    projection: new OpenLayers.Projection('EPSG:3857'),
                    displayInLayerSwitcher: false,
                    strategies: [new OpenLayers.Strategy.Fixed()],
                    protocol: new OpenLayers.Protocol.HTTP({
                        url: layer.url,
                        format: new OpenLayers.Format.GeoJSON()
                    }),
                    styleMap: styleMap,                    
                    layerModel: layer
                }
            );
            app.map.addLayer(layer.layer);  
            if (layer.attributes.length) {
                app.map.vectorList.unshift(layer.layer);
                app.map.selectFeatureControl.setLayer(app.map.vectorList);
            }
        } else if (layer.type === 'ArcRest') {
            layer.layer = new OpenLayers.Layer.ArcGIS93Rest(
                layer.name, 
                layer.url,
                {
                    layers: "show:"+layer.arcgislayers,
                    srs: 'EPSG:3857',
                    transparent: true
                },
                {
                    isBaseLayer: false
                }
            );
            app.map.addLayer(layer.layer);  
        } else if (layer.type === 'WMS') {
            layer.layer = new OpenLayers.Layer.WMS(
                layer.name, 
                layer.url,
                {
                    'layers': 'basic'
                }
            );
            app.map.addLayer(layer.layer);  
        } else { //if XYZ with no utfgrid
            layer.layer = new OpenLayers.Layer.XYZ(layer.name, 
                layer.url,
                $.extend({}, opts, 
                    {
                        sphericalMercator: true,
                        isBaseLayer: false
                    }
                )
            );
            app.map.addLayer(layer.layer);  
        }
        //app.map.addLayer(layer.layer);  
        //layer.layer.projection = new OpenLayers.Projection("EPSG:3857");
    } else if ( layer.utfurl ) { //re-adding utfcontrol for existing utf layers (they are destroyed in layer.deactivateLayer)
        //layer.utfcontrol = app.addUTFControl(layer);
        //app.map.addControl(layer.utfcontrol); 
    }
    layer.layer.opacity = layer.opacity();
    layer.layer.setVisibility(true);
};


app.utils.setLayerVisibility = function(layer, visibility) {
    // if layer is in openlayers, hide it
    if (layer.layer) {
        layer.layer.setVisibility(visibility);
    }
};

app.utils.setLayerZIndex = function(layer, index) {
    layer.layer.setZIndex(index);
};

$(document).mousedown(function(e) {
  //removing opacity popover from view
  var op_pvr_event = $(e.target).closest("#opacity-popover").length;
  var op_btn_event = $(e.target).closest(".opacity-button").length;
  if (!op_pvr_event && !op_btn_event) {
    $('#opacity-popover').hide();
    $('.opacity-button').removeClass('active');
  }
});
