lingcod.Manipulator = function(gex, form, render_target, div){
    
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
            if (value == 'load_shp' && !$.browser.msie) {
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
    
    // Figure out if there is an existing shape in the form, or if a new one
    // needs to be drawn
    if(this.form_.find('#id_geometry_orig').val()){
        this.enterExistingShapeState_();
    }else{
        this.enterNewState_();
    }
}

lingcod.Manipulator.prototype.constructUrl_ = function(){
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

lingcod.Manipulator.prototype.loadShapeForm_ = function(){
    this.is_defining_shape_ = true;
    this.is_defining_new_shape_ = true;
	var self = this;
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
    this.process(this.shape_.getKml(), this.manipulators_url, function(data){
        if(data.success === '1'){
            var kmlObject = self.addNewShape_(data.final_shape_kml);
            self.gex_.util.flyToObject(kmlObject, {
                boundsFallback: true, aspectRatio: $(self.div).width() / $(self.div).height()});
            self.setGeometryFields_(data.user_shape, data.submitted, data.final_shape, data.final_shape_kml);
            self.enterManipulatedState_(data.html, true);            
        }else{
            self.setGeometryFields_('', data.submitted, '', '');
            self.addNewShape_(data.submitted);
            self.gex_.util.flyToObject(self.shape_, {
                boundsFallback: true, aspectRatio: $(self.div).width() / $(self.div).height()});
            self.enterManipulatedState_(data.html, false);
        }
    });
}

lingcod.Manipulator.prototype.setGeometryFields_ = function(original_wkt, original_kml, final_wkt, final_kml){
    this.form_.find('#id_geometry_orig').val(original_wkt);
    // Replacing the entire script tag rather than just changing the contents
    // for the benefit of IE8 (damn IE 8 !!)
    $('#geometry_final_kml').replaceWith('<script id="geometry_final_kml" type="application/vnd.google-earth.kml+xml">'+final_kml+'</script>');
    $('#geometry_orig_kml').replaceWith('<script id="geometry_orig_kml" type="application/vnd.google-earth.kml+xml">'+original_kml+'</script>');
}

lingcod.Manipulator.prototype.hideStates_ = function(){
    this.render_target_.find('div.manipulators, div.new, div.edit, div.manipulated, div.editing').hide();
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
    this.render_target_.find('a.load_shape').removeClass('disabled');
    if(this.optional_manipulators){
        this.render_target_.find('div.manipulators').show();
    }
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
    if(this.optional_manipulators){
        this.render_target_.find('div.manipulators').show();
    }
}

lingcod.Manipulator.prototype.enterExistingShapeState_ = function(){
    var self = this;
    this.hideStates_();
    this.is_defining_shape = false;
    this.render_target_.find('div.edit .edit_shape').removeClass('disabled');
    this.render_target_.find('div.edit').show();
    var kml = jQuery.trim($('#geometry_final_kml').html());
    if(!kml){
        var kml = jQuery.trim($('#geometry_orig_kml').html());
        this.process(kml, this.manipulators_url, function(data){
            if(data.success === '1'){
                var kmlObject = self.addNewShape_(data.final_shape_kml);
                self.gex_.util.flyToObject(kmlObject, {
                    boundsFallback: true, aspectRatio: $(self.div).width() / $(self.div).height()});
            }else{
                // do nothing
            }
        });
    }
    this.addNewShape_(kml);
    this.gex_.util.flyToObject(this.shape_, {
        boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
    var self = this;
}

lingcod.Manipulator.prototype.isShapeDefined = function(){
    return !!this.form_.find('#id_geometry_orig').val();
}

lingcod.Manipulator.prototype.isDefiningShape = function(){
    return this.is_defining_shape_;
}

lingcod.Manipulator.prototype.process = function(kml, url, callback){
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

lingcod.Manipulator.prototype.editExistingShape_ = function(){
    var kml = jQuery.trim($('#geometry_orig_kml').html());
    this.addNewShape_(kml);
    this.gex_.util.flyToObject(this.shape_, {
        boundsFallback: true, aspectRatio: $(this.div).width() / $(this.div).height()});
    this.edit_();
    this.enterEditingState_();
    
}

lingcod.Manipulator.prototype.clearShape_ = function(){
    if(this.shape_ && this.shape_.getParentNode()){
        this.endEdit_();
        gex.dom.removeObject(this.shape_);
        this.shape_ = false;
    }
}

lingcod.Manipulator.prototype.edit_ = function(){
    this.gex_.edit.editLineString(this.shape_.getGeometry().getOuterBoundary());
}

lingcod.Manipulator.prototype.endEdit_ = function(){
    this.gex_.edit.endEditLineString(this.shape_.getGeometry().getOuterBoundary());
}


lingcod.Manipulator.prototype.destroy = function(){
    this.clearShape_();
}
