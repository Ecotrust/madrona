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
    $(this.form).submit(function(e){
        e.preventDefault();
        var location = $(this).find('input:first').val();
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
                    gex.dom.addPointPlacemark([point.lat(), point.lng()], {
                      // stockIcon: 'pal3/icon60.png',
                      name: location
                    });
                }else{
                    alert("geocoder didn't find any results.");
                }
            }else{
                alert("Geocoder failed due to: " + status);
            }
        });
    });
};

/**
 * Prepare instance for destruction by remove event listeners.
 */
lingcod.map.geocoder.prototype.destroy = function(){
    $(this.form).unbind('submit');
};