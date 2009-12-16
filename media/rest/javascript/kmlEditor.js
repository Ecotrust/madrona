lingcod.rest.kmlEditor = function(options){
    
    if(!options || !options.url || !options.appendTo || !options.gex || !options.ge || !options.div || !options.client){
        throw('kmlEditor needs url, appendTo, ge, gex, client, and div options');
    }
                
    var kmlLoaded = function(kml){
        var configs = options.client.parseDocument(kml.getKml());
        for(var key in configs){
            var config = configs[key];
            var link = $('<a class="create" href="#js">'+config.title+"</a>");
            link.click(function(){
                options.client.create(config, {
                    success: function(location){
                        // possible memory leak!!!!!!!
                        that.el.kmlForest('refresh', options.url, {
                            cachebust: true, callback: kmlLoaded, native_xhr: true});
                    }
                });
                return false;
            });
            $(that.el).find('>li span.badges').prepend(link);
        }
    }
    
    var that = {};
    
    that.el = $('<div />');
    
    $(options.appendTo).append(that.el);

    that.el.kmlForest({ge: options.ge, gex: options.gex, div: options.div})
        .kmlForest('add', options.url, {cachebust: true, 
            callback: kmlLoaded, native_xhr: true});
    
    that.el.addClass('kmlEditor');
}