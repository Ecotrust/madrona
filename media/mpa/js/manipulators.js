var try_again_html = '<p><button id="try_again_button">Try Again</button></p>';
var manip_url = '/manipulators-list/';
/**
 * Creates a new Manipulator instance.
 * @constructor
 * @param {Panel} results_panel, used for displaying templates related to manipulator processing
 * @param {Function} renderCallBack, function called after manipulator processing attempt is complete
 * @param {List} manip_list, list of manipulators to process
 * @param {DrawTool} drawTool, object used to draw and edit shapes on the map
 */
lingcod.Manipulators = function(results_panel, renderCallBack, drawTool) { 
    this.results_panel = results_panel;
    this.renderCallBack = renderCallBack;
    this.drawTool = drawTool;
    $.ajaxSetup({ cache: false });
    $.getJSON( manip_url, $.delegate(this.initialize_list, this) );
};

/**
 * Called in response to a completed GET request for the list of manipulators 
 * Assigns manipulator_list with a string representation of the list of manipulators to be executed
 */
lingcod.Manipulators.prototype.initialize_list = function(manip_list) {
    this.manipulator_list = this.stringFromList(manip_list);
}
      
/**
 * Executes an ajax POST request to /manipulators/<manipulator-list> with the user-drawn geometry
 */
lingcod.Manipulators.prototype.process = function() { 
    target_wkt = this.drawTool.targetToWkt();
    $.post(
        '/manipulators/'+this.manipulator_list+'/', 
        { target_shape: target_wkt },
        $.delegate(this.renderResults, this)
    );
};

/**
 * Called upon manipulator completion
 * Assigns clipped shape to drawTool
 * If clipping was a success
 *      Display clipped geometry on map
 *      Display returned template on results panel
 *      Return control to callback
 * Otherwise, display returned template on results panel 
 * @param {JSON} manip_data, the json dictionary containing the manipulated mpa
 */
lingcod.Manipulators.prototype.renderResults = function(manip_data) {
    manip_ret = eval( '(' + manip_data + ')' );
    this.success = manip_ret.success=='1';
    
    if(this.success) {
        var geojson_clipped = eval( '(' + manip_ret.geojson_clipped + ')' );
        this.drawTool.setClippedShape(geojson_clipped);
        this.drawTool.hide();
        this.drawTool.displayClipped();
        this.results_panel.html(manip_ret.html);
        this.renderCallBack.call(this.renderCallBack, this.success);
    }
    else {
        this.displayFail(manip_ret.html);
    }
};

/**
 * Called from renderResults upon manipulator failure
 * Display the failure template and associated buttons
 * @param {String} display_html, the template explaining the failure
 */
lingcod.Manipulators.prototype.displayFail = function(display_html) {
    display = display_html + try_again_html;
    this.results_panel.html(display);
    
    this.try_again_button = $('#try_again_button');
    this.try_again_button.click($.delegate(this.tryAgain, this));
};

/**
 * Returns control to callback with 'success' parameter
 */
lingcod.Manipulators.prototype.tryAgain = function() {
    this.renderCallBack.call(this.success);
};

/**
 * Creates a comma separated string from a list object.
 * @param {List} 
 */
lingcod.Manipulators.prototype.stringFromList = function(list) {
    string_result = '';
    for ( var i = 0; i < list.length; i++ ) {
        if (i > 0)
            string_result = string_result + ',';
        string_result = string_result + list[i];
    }
    return string_result
};
