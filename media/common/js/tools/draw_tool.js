//var studyregionKML = 'http://' + document.location.host + '/studyregion/kml/';

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
};

lingcod.DrawTool.prototype.setMpaID = function(id) {
    this.id = id;
};

lingcod.DrawTool.prototype.getMpaID = function(id) {
    return this.id;
};

/**
 * Assigns local variables related to clipped shape geometries
 * @param {String} clipped_wkt, clipped geometry in wkt
 * @param {String} clipped_kml, clipped geometry in kml
 */
lingcod.DrawTool.prototype.setClippedShape = function(clipped_wkt, clipped_kml) {
    this.clippedShapeWKT = clipped_wkt;
    this.clippedShapeKML = clipped_kml;
};

/**
 * Returns wkt of clipped shape
 */
lingcod.DrawTool.prototype.getClippedShape = function() {
    return this.clippedShapeWKT;
};

/**
 * Displays clipped shape on the map
 */
lingcod.DrawTool.prototype.displayClipped = function() {
    //it's important to know here why we reassign clippedShapeKML
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
 * Displays target shape (user drawn shape) on the map
 */
lingcod.DrawTool.prototype.displayTarget = function() {
    this.gex.util.displayKmlString(this.targetShape);
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

//var test_shape = '<Document><Placemark id="coords"> <Style> <LineStyle><color>ffffffff</color><width>2</width></LineStyle> <PolyStyle><color>8000ff00</color></PolyStyle> </Style><Polygon><outerBoundaryIs><LinearRing><coordinates>-118.380493164,32.6103172302,0 -118.167098999,32.8235702515,0 -118.238487244,33.0850410461,0 -118.696723938,33.1927986145,0 -118.837890625,32.8370475769,0 -118.380493164,32.6103172302,0</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark></Document>';


/**
 * Creates and assigns new Target Shape from given coordinate list
 * @param {List} coords, list of coordinates [(long, lat)]
 */
lingcod.DrawTool.prototype.setTargetShape = function(coords) {
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
//maybe we should add function editThisShape that merges editShape with setTargetShape?

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
 * Wraps the targetShape coordinates in a wkt representation
 */
lingcod.DrawTool.prototype.targetToWkt = function() {
    var linearRing = this.targetShape.getGeometry().getOuterBoundary();
    var wkt = 'POLYGON((';
    for ( var i = 0; i < linearRing.getCoordinates().getLength(); i++ ) {
        if (i > 0)
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

