lingcod.Manipulator = function(gex, form, render_target, div){
    
    this.altitude = 100;
    var json = false;
    var data = form.find('.json').html();
    if(data){
        json = JSON.parse(data);
    }
    this.needed = true;
    // Return false if manipulations are not needed, else proceed.
    if(!json || !json.manipulators){
        this.needed = false;
        return false;
    }
    this.div = div;
    this.shape_;
    this.manipulators_ = json.manipulators;
    this.gex_ = gex;
    this.form_ = form;
    this.render_target_ = render_target;

    // Fill in the form with content from map.html
    this.render_target_.html($('#geopanel').html());
    
    var self = this;
    
    // Setup event listeners
    this.render_target_.find('.draw_shape').click(function(){
        if(!$(this).hasClass('disabled')){
            $(this).addClass('disabled');
            self.drawNewShape_();
        }
    });
    
    this.render_target_.find('div.manipulated .edit_shape').click(function(){
        if(!$(this).hasClass('disabled')){
            $(this).addClass('disabled');
            self.editExistingShape_();
        }
    });
    
    this.render_target_.find('.done_editing').click(function(){
        self.render_target_.find('.done_editing').addClass('disabled');
        self.finishedEditingCallback_();
    });
    
    this.render_target_.find('div.edit .edit_shape').click(function(){
        if(!$(this).hasClass('disabled')){
            $(this).addClass('disabled');
            self.editExistingShape_();
        }
    });
    
    // Figure out if there is an existing shape in the form, or if a new one
    // needs to be drawn
    if(this.form_.find('#id_geometry_orig').val()){
        this.enterExistingShapeState_();
    }else{
        this.enterNewState_();
    }
}

lingcod.Manipulator.prototype.drawNewShape_ = function(){
    this.is_defining_shape_ = true;
    this.is_defining_new_shape_ = true;
    this.addNewShape_();
    var bounds = this.shape_.getGeometry().getOuterBoundary();
    var self = this;
    this.gex_.edit.drawLineString(bounds, {
        bounce: false,
        finishCallback: function(){
            self.finishedEditingCallback_();
        },
        drawCallback: function(i){
            var coords = bounds.getCoordinates();
            var coord = coords.get(i);
            coord.setAltitude(self.altitude);
            coords.set(i, coord);
        },
        ensureCounterClockwise: false
    });
}

lingcod.Manipulator.prototype.addNewShape_ = function(kml){
    this.clearShape_();
    if(kml){
        this.shape_ = this.gex_.pluginInstance.parseKml(kml);
        this.gex_.pluginInstance.getFeatures().appendChild(this.shape_);
    }else{
        this.shape_ = this.gex_.dom.addPlacemark({
            visibility: true,
            polygon: [],
            style: {
                line: { width: 2, color: 'ffffffff' },
                poly: { color: '8000ff00' }
            }
        });
        this.setZ(this.shape_, this.altitude);
    }
    return this.shape_;
}

lingcod.Manipulator.prototype.setZ = function(kmlObject, z){
    var geo = kmlObject.getGeometry();
    geo.setAltitudeMode(ge.ALTITUDE_ABSOLUTE);
    geo.setExtrude(true);
    var coords = geo.getOuterBoundary().getCoordinates();
    var length = coords.getLength();
    for(var i =0; i<length;i++){
        var coord = coords.get(i)
        coord.setAltitude(z);
        coords.set(i, coord);
    }
    return kmlObject;
}

