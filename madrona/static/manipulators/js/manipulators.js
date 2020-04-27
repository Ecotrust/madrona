madrona.Manipulator = function(gex, form, render_target, div){
    this.altitude = 100;
    var json = false;
    var data = form.find('.json').html();
    if(data){
        json = JSON.parse(data);
    }
    this.needed = true;
    // Return false if manipulations are not needed, else proceed.
    if(!json || !json.url){
        this.needed = false;
        return false;
    }
    this.div = div;
    this.shape_;
    this.required_manipulators = json.manipulators;
    this.optional_manipulators = json.optional_manipulators;
    this.manip_desc = json.descriptions;
    this.manip_name = json.display_names;
    this.active = this.required_manipulators.slice(); // pass by value
    this.manipulators_url = json.url;
    this.gex_ = gex;
    this.form_ = form;
    this.render_target_ = render_target;

    // Fill in the form with content from map.html
    this.render_target_.html($('#geopanel').html());
        
    var self = this;

    // Do we expose any geometry input methods other than digitize?
    $.each(json.geometry_input_methods, function(index, value){
            // disable for Internet Exploder
            if (value == 'loadshp' && !$.browser.msie) {
                self.render_target_.find('.load_shape').show();
                self.loadshp_url = json.loadshp_url;
            }
    });
   
    // Set up the manipulators UI 
    if(this.optional_manipulators){
        var required_html = "<form action=''><ul>";
        $.each(this.required_manipulators, function(index, value) { 
                var display_name = self.manip_name[value];
                if(!display_name)
                    display_name = value;
                var description = self.manip_desc[value];
                required_html += "<li class=\"required_manipulator\">";
                required_html += "<input class=\"required_manipulator\" type=\"checkbox\" name=\"required_manipulators\"";
                required_html += " value=\""+ value + "\" id=\"required_manipulator_" + value + "\" CHECKED DISABLED />";
                required_html += "<span>" + display_name + "</span>";
                if(description)
                    required_html += "<p><em>" + description + "</em></p>";
                required_html += "</li>";
        });
        required_html += "</ul></form>";
        this.render_target_.find('.requiredManipulators').html(required_html);

        var optional_html = "<form action=''><ul>";
        var stored_manipulator_string = this.form_.find('#id_manipulators').attr('value');
        $.each(this.optional_manipulators, function(index, value) { 
                var display_name = self.manip_name[value];
                if(!display_name)
                    display_name = value;
                var description = self.manip_desc[value];
                optional_html += "<li class=\"optional_manipulator\">";
                optional_html += "<input class=\"optional_manipulator\" type=\"checkbox\" name=\"optional_manipulators\"";
                optional_html += " value=\""+ value + "\" id=\"optional_manipulator_" + value + "\"";
                if( stored_manipulator_string && stored_manipulator_string.indexOf(value) >= 0) {
                    optional_html += " CHECKED";
                }
                optional_html += "/>";
                optional_html += "<span>" + display_name + "</span>";
                if(description)
                    optional_html += "<p><em>" + description + "</em></p>";
                optional_html += "</li>";
        });
        optional_html += "</ul></form>";
        this.render_target_.find('.optionalManipulators').html(optional_html);
    
        this.render_target_.find('input.optional_manipulator').each( function(index){
            $(this).click(function(){
                self.constructUrl_();
            });
        });
        self.constructUrl_();
    }

    // Setup event listeners
    this.render_target_.find('.draw_shape').click(function(){
        if(!$(this).hasClass('disabled')){
            $(this).addClass('disabled');
            self.render_target_.find('.load_shape').addClass('disabled');
            self.drawNewShape_();
        }
    });
    
    this.render_target_.find('.load_shape').click(function(){
        if(!$(this).hasClass('disabled')){
            $(this).addClass('disabled');
            self.render_target_.find('.draw_shape').addClass('disabled');
            self.loadShapeForm_();
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
    
    this.type = $('#geometry_orig_kml').attr('class');
    // Figure out if there is an existing shape in the form, or if a new one
    // needs to be drawn
    if(this.form_.find('#id_geometry_orig').val()){
        this.enterExistingShapeState_();
    }else{
        this.enterNewState_();
    }
}

madrona.Manipulator.prototype.constructUrl_ = function(){
    var self = this;
    self.active = self.required_manipulators.slice(); // pass by value, NOT reference
    this.render_target_.find('input.optional_manipulator').each( function(index){
        if($(this).attr("checked")) {
            self.active.push($(this).attr("value"));
        }
    });
    var url_parts = this.manipulators_url.split("/").slice(1); // get rid of first empty item 
    url_parts.pop(); // get rid of last empty item
    url_parts.pop(); // remove the comm-seperated manipulators list
    url_parts.push(self.active.join(","));
    this.manipulators_url = "/" + url_parts.join("/") + "/";
    this.form_.find('#id_manipulators').val(self.active.join(","));
}

madrona.Manipulator.prototype.drawNewShape_ = function(){
    this.is_defining_shape_ = true;
    this.is_defining_new_shape_ = true;
    this.addNewShape_();
    var bounds;
    if(this.type === 'polygon'){
        bounds = this.shape_.getGeometry().getOuterBoundary();        
    }else{
        bounds = this.shape_.getGeometry();
    }
    var self = this;
    if(this.type === 'point'){
        this.gex_.edit.place(this.shape_, {
            bounce: false,
            dropCallback: function(){
                self.finishedEditingCallback_();
            }
        });
    }else{
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
}

madrona.Manipulator.prototype.loadShapeForm_ = function(){
    this.is_defining_shape_ = true;
    this.is_defining_new_shape_ = true;
	var self = this;
    if (typeof(self.loadshp_url) == 'undefined') {
        console.log("loadshp_url is undefined");
    }
    $.ajax({
        url: self.loadshp_url, 
        type: 'GET',
        success: function(data, status){
            if(status === 'success'){
                $('#load_shape_div').show().find('>p').html(data); 
                self.render_target_.find('.upload_button').hide();
                var button_html = [
                        '<a href="#" id="load_shape_submit_button" class="button" onclick="this.blur(); return false;">',
                            '<span>Upload File</span>',
                        '</a>',
                ].join('');

                var form = $('#load_shape_form');
                form.after(button_html);

                var errors = '<ul id="load_shape_errorlist" class="errorlist" style="display:none"></ul>';
                form.before(errors);
                var ule = $('#load_shape_errorlist')

                var opts = {
                    dataType: 'json',
                    beforeSubmit: function(formData,b,c) {
                        $(self).trigger('saving', ["Uploading Shape"]);
                        return true;
                    },
                    success: function(response){
                        $(self).trigger('doneSaving');       
                        if (response.status == 'success') {
                            self.shape_ = self.gex_.pluginInstance.parseKml(response.input_kml);
                            self.finishedEditingCallback_();
                        } else {
                            ule.show();
                            ule.html("<li>" + response.error_html + "</li>");
                        }
                        return true;
                    },
                    error: function(data, stat, ethrown){
                        alert(stat);
                        alert(data);
                        alert(ethrown);
                        $(self).trigger('error', "There was an error processing your shape; Status was " + stat + ".");
                        return true;
                    } 
                }

                $('#load_shape_submit_button').click(function(){
                    $(form).ajaxSubmit(opts); 
                    return false; 
                });
            }else{
                $(self).trigger('error', "There was an error retrieving the form; Status was " + status + ".");
            }
        },
        error: function(data, status){
            $(self).trigger('error', 'There was an error processing your shape.');
        }
    });
}

madrona.Manipulator.prototype.addNewShape_ = function(kml){
    this.clearShape_();
    var geom;
    if(kml){
        this.shape_ = this.gex_.pluginInstance.parseKml(kml);
        geom = this.shape_.getGeometry();
    }
    var popts = {
        visibility: true,
        style: {
            line: { width: 2, color: '#FF0' },
            poly: { color: '#FF0', opacity: 0.5 },
            icon: {
                stockIcon: 'shapes/cross-hairs',
                color: '#FF0'
            }
        }            
    }
    if(this.type === 'polygon'){
        popts['polygon'] = geom || [];
    }else if(this.type === 'linestring'){
        popts['lineString'] = geom || [];
    }else{
        // point
        popts['point'] = geom || [0, 0];
    }
    this.shape_ = this.gex_.dom.addPlacemark(popts);
    this.setZ(this.shape_, this.altitude);
    return this.shape_;
}

madrona.Manipulator.prototype.setZ = function(kmlObject, z){
    if(this.type !== 'polygon'){
        // only polygons need z set
        return kmlObject;
    }
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

madrona.Manipulator.prototype.finishedEditingCallback_ = function(){
    var self = this;
    this.process(this.shape_.getKml(), this.manipulators_url, function(data){
        if(data.success === '1'){
            var kmlObject = self.addNewShape_(data.final_shape_kml);
            if(self.type != 'point'){
                self.gex_.util.flyToObject(kmlObject, {
                    boundsFallback: true, aspectRatio: $(self.div).width() / $(self.div).height()});                
            }
            self.setGeometryFields_(data.user_shape, data.submitted, data.final_shape, data.final_shape_kml);
            self.enterManipulatedState_(data.html, true);            
        }else{
            self.setGeometryFields_('', data.submitted, '', '');
            self.addNewShape_(data.submitted);
            if(self.type != 'point'){
                self.gex_.util.flyToObject(self.shape_, {
                    boundsFallback: true, aspectRatio: $(self.div).width() / $(self.div).height()});
            }
            self.enterManipulatedState_(data.html, false);
        }
    });
}

madrona.Manipulator.prototype.setGeometryFields_ = function(original_wkt, original_kml, final_wkt, final_kml){
    this.form_.find('#id_geometry_orig').val(original_wkt);
    // Replacing the entire script tag rather than just changing the contents
    // for the benefit of IE8 (damn IE 8 !!)
    $('#geometry_final_kml').replaceWith('<script id="geometry_final_kml" type="application/vnd.google-earth.kml+xml">'+final_kml+'</script>');
    $('#geometry_orig_kml').replaceWith('<script id="geometry_orig_kml" type="application/vnd.google-earth.kml+xml">'+original_kml+'</script>');
}

madrona.Manipulator.prototype.hideStates_ = function(){
    this.render_target_.find('div.manipulators, div.new, div.edit, div.manipulated, div.editing').hide();
}

madrona.Manipulator.prototype.enterManipulatedState_ = function(html, success){
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

madrona.Manipulator.prototype.isInvalidGeometry = function(){
    return this.is_invalid_geometry;
}

madrona.Manipulator.prototype.enterNewState_ = function(){
    this.hideStates_();
    // this.is_defining_shape_ = true;
    if(this.type === 'point'){
        this.render_target_.find('div.new p.poly').hide();
        this.render_target_.find('div.new p.point').show();        
    }else{
        // poly or linestring
        this.render_target_.find('div.new p.poly').show();
        this.render_target_.find('div.new p.point').hide();
    }
    this.render_target_.find('div.new').show();
    this.render_target_.find('a.draw_shape').removeClass('disabled');
    this.render_target_.find('a.load_shape').removeClass('disabled');
    if(this.optional_manipulators){
        this.render_target_.find('div.manipulators').show();
    }
}

madrona.Manipulator.prototype.isDefiningNewShape = function(){
    return this.is_defining_new_shape_;
}

madrona.Manipulator.prototype.enterEditingState_ = function(){
    this.hideStates_();
    this.is_invalid_geometry = false;
    this.is_defining_shape_ = true;
    this.is_defining_new_shape_ = false;
    this.render_target_.find('.done_editing').removeClass('disabled');
    if(this.type === 'point'){
        this.render_target_.find('div.editing p.poly').hide();
        this.render_target_.find('div.editing p.point').show();        
    }else{
        // poly or linestring
        this.render_target_.find('div.editing p.poly').show();
        this.render_target_.find('div.editing p.point').hide();
    }
    this.render_target_.find('div.editing').show();
    if(this.optional_manipulators){
        this.render_target_.find('div.manipulators').show();
    }
}

madrona.Manipulator.prototype.enterExistingShapeState_ = function(){
    var self = this;
    this.hideStates_();
    this.is_defining_shape = false;
    this.render_target_.find('div.edit .edit_shape').removeClass('disabled');
    if(this.type === 'point'){
        this.render_target_.find('div.edit p.poly').hide();
        this.render_target_.find('div.edit p.point').show();        
    }else{
        // poly or linestring
        this.render_target_.find('div.edit p.poly').show();
        this.render_target_.find('div.edit p.point').hide();
    }
    this.render_target_.find('div.edit').show();
    var kml = jQuery.trim($('#geometry_final_kml').html());
    if(!kml){
        var kml = jQuery.trim($('#geometry_orig_kml').html());
        this.process(kml, this.manipulators_url, function(data){
            if(data.success === '1'){
                var kmlObject = self.addNewShape_(data.final_shape_kml);
                if(self.type != 'point'){
                    self.gex_.util.flyToObject(kmlObject, {
                        boundsFallback: true, aspectRatio: $(self.div).width() / $(self.div).height()});
                }
            }else{
                // do nothing
            }
        });
    }
    this.addNewShape_(kml);
    if(this.type != 'point'){
        this.gex_.util.flyToObject(this.shape_, {
            boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
    }
    var self = this;
}

madrona.Manipulator.prototype.isShapeDefined = function(){
    return !!this.form_.find('#id_geometry_orig').val();
}

madrona.Manipulator.prototype.isDefiningShape = function(){
    return this.is_defining_shape_;
}

madrona.Manipulator.prototype.process = function(kml, url, callback){
    $(this).trigger('processing');
	var self = this;
    $.ajax({
        url: url,
        type: 'POST',
        data: { target_shape: kml },
        success: function(data, status){
            $(self).trigger('doneprocessing');
            if(status === 'success'){
                callback(JSON.parse(data));
            }else{
                $(self).trigger('error', "There was an error processing your shape.");
                callback({success: false, html: $('#manipulators_server_error')});
            }
        },
        error: function(data, status){
            $(self).trigger('doneprocessing');
            $(self).trigger('error', 'There was an error processing your shape.');
            callback({success: false, html: $('#manipulators_server_error').html()});
        }
    });
}

madrona.Manipulator.prototype.editExistingShape_ = function(){
    var kml = jQuery.trim($('#geometry_orig_kml').html());
    this.addNewShape_(kml);
    if(this.type != 'point'){
        this.gex_.util.flyToObject(this.shape_, {
            boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});        
    }
    this.edit_();
    this.enterEditingState_();
    
}

madrona.Manipulator.prototype.clearShape_ = function(){
    if(this.shape_ && this.shape_.getParentNode()){
        this.endEdit_();
        gex.dom.removeObject(this.shape_);
        this.shape_ = false;
    }
}

madrona.Manipulator.prototype.edit_ = function(){
    switch(this.type){
        case 'polygon':
            this.gex_.edit.editLineString(this.shape_.getGeometry().getOuterBoundary());
            break;
        case 'linestring':
            this.gex_.edit.editLineString(this.shape_.getGeometry());
            break;
        case 'point':
            this.gex_.edit.makeDraggable(this.shape_, {bounce: false});
            break;
        default:
            alert('Unrecognized geometry type');
    }
}

madrona.Manipulator.prototype.endEdit_ = function(){
    switch(this.type){
        case 'polygon':
            this.gex_.edit.endEditLineString(this.shape_.getGeometry().getOuterBoundary());
            break;
        case 'linestring':
            this.gex_.edit.endEditLineString(this.shape_.getGeometry());
            break;
        case 'point':
            this.gex_.edit.endDraggable(this.shape_);
            break;
        default:
            alert('Unrecognized geometry type');
    }
}


madrona.Manipulator.prototype.destroy = function(){
    this.clearShape_();
}
