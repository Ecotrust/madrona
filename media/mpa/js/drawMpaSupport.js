lingcod.drawMpaComplete = function(){
    $.getJSON(
        '/mlpa/mpa/manipulators/',
        lingcod.processManipulators
    );
};

lingcod.processManipulators = function(manipulator_list) {
    manip_string = lingcod.stringFromList(manipulator_list);
    
    target_wkt = lingcod.placemarkToWkt(lingcod.drawTool.placemark);
    
    $.post(
        '/manipulators/'+manip_string+'/', 
        { target_shape: target_wkt },
        lingcod.renderManipulatorResults
    );
};

lingcod.stringFromList = function(list) {
    string_result = '';
    for ( var i = 0; i < list.length; i++ )
    {
        if (i > 0)
            string_result = string_result + ',';
        string_result = string_result + list[i];
    }
    return string_result
};

lingcod.renderManipulatorResults = function(manip_data) {
    ret_obj = eval( '(' + manip_data + ')' );
    document.getElementById("mpa_draw_results").innerHTML=ret_obj.html;
    gex.util.displayKmlString(ret_obj.clipped_shape);
    lingcod.drawTool.clear();
};

lingcod.placemarkToWkt = function(placemark) {
    var linearRing = placemark.getGeometry().getOuterBoundary();
    var wkt = 'POLYGON((';
    for ( var i = 0; i < linearRing.getCoordinates().getLength(); i++ )
    {
        if (i > 0)
            wkt = wkt + ',';
        wkt = wkt + linearRing.getCoordinates().get(i).getLongitude() + ' ' + linearRing.getCoordinates().get(i).getLatitude();
    }
    wkt = wkt + '))'
    
    return wkt;
};
    