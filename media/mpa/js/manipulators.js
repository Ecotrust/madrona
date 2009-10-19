/**
 * Creates a new Manipulator instance.
 * @constructor
 * @param {String} renderCallBack will be called after manipulators are processed.
 * @param {List} manip_list is the list of manipulators to process.
 */
lingcod.Manipulators = function(renderCallBack, manip_list) { 
    this.renderCallBack = renderCallBack;
    this.manipulator_list = this.stringFromList(manip_list);
};
      
/**
 * Posts a request to /manipulators/<manipulator-list> with the user-drawn coordinates.
 * @param {WKT Geometry} target_wkt is the geometry to be manipulated
 */
lingcod.Manipulators.prototype.process = function(target_wkt) { 
    $.post(
        '/manipulators/'+this.manipulator_list+'/', 
        { target_shape: target_wkt },
        this.renderCallBack
    );
};

/**
 * Creates a comma separated string from a list object.
 * @param {List} 
 */
lingcod.Manipulators.prototype.stringFromList = function(list) {
    string_result = '';
    for ( var i = 0; i < list.length; i++ )
    {
        if (i > 0)
            string_result = string_result + ',';
        string_result = string_result + list[i];
    }
    return string_result
};
