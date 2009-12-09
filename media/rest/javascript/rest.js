lingcod.rest = {}

lingcod.rest.client = function(gex){
    var that;
    
    if(!gex){
        throw({
            name: 'InvalidOptions',
            message: 'earth-api-utility-library instance required.'
        });
    }
    
    that = {};
    
    // Reads a kml document (from a string) and returns an array of objects that
    // can be used as input to client.create().
    var parseDocument = function(kml){
        
    }
    
    that.parseDocument = parseDocument;
    
    var parseResource = function(kmlFeatureObject){
        
    }
    
    that.parseResource = parseResource;
    
    var create = function(configOrFeature, options){
        
    }
    
    that.create = create;
    
    var update = function(configOrFeature, options){
        
    }
    
    that.update = update;
    
    var destroy = function(configOrFeature, options){
        
    }
    
    that.destroy = destroy;
    
    var show = function(configOrFeature, options){
        
    }
    
    that.show = show;
    
    // Private methods
    
    var showForm = function(options){
        
    }
    
    return that;
}