lingcod.Manipulator.prototype.finishedEditingCallback_ = function(){
    var self = this;
    this.process(this.shape_.getKml(), this.manipulators_, function(data){
        if(data.success === '1'){
            var kmlObject = self.addNewShape_(data.final_shape_kml);
            self.gex_.util.flyToObject(kmlObject, {
                boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
            self.setGeometryFields_(data.user_shape, data.submitted, data.final_shape, data.final_shape_kml);
            self.enterManipulatedState_(data.html, true);            
        }else{
            self.setGeometryFields_('', data.submitted, '', '');
            self.addNewShape_(data.submitted);
            self.gex_.util.flyToObject(self.shape_, {
                boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
            self.enterManipulatedState_(data.html, false);
        }
    });
}

lingcod.Manipulator.prototype.setGeometryFields_ = function(original_wkt, original_kml, final_wkt, final_kml){
    this.form_.find('#id_geometry_orig').val(original_wkt);
    $('#geometry_final_kml').text(final_kml);
    $('#geometry_orig_kml').text(original_kml);
}

lingcod.Manipulator.prototype.hideStates_ = function(){
    this.render_target_.find('div.new, div.edit, div.manipulated, div.editing').hide();
}

lingcod.Manipulator.prototype.enterManipulatedState_ = function(html, success){
    this.hideStates_();
    if(success === true){
        this.render_target_.find('div.manipulated').removeClass('error');
        this.is_invalid_geometry = false;
        this.is_defining_shape_ = false;
        this.is_defining_new_shape_ = false;
    }else{
        this.is_invalid_geometry = true;
        this.render_target_.find('div.manipulated').addClass('error');
    }
    this.render_target_.find('div.manipulated a.edit_shape').removeClass('disabled');
    this.render_target_.find('div.manipulated').show().find('>p')
        .html(html);
}

lingcod.Manipulator.prototype.isInvalidGeometry = function(){
    return this.is_invalid_geometry;
}

lingcod.Manipulator.prototype.enterNewState_ = function(){
    this.hideStates_();
    // this.is_defining_shape_ = true;
    this.render_target_.find('div.new').show();
    this.render_target_.find('a.draw_shape').removeClass('disabled');
}

lingcod.Manipulator.prototype.isDefiningNewShape = function(){
    return this.is_defining_new_shape_;
}

lingcod.Manipulator.prototype.enterEditingState_ = function(){
    this.hideStates_();
    this.is_invalid_geometry = false;
    this.is_defining_shape_ = true;
    this.is_defining_new_shape_ = false;
    this.render_target_.find('.done_editing').removeClass('disabled');
    this.render_target_.find('div.editing').show();
}

lingcod.Manipulator.prototype.enterExistingShapeState_ = function(){
    this.hideStates_();
    this.is_defining_shape = false;
    this.render_target_.find('div.edit .edit_shape').removeClass('disabled');
    this.render_target_.find('div.edit').show();
    var kml = jQuery.trim($('#geometry_final_kml').text());
    if(!kml){
        var kml = jQuery.trim($('#geometry_orig_kml').text());
    }
    this.addNewShape_(kml);
    this.gex_.util.flyToObject(this.shape_, {
        boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
    var self = this;
    this.process(kml, this.manipulators_, function(data){
        if(data.success === '1'){
            var kmlObject = self.addNewShape_(data.final_shape_kml);
            self.gex_.util.flyToObject(kmlObject, {
                boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
        }else{
            // do nothing
        }
    });
}

lingcod.Manipulator.prototype.isShapeDefined = function(){
    return !!this.form_.find('#id_geometry_orig').val();
}

lingcod.Manipulator.prototype.isDefiningShape = function(){
    return this.is_defining_shape_;
}

lingcod.Manipulator.prototype.process = function(wkt, url, callback){
	var self = this;
    $.ajax({
        url: url,
        type: 'POST',
        data: { target_shape: wkt },
        success: function(data, status){
            if(status === 'success'){
                callback(JSON.parse(data));
            }else{
                $(self).trigger('error', "There was an error processing your shape.");
                callback({success: false, html: $('#manipulators_server_error')});
            }
        },
        error: function(data, status){
            $(self).trigger('error', 'There was an error processing your shape.');
            callback({success: false, html: $('#manipulators_server_error').html()});
        }
    });
}

lingcod.Manipulator.prototype.editExistingShape_ = function(){
    var kml = jQuery.trim($('#geometry_orig_kml').text());
    this.addNewShape_(kml);
    this.gex_.util.flyToObject(this.shape_, {
        boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
    this.gex_.edit.editLineString(this.shape_.getGeometry().getOuterBoundary());
    this.enterEditingState_();
    
}

lingcod.Manipulator.prototype.clearShape_ = function(){
    if(this.shape_ && this.shape_.getParentNode()){
        this.gex_.edit.endEditLineString(this.shape_.getGeometry().getOuterBoundary());
        gex.dom.removeObject(this.shape_);
        this.shape_ = false;
    }
}

lingcod.Manipulator.prototype.destroy = function(){
    this.clearShape_();
}