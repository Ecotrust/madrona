/**
 * Creates a new Formats object.
 * @constructor
 */
madrona.Formats = function() {
};

/**
 * Builds the wkt polygon representation from a geojson polygon representation
 * @param {Geojson} geojson_obj, geojson representation of a polygon
 */
madrona.Formats.prototype.geojsonToWkt = function(geojson_obj) {
    var coords = geojson_obj.coordinates;
    var wkt = 'POLYGON(';
    var numPolys = coords.length;
    for ( var poly = 0; poly < numPolys; poly++ ) {
        var numPoints = coords[poly].length;
        if ( poly == 0 )
            wkt += '(';
        else
            wkt += ', (';
        for ( var point = 0; point < numPoints; point++ ) {
            if (point > 0)
                wkt += ',';
            wkt += coords[poly][point][0] + ' ' + coords[poly][point][1];
        }
        wkt += ')';
    }
    wkt += ')';
    return wkt;
};

madrona.Formats.prototype.kmlToWkt = function(shape) {
    var linearRing = shape.getGeometry().getOuterBoundary();
    var wkt = 'POLYGON((';
    for ( var i = 0; i < linearRing.getCoordinates().getLength(); i++ ) {
        if ( i > 0 )
            wkt = wkt + ',';
        wkt = wkt + linearRing.getCoordinates().get(i).getLongitude() + ' ' + linearRing.getCoordinates().get(i).getLatitude();
    }
    wkt = wkt + '))';
    return wkt;
};


/**
 * Builds the kml placemark representation from a geojson encoded polygon 
 * @param {Geojson} geojson_obj, geojson representation of a polygon
 */
madrona.Formats.prototype.geojsonToKmlPlacemark = function(geojson_obj) {
    var coords = geojson_obj.coordinates;
    var inner_kml = this.innerKml(coords);
    var kml = '<Placemark> <Style> <LineStyle><color>ffffffff</color><width>2</width></LineStyle> <PolyStyle><color>8000ff00</color></PolyStyle> </Style>'+inner_kml+'</Placemark>';
    return kml;
};

/**
 * Called from geojsonToKml
 * Builds the coordinate related kml from a geojson list of coordinates
 * @param {List} coords, geojson list of coordinates
 */
madrona.Formats.prototype.innerKml = function(coords) {
    var kml = '<Polygon>';
    var numPolys = coords.length;
    for ( var poly = 0; poly < numPolys; poly++ ) {
        var numPoints = coords[poly].length;
        if ( poly == 0 ) 
            kml += '<outerBoundaryIs><LinearRing><coordinates>';
        else
            kml += '<innerBoundaryIs><LinearRing><coordinates>';
        for ( var point = 0; point < numPoints; point++ ) {
            if ( point > 0 ) 
                kml += ' ';
            kml += coords[poly][point][0] + ',' + coords[poly][point][1] + ',0';
        }
        if ( poly == 0 )
            kml += '</coordinates></LinearRing></outerBoundaryIs>';
        else
            kml += '</coordinates></LinearRing></innerBoundaryIs>';
    }
    kml += '</Polygon>';
    return kml;
};

madrona.Formats.prototype.wktPolyToKml = function(wkt){
    var wkt = wkt.replace('POLYGON', '');
    wkt = wkt.replace('SRID=4326;', '');
    wkt = jQuery.trim(wkt.replace('((', '').replace('))', ''));
    var coords = wkt.split(',');
    var new_coords = [];
    for(var i=0; i<coords.length;i++){
        var values = jQuery.trim(coords[i]).split(' ');
        new_coords.push([values[0], values[1]]);
    }
    var inner_kml = this.innerKml([new_coords]);
    var kml = '<Placemark><Style><LineStyle><color>ffffffff</color><width>2</width></LineStyle> <PolyStyle><color>8000ff00</color></PolyStyle></Style>'+inner_kml+'</Placemark>';
    return kml;
};