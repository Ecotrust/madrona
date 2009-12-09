module('googleLayers');

earthTest("layers", 4, function(ge, gex){
    // append form for layers
    $(document.body).append('<form name="ge_layers"><li><input type="checkbox" name="LAYER_BORDERS">Borders</li><li><input type="checkbox" name="LAYER_ROADS">Roads</li></form>');
    // append form for options
    $(document.body).append('<form name="ge_options"><li><input type="checkbox" name="setStatusBarVisibility" checked />Status Bar</li><li><input type="checkbox" name="nav" />Navigation Control</li><li><input type="checkbox" name="setGridVisibility" />Grid</li><li><input type="checkbox" name="setOverviewMapVisibility" />Overview Map</li><li><input type="checkbox" name="setScaleLegendVisibility" />Scale Legend</li><li><input type="checkbox" name="setAtmosphereVisibility" checked />Atmosphere</li><li><input type="checkbox" name="sun" />Sun</li></form>');
    var googleLayers = new lingcod.map.googleLayers(ge, document.ge_options, document.ge_layers);
    equals(ge.getLayerRoot().getLayerById(ge['LAYER_BORDERS']).getVisibility(), false);
    equals(ge.getLayerRoot().getLayerById(ge['LAYER_ROADS']).getVisibility(), false);
    // no idea why I have to call this twice.
    $('input[name="LAYER_BORDERS"]').click();
    $('input[name="LAYER_BORDERS"]').click();
    equals(ge.getLayerRoot().getLayerById(ge['LAYER_BORDERS']).getVisibility(), true);
    equals(ge.getLayerRoot().getLayerById(ge['LAYER_ROADS']).getVisibility(), false);
});

earthTest("options", function(ge, gex){
    equals(ge.getOptions().getGridVisibility(), false);
    $('input[name="setGridVisibility"]').click();
    $('input[name="setGridVisibility"]').click();
    equals(ge.getOptions().getGridVisibility(), true);
});

test('cleanup (no assertions)', function(){
    $("form[name='ge_layers']").remove();
    $("form[name='ge_options']").remove();
});