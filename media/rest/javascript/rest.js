lingcod.rest = {}

lingcod.rest.client = function(gex, panel){
    var that;
    
    if(!gex){
        throw('earth-api-utility-library instance required.');
    }
    
    if(!panel){
        throw('lingcod.panel instance required.');
    }
    
    that = {};
    
    // Reads a kml document (from a string) and returns an array of objects that
    // can be used as input to client.create().
    var parseDocument = function(kml){
        var xml = $(kml);
        var return_values = {};
        xml.find("atom\\:link[rel='marinemap.create_form']").each(function(){
            $link = $(this);
            return_values[$link.attr('mm:model')] = {
                model: $link.attr('mm:model'),
                href: $link.attr('href'),
                icon: $link.attr('mm:icon'),
                title: $link.attr('title')                
            }
        });
        return return_values;
    }
    
    that.parseDocument = parseDocument;
    
    var parseResource = function(kmlFeatureObject){
        
    }
    
    that.parseResource = parseResource;
    
    var create = function(config, options){
        $.ajax({
            url: config.href,
            type: 'GET',
            success: function(data, status){
                if(status === 'success'){
                    var html = $(data)[5].innerHTML;
                    var elements = $(html);
                    panel.showContent(elements);
                }else{
                    throw('could not get form at '+config.href);
                }
            },
            error: function(e, b){
                throw('could not get form at '+config.href);
            }
        });
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