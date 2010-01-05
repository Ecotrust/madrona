/**
 * Creates a module that listens to the given form for a new location, adds it
 * to the map, and pans/zooms the map.
 * @constructor
 * @param {GEPlugin} plugin An instance of GoogleEarthExtensions
 * @param {HTMLFormElement} location A form with a single text input for a location to geocode
 */
lingcod.map.geocoder = function(gex, form){
    // Will need to have google maps api v3 already loaded
    this.geocoder = new google.maps.Geocoder();
    this.form = form;
    this.get = ge;
    var self = this;
    
    var clearPlacemark = function(dont_clear_input){
        if(self.placemark){
            gex.dom.removeObject(self.placemark);
            self.placemark = false;
        }
        if(dont_clear_input !== true){
            $(self.form).find('input[name=flyto_location]').val('');
        }
        $(self.form).find('#flytoclear').addClass('disabled');
        return false;
    };
    
    var callback = function(e){
        clearPlacemark(true);
        var location = $(self.form).find('input:first').val();
        if(!location){
            alert('You need to type in a location name.');
            return false;
        }
        self.geocoder.geocode({ address: location, country: '.us'}, function(results, status){
            if(status == google.maps.GeocoderStatus.OK && results.length){
                if(status != google.maps.GeocoderStatus.ZERO_RESULTS){
                    //provide appropriate map extent (bounding box) for each location
                    var viewport = results[0].geometry.viewport; 
                    var sw = new geo.Point(viewport.getSouthWest());
                    var ne = new geo.Point(viewport.getNorthEast());
                    var bounds = new geo.Bounds(sw, ne);
                    var opts = {aspectRatio: 1.0};
                    var bounding_view = gex.view.createBoundsView(bounds, opts);
                    ge.getView().setAbstractView(bounding_view);
                    
                    var point = results[0].geometry.location;
                    self.placemark = gex.dom.addPointPlacemark([point.lat(), point.lng()], {
                      stockIcon: 'shapes/cross-hairs',
                      name: location
                    });
                    $(self.form).find('#flytoclear').removeClass('disabled');
                }else{
                    alert("geocoder didn't find any results.");
                }
            }else{
                alert("Geocoder failed due to: " + status);
            }
        });        
        e.preventDefault();
        return false;        
    }
    $(this.form).find('#flytogo').click(callback);
    $(this.form).find('#flytoclear').click(clearPlacemark);
    $(this.form).submit(callback);
    
};

/**
 * Prepare instance for destruction by remove event listeners.
 */
lingcod.map.geocoder.prototype.destroy = function(){
    $(this.form).find('#flytogo').unbind('click');
    $(this.form).unbind('submit');
};