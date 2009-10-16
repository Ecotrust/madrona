/**
 * Creates a new draw tool.
 * @constructor
 */
lingcod.DrawTool = function() {
    this.targetShape = null;
};

/**
 * Start accepting user input for shape-draw. Sets callbacks to keep measures updated and to switch to edit mode on completion.
 * @param {String} finishedCallback will be called when the user indicates the drawing is complete.
 */
lingcod.DrawTool.prototype.drawShape = function( finishedCallback ) 
{
    var self = this; //is this needed?
    this.clear();
    
    this.targetShape = gex.dom.addPlacemark({
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

    gex.edit.drawLineString( this.targetShape.getGeometry().getOuterBoundary(), drawLineStringOptions );
};

/**
 * Wraps the user-drawn coordinates in a wkt type geometry
 */
lingcod.DrawTool.prototype.polyToWkt = function() {
    var linearRing = this.targetShape.getGeometry().getOuterBoundary();
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

/**
 * Starts accepting user input for editing.
 */
lingcod.DrawTool.prototype.editShape = function( )
{
    this.targetShape.setVisibility(true);
    gex.edit.editLineString( this.targetShape.getGeometry().getOuterBoundary() );
}

/**
 * Stops the editing process.
 * @param {String} finishedCallback will be called after editing is halted.
 */
lingcod.DrawTool.prototype.endEdit = function( finishedCallback )
{
    gex.edit.endEditLineString(this.targetShape.getGeometry().getOuterBoundary());
    //finishedCallback.call(null, this.targetShape);
    finishedCallback.call();
    
}

/**
 * Remove the shape that was being drawn
 */
lingcod.DrawTool.prototype.clear = function() 
{ 
    if ( this.targetShape )
    {
        gex.edit.endEditLineString( this.targetShape.getGeometry().getOuterBoundary() );
        gex.dom.removeObject( this.targetShape );
        this.targetShape = null;
    }
};

/**
 * Hide the shape that was being drawn
 */
lingcod.DrawTool.prototype.hide = function() 
{ 
    if ( this.targetShape )
    {
        gex.edit.endEditLineString( this.targetShape.getGeometry().getOuterBoundary() );
        this.targetShape.setVisibility(false);
    }
};

