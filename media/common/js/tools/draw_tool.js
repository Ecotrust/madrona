
/**
 * Creates a new draw tool.
 * @constructor
 * @param {GEarthExtensions} gex, the Google Earth Extensions object
 */
lingcod.DrawTool = function(gex) {
    this.id = null;
    this.targetShape = null;
    this.clippedShapeWKT = null;
    this.clippedShapeKML = null;
    this.gex = gex;
    this.formats = new lingcod.Formats();
};

lingcod.DrawTool.prototype.setMpaID = function(id) {
    this.id = id;
};

lingcod.DrawTool.prototype.getMpaID = function(id) {
    return this.id;
};

/**
 * Assigns local variables related to clipped shape geometries
 * @param {GeoJSON} geojson_obj, geojson representation of the clipped geometry 
 */
lingcod.DrawTool.prototype.setClippedShape = function(geojson_obj) {
    this.clippedShapeWKT = this.formats.geojsonToWkt(geojson_obj);
    this.clippedShapeKML = this.formats.geojsonToKml(geojson_obj);
};

/**
 * Returns wkt of clipped shape
 */
lingcod.DrawTool.prototype.getClippedShape = function() {
    return this.clippedShapeWKT;
};

/**
 * Creates and assigns new Target Shape from given coordinate list
 * @param {GeoJSON} geojson_obj, geojson representation of the user-drawn geometry 
 */
lingcod.DrawTool.prototype.setTargetShape = function(geojson_obj) {
    //I'm uncomfortable with this [0] reference
    //however, a user-drawn shape cannot be a multi-polygon, so perhaps this is acceptable
    //I'd also like to find a better way of building the targetShape placemark
    //Seems like there should be a better way than extracting and reversing the coordinate pairs
    //Seems like we should be able to use a kml geometry to build the placemark but failed to get that to work
    var coords = this.formats.geojsonToCoords(geojson_obj)[0];
    this.clear();
    this.targetShape = this.gex.dom.addPlacemark({
        visibility: false,
        polygon: coords,
        style: {
            line: { width: 2, color: '#ff0' },
            poly: { color: '8000ffff' }
        }
    });
};

/**
 * Start accepting user input for shape-draw. Sets callbacks to keep measures updated and to switch to edit mode on completion.
 * @param {Function} finishedCallback, function to be called when the user indicates the drawing is complete.
 */
lingcod.DrawTool.prototype.drawShape = function( finishedCallback ) {
    this.clear();
    this.id = null;
    this.clippedShapeWKT = null;
    this.clippedShapeKML = null;
    //this.removeClipped();
    
    this.targetShape = this.gex.dom.addPlacemark({
        visibility: true,
        polygon: [],
        style: {
            line: { width: 2, color: '#ff0' },
            poly: { color: '8000ffff' }
        }
    });
        
    var drawLineStringOptions = {
        bounce: false,
        finishCallback: finishedCallback
    };

    this.gex.edit.drawLineString( this.targetShape.getGeometry().getOuterBoundary(), drawLineStringOptions );
};

/**
 * Displays target shape (user drawn shape) on the map
 */
lingcod.DrawTool.prototype.displayTarget = function() {
    this.gex.util.displayKmlString(this.targetShape);
};

/**
 * Displays clipped shape on the map
 */
lingcod.DrawTool.prototype.displayClipped = function() {
    //it's important to know here why we reassign clippedShapeKML (I don't know why)
    this.clippedShapeKML = this.gex.util.displayKmlString(this.clippedShapeKML);
};

/**
 * Removes clipped shape from display 
 * Removes any references to clipped shape in draw tool
 */
lingcod.DrawTool.prototype.removeClipped = function() {
    if ( this.clippedShapeKML ) {
        //this.gex.edit.endEditLineString( this.clippedShapeKML.getGeometry().getOuterBoundary() );
        this.gex.dom.removeObject( this.clippedShapeKML );
        this.id = null;
        this.clippedShapeWKT = null;
        this.clippedShapeKML = null;
    }
};

/**
 * Displays given shape on the map
 * @param {String} shape, kml version of shape
 */
lingcod.DrawTool.prototype.displayShape = function(shape) {
    return this.gex.util.displayKmlString(shape);
};

/**
 * Removes given shape from the map
 * @param {String} shape, kml version of shape
 */
lingcod.DrawTool.prototype.removeShape = function(shape) {
    this.gex.dom.removeObject(shape);
};

/**
 * Wraps the targetShape coordinates in a wkt representation
 */
lingcod.DrawTool.prototype.targetToWkt = function() {
    //Once again, it seems safe for now to assume a single polygon for target shape (user-drawn)
    //Perhaps this function should be changed to placemarkToWkt and placed in formats.js?
    //Can placemarks be multipolygons?
    var linearRing = this.targetShape.getGeometry().getOuterBoundary();
    var wkt = 'POLYGON((';
    for ( var i = 0; i < linearRing.getCoordinates().getLength(); i++ ) {
        if ( i > 0 )
            wkt = wkt + ',';
        wkt = wkt + linearRing.getCoordinates().get(i).getLongitude() + ' ' + linearRing.getCoordinates().get(i).getLatitude();
    }
    wkt = wkt + '))'
    
    return wkt;
};


/**
 * Begin editing process
 */
lingcod.DrawTool.prototype.editShape = function() {
    this.targetShape.setVisibility(true);
    this.gex.edit.editLineString( this.targetShape.getGeometry().getOuterBoundary() );
};
//maybe we should add function editThisShape that merges editShape with setTargetShape?

/**
 * Stops the editing process.
 * @param {Function} finishedCallback, function called after editing is halted.
 */
lingcod.DrawTool.prototype.endEdit = function( finishedCallback ) {
    this.gex.edit.endEditLineString(this.targetShape.getGeometry().getOuterBoundary());
    finishedCallback.call();
    
};

/**
 * Remove the shape that was being drawn.
 */
lingcod.DrawTool.prototype.clear = function() { 
    if ( this.targetShape ) {
        this.gex.edit.endEditLineString( this.targetShape.getGeometry().getOuterBoundary() );
        this.gex.dom.removeObject( this.targetShape );
        this.targetShape = null;
    }
};

/**
 * Remove all shapes from map
 * Remove references to target shape
 */
lingcod.DrawTool.prototype.clearAll = function() { 
    if ( this.targetShape ) {
        this.gex.edit.endEditLineString( this.targetShape.getGeometry().getOuterBoundary() );
        this.id = null;
        this.targetShape = null;
    }
    //the following line also removes the study region from the map (problem)
    this.gex.dom.clearFeatures();
    //the following line isn't much of a solution to this problem (as it takes many seconds to load)
    //this.gex.util.displayKml(studyregionKML);
};

/**
 * Hide the shape that was being drawn.
 */
lingcod.DrawTool.prototype.hide = function() { 
    if ( this.targetShape ) {
        this.gex.edit.endEditLineString( this.targetShape.getGeometry().getOuterBoundary() );
        this.targetShape.setVisibility(false);
    }
};


