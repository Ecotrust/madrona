lingcod.Manipulator = function(gex, form, render_target, div){
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
    this.formats_ = new lingcod.Formats();

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
    if(this.form_.find('#id_geometry_final').val()){
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
        }
    });
}

lingcod.Manipulator.prototype.addNewShape_ = function(kml){
    this.clearShape_();
    if(kml){
        this.shape_ = this.gex_.util.displayKmlString(kml);
    }else{
        this.shape_ = this.gex_.dom.addPlacemark({
            visibility: true,
            polygon: [],
            style: {
                line: { width: 2, color: 'ffffffff' },
                poly: { color: '8000ff00' }
            }
        });        
    }
    return this.shape_;
}

lingcod.Manipulator.prototype.finishedEditingCallback_ = function(){
    var orig_wkt = this.formats_.kmlToWkt(this.shape_);
    var self = this;
    this.process(orig_wkt, this.manipulators_, function(data){
        if(data.success === '1'){
            var g = JSON.parse(data.geojson_clipped);
            var kml = self.formats_.geojsonToKmlPlacemark(g);
            var kmlObject = self.addNewShape_(kml);
            // that.finalKmlObject = gex.util.displayKmlString(kml);
            self.gex_.util.flyToObject(kmlObject, {
                boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
            self.setGeometryFields_(orig_wkt, self.formats_.geojsonToWkt(g));
            // setGeomFields(wkt, formats.geojsonToWkt(g));
            self.enterManipulatedState_(data.html, true);            
        }else{
            self.setGeometryFields_(orig_wkt, '');
            var shape = self.shape_;
            self.addNewShape_(shape.getKml());
            self.gex_.util.flyToObject(self.shape_, {
                boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
            self.enterManipulatedState_(data.html, false);
        }
    });
}

lingcod.Manipulator.prototype.setGeometryFields_ = function(original_wkt, final_wkt){
    this.form_.find('#id_geometry_final').val('SRID=4326;'+final_wkt);
    this.form_.find('#id_geometry_orig').val('SRID=4326;'+original_wkt);
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
    var wkt = this.form_.find('#id_geometry_final').val();
    var kml = this.formats_.wktPolyToKml(wkt);
    this.addNewShape_(kml);
    this.gex_.util.flyToObject(this.shape_, {
        boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
}

lingcod.Manipulator.prototype.isShapeDefined = function(){
    return !!this.form_.find('#id_geometry_final').val();
}

lingcod.Manipulator.prototype.isDefiningShape = function(){
    return this.is_defining_shape_;
}

lingcod.Manipulator.prototype.process = function(wkt, url, callback){
    $.ajax({
        url: url,
        type: 'POST',
        data: { target_shape: wkt },
        success: function(data, status){
            if(status === 'success'){
                callback(JSON.parse(data));
            }else{
                alert('there was an error processing your shape.');
                $(this).trigger('error', "There was an error processing your shape.");
                callback({success: false, html: $('#manipulators_server_error')});
            }
        },
        error: function(data, status){
            $(this).trigger('error', 'There was an error processing your shape.');
            callback({success: false, html: $('#manipulators_server_error').html()});
        }
    });
}

lingcod.Manipulator.prototype.editExistingShape_ = function(){
    var wkt = this.form_.find('#id_geometry_orig').val();
    var kml = this.formats_.wktPolyToKml(wkt);
    this.addNewShape_(kml);
    window.shape = this.shape_;
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