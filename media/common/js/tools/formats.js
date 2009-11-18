/**
 * Creates a new Formats object.
 * @constructor
 */
lingcod.Formats = function() {
};

/**
 * Builds a [lat,lon] list (reversing the order of geojson coordinates) of coordinates from a geojson polygon representation
 * (used to create new placemark (targetShape))
 * @param {Geojson} geojson_obj, geojson representation of a polygon
lingcod.Formats.prototype.geojsonToCoords = function(geojson_obj) {
    var coords = geojson_obj.coordinates;
    var numPolys = coords.length;
    var rev_coords = [];
    for ( poly = 0; poly < numPolys; poly++ ) {
        var numPoints = coords[poly].length;
        rev_coords.push([]);
        for ( var point = 0; point < numPoints; point++ ) {
            var lon = coords[poly][point][0];
            var lat = coords[poly][point][1];
            rev_coords[poly].push([lat,lon]);
        }
    }
    return rev_coords;
};
 */

/**
 * Builds the wkt polygon representation from a geojson polygon representation
 * @param {Geojson} geojson_obj, geojson representation of a polygon
 */
lingcod.Formats.prototype.geojsonToWkt = function(geojson_obj) {
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
    wkt += ')'
    return wkt;
};

/**
 * Builds the kml placemark representation from a geojson encoded polygon 
 * @param {Geojson} geojson_obj, geojson representation of a polygon
 */
lingcod.Formats.prototype.geojsonToKmlPlacemark = function(geojson_obj) {
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
lingcod.Formats.prototype.innerKml = function(coords) {
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
