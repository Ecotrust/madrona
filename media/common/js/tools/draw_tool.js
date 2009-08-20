
/**
 * Creates a new draw tool.
 *    
 * @constructor
 */
lingcod.drawTool = function() {
    this.placemark = null;
    this.gex = null;
};


/**
 * Remove the shape that was being drawn
 */
lingcod.drawTool.prototype.clear = function() 
{ 
    if ( this.placemark )
    {
        this.gex.edit.endEditLineString( this.placemark.getGeometry().getOuterBoundary() );
        this.gex.dom.removeObject( this.placemark );
        this.placemark = null;
    }
};


/**
 * Start accepting user input for shape-draw. Sets callbacks to keep measures updated and to switch to edit mode on completion.
 * @param {GEarthExtensions} gex The handle to the GEarthExtensions object
 * @param {String} feedbackSpanId The id of an HTML tag whose innerHTML will be overwritten with server status/feedback results.
 */
lingcod.drawTool.prototype.drawShape = function( gex, finishedCallback ) 
{
    var self = this;
    this.gex = gex;
    
    this.clear();

    this.placemark = gex.dom.addPlacemark({
        polygon: [],
        style: {
            line: { width: 2, color: '#ff0' },
            poly: { color: '8000ffff' }
        }
    });
    
    var drawLineStringOptions = {
        bounce: false,
        drawCallback: null, //function() { anything that should be updated on each mouse event },
        finishCallback: finishedCallback
    };

    gex.edit.drawLineString( this.placemark.getGeometry().getOuterBoundary(), drawLineStringOptions );
};
