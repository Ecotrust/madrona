// load layers from fixture or the server
app.viewModel.layers.loadLayers = function(data) {
    var self = app.viewModel.layers;
    // load layers
    $.each(data.layers, function(i, layer) {
        var layerViewModel = new layerModel(layer);

        self.layerIndex[layer.id] = layerViewModel;
        // add sublayers if they exist
        if (layer.subLayers) {
            $.each(layer.subLayers, function(i, layer_options) {
                var subLayer = new layerModel(layer_options, layerViewModel);
                app.viewModel.layers.layerIndex[subLayer.id] = subLayer;
                layerViewModel.subLayers.push(subLayer);
            });
        }
    });

    // load themes
    $.each(data.themes, function(i, themeFixture) {
        var layers = [],
            theme = new themeModel(themeFixture);
        $.each(themeFixture.layers, function(j, layer_id) {
            // create a layerModel and add it to the list of layers
            var layer = self.layerIndex[layer_id],
                searchTerm = layer.name + ' (' + themeFixture.display_name + ')';
            layer.themes.push(theme);
            theme.layers.push(layer);
            
            if (!layer.subLayers.length) { //if the layer does not have sublayers
                self.layerSearchIndex[searchTerm] = {
                    layer: layer,
                    theme: theme
                };
            } else { //if the layer has sublayers
                $.each(layer.subLayers, function(i, subLayer) {
                    var searchTerm = subLayer.name + ' (' + themeFixture.display_name + ')';
                    self.layerSearchIndex[searchTerm] = {
                        layer: subLayer,
                        theme: theme
                    };
                });  
                layer.subLayers.sort( function(a,b) { return a.name.toUpperCase().localeCompare(b.name.toUpperCase()); } );
            } 

        });
        //sort by name
        theme.layers.sort( function(a,b) { return a.name.toUpperCase().localeCompare(b.name.toUpperCase()); } );
        
        self.themes.push(theme);
    });
    app.utils.typeAheadSource = (function () {
            var keys = [];
            for (var searchTerm in app.viewModel.layers.layerSearchIndex) {
                if (app.viewModel.layers.layerSearchIndex.hasOwnProperty(searchTerm)) {
                    keys.push(searchTerm);
                }
            }
            return keys;
        })();

};

app.viewModel.layers.loadLayersFromFixture = function() {
    app.viewModel.layers.loadLayers(app.fixture);
    $('#layer-search-box').typeahead({ source: app.utils.typeAheadSource  });
    $('#layers-loading').fadeOut();
    app.viewModel.layers.turnOnDefault();
};

app.viewModel.layers.turnOnDefault = function() {
    $.each(app.viewModel.layers.layerIndex, function(i, layer) {
        if (layer.defaultOn) {
            layer.activateLayer();
        }
    });
};

app.viewModel.layers.loadLayersFromServer = function() {
    return $.getJSON('/layer_manager/layers.json', function(data) {
        app.viewModel.layers.loadLayers(data);
    })
    .success( function() { 
        $('#layer-search-box').typeahead({
            source: app.utils.typeAheadSource  
        });
        $('#layers-loading').fadeOut();
        app.viewModel.layers.turnOnDefault();
    })
    .error( function() { console.log("error"); } );

};
