lingcod.features.workspace = (function(){
    
    // 
    // extractActions
    // 
    // Private static method. Looks for links with the give rel attribute 
    // within both feature-specific and generic links. Constructs an Action 
    // for each encountered link title. 
    // 
    // @returns Array
    // 
    function extractActions(doc){
        // list of actions to return
        var actions = [];
        // we're also going to keep a hash keyed by rel+title for lookups
        var existing = {};
        // First grab feature-specific links
        jQuery.each(doc['feature-classes'], function(i, klass){
            jQuery.each(klass['link-relations'], function(linkrel, links){
                if(links instanceof Array){
                    jQuery.each(links, function(i, link){
                        if(!link.rel){
                            link.rel = linkrel;
                        }
                        if(link.title){
                            var action = getOrCreateAction(link, actions)
                            action.addLink(link);                    
                        }else{
                            throw('invalid link with no title');
                        }                        
                    });
                }
                // else do nothing, special type of link
            });
        });
        // Then grab generic links
        jQuery.each(doc['generic-links'], function(i, link){
            if(link.title){
                var action = getOrCreateAction(link, actions)
                action.addLink(link);                    
            }else{
                throw('invalid link with no title');
            }
        })
        return actions;
    }
    
    function getOrCreateAction(link, actions){
        var key = link.rel+link.title;
        var action = actions[key];
        if(typeof action !== 'object'){
            // Is a new named action
            var action = actions[key] = new Action(
                link.title, link.rel);
            actions.push(action);
        }
        return action;
    }
    
    //
    // lingcod.feature.workspace constructor
    //
    var constructor = function(doc, options){
        // Exported public API
        var that = {};
        
        // apply defaults to options
        var options = jQuery.extend(options || {}, defaults);
        
        that.feature_classes = doc.feature_classes;
        
        // List of actions, derived from links within server-side workspace
        that.actions = extractActions(doc);
        
        // Useful for testing
        that.doc = doc;

        // Return all public methods, properties
        return that;
    }
    
    // Default options if left unspecified
    var defaults = {
        // By default, share rel isolated on the actions property. If set to
        // true it will just be another edit link.
        shareInEditLinks: false
    }
    
    function Action(title, rel){
        // exported public api
        var that = {};
        
        that.title = title;
        that.rel = rel;
        // links 
        that.links = [];
        
        that.addLink = function(link){
            if(link.rel !== that.rel){
                throw('Wrong link type! Must be ' + that.rel + '. Is ' + 
                    link.rel);
            }else{
                that.links.push(link);                
            }
        }
        
        // return public api
        return that;
    }
    
    return constructor;
    
})();