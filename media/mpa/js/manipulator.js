/*  lingcod.Manipulators 
    parameters:
        renderCallBack -- this is a function that will be called after the POST in processManipulators
                          it will be passed the return value resulting from the manipulators execution
        manip_list -- this is the list of manipulators to be processed for the given model
        drawTool -- this is an instance of drawTool with which the user will draw their mpa
    call path:
        'create_button' click event causes drawAndProcess to be called
        drawAndProcess calls processManipulators 
        processManipulators calls the function referred to by the renderCallBack parameter
*/ 
lingcod.Manipulator = function(renderCallBack, manip_list, drawTool) { 
    this.renderCallBack = renderCallBack;
    this.manipulator_list = this.stringFromList(manip_list);
    this.drawTool = drawTool;
};
      
//called from 'create_button' click event in mlpa-manipulators      
lingcod.Manipulator.prototype.drawAndProcess = function(){
    //enable shape drawing, passing the shape finished handler, setting the scope to this instance
    this.drawTool.drawShape( $.delegate(this.processManipulators, this) );
}

//called from lingcod.Manipulators.drawAndProcess
//posts a request to /manipulators/<manipulator-list> with the target_shape containing the user-drawn coordinates
lingcod.Manipulator.prototype.processManipulators = function() {    
    target_wkt = this.shapeToWkt(this.drawTool.placemark);
    
    $.post(
        '/manipulators/'+this.manipulator_list+'/', 
        { target_shape: target_wkt },
        this.renderCallBack
    );
};

//called from lingcod.Manipulator.processManipulators
//wraps the user-drawn coordinates in a wkt type geometry
lingcod.Manipulator.prototype.shapeToWkt = function(placemark) {
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

//called from lingcod.Manipulator constructor 
//creates a comma separated string from a list object
lingcod.Manipulator.prototype.stringFromList = function(list) {
    string_result = '';
    for ( var i = 0; i < list.length; i++ )
    {
        if (i > 0)
            string_result = string_result + ',';
        string_result = string_result + list[i];
    }
    return string_result
};

