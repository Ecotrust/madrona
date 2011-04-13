lingcod.features.workspace = (function(){
    
    function ucase(string){
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    function idsToUniqueClasses(uids){
        var klasses = [];
        var existing = {};
        jQuery.each(uids, function(i, v){
            var klass = v.replace(/_\d+$/, '');
            if(!existing[klass]){
                klasses.push(klass);
                existing[klass] = true;
            }
        });
        return klasses;
    }
    
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
        
        // First grab feature-specific links
        jQuery.each(doc['feature-classes'], function(i, klass){
            jQuery.each(klass['link-relations'], function(linkrel, links){
                if(links instanceof Array){
                    jQuery.each(links, function(i, link){
                        if(link.title){
                            link.title = ucase(link.title);
                            var action = getOrCreateAction(link, actions)
                            action.addLink(link);                    
                        }else{
                            throw('invalid link with no title');
                        }                        
                    });
                }else{
                    var action = getOrCreateAction(links, actions);
                    action.addLink(links);     
                }
            });
        });
        
        // Then grab generic links
        jQuery.each(doc['generic-links'], function(i, link){
            if(link.title){
                link.title = ucase(link.title);
                var action = getOrCreateAction(link, actions)
                action.addLink(link);                    
            }else{
                throw('invalid link with no title');
            }
        });
        
        // Then grab links by name
        jQuery.each(doc['feature-classes'], function(i, klass){
            var rels = klass['link-relations'];
            // self link, required.
            var self = rels['self'];
            if(typeof self === 'undefined' || self instanceof Array){
                throw('undefined or invalid self link for '+klass.title);
            }else{
                self.rel = 'self';
                var action = getOrCreateAction(self, actions);
            }
        });
        
        return actions;
    }
    
    // 
    // getOrCreateAction
    // 
    // Looks in the given actions list to see if there is an action matching
    // the given link's rel and title attributes. If it can't be found, 
    // creates and appends one. Then adds the link to the actions links via 
    // action.addLink
    function getOrCreateAction(link, actions){
        var action = new Action(
            link.title, link.rel);
        for(var i = 0; i < actions.length; i++){
            if(actions[i].id === action.id){
                return actions[i];
            }
        }
        actions.push(action);
        return action;
    }
    
    function extractFeatureClasses(doc){
        var classes = [];
        jQuery.each(doc['feature-classes'], function(i, klass){
            if(typeof klass['link-relations']['self'] === 'undefined' || 
                self instanceof Array){
                throw('feature class '+klass.title+
                    ' has missing or improperly configured self link.');
            }
            // Make sure each link has the right link rel associated
            jQuery.each(klass['link-relations'], function(linkrel, items){
                if(items instanceof Array){
                    jQuery.each(items, function(i, link){
                        link.rel = linkrel;
                        link.featureClass = klass;
                        link.models = [klass.id];
                    });
                }else{
                    items.rel = linkrel;
                    items.featureClass = klass;
                    items.models = [klass.id];
                }
            });
            classes.push(klass);
        });
        return classes;
    }
    
    //
    // lingcod.feature.workspace constructor
    //
    var constructor = function(doc, options){
        // Exported public API
        var that = {};
        
        // apply defaults to options
        var options = jQuery.extend(options || {}, defaults);
        
        var getById = function(id){
            for(var i = 0; i < that.featureClasses.all.length; i++){
                if(that.featureClasses.all[i].id === id){
                    return that.featureClasses.all[i];
                }
            }
            return false;
        };
        
        that.featureClasses = {
            all: extractFeatureClasses(doc),
            getById: getById
        };
        
        function getByRel(rel){
            var actions = [];
            for(var i = 0; i < that.actions.all.length; i++){
                if(that.actions.all[i].rel === rel){
                    actions.push(that.actions.all[i]);
                }
            }
            return actions;
        }
        
        function getByTitle(title){
            var actions = [];
            for(var i = 0; i < that.actions.all.length; i++){
                if(that.actions.all[i].title === title){
                    actions.push(that.actions.all[i]);
                }
            }
            return actions;
        }
        
        function getActionById(id){
            for(var i = 0; i < that.actions.all.length; i++){
                if(that.actions.all[i].id === id){
                    return that.actions.all[i];
                }
            }
            return false;
        }
        
        // List of actions, derived from links within server-side workspace
        that.actions = {
            all: extractActions(doc),
            getByRel: getByRel,
            getByTitle: getByTitle,
            getById: getActionById,
            each: function(callback){
                jQuery.each(that.actions.all, function(i, v){callback(v)});
            }
        }
        
        // Gets all actions that should be accessible with the current 
        // selection. selection argument should be an array of client ids, ie
        // ['mlpa_mpa_1', 'folder_2']
        that.getActiveActions = function(selection){
            if(!selection.length){
                return [];
            }
            var multiple = selection.length > 1;
            var klasses = idsToUniqueClasses(selection);
            var actions = [];
            that.actions.each(function(action){
                if(action.active(klasses, multiple)){
                    actions.push(action);
                }                
            });
            return actions;
        }
        
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
    
    var id_counter = 0;
    
    function Action(title, rel){
        // exported public api
        var that = {};
        
        that.title = title;
        that.rel = rel;
        if(that.rel === 'self'){
            that.id = that.rel;
        }else if(that.rel === 'create'){
            that.id = that.rel + id_counter;
            id_counter++;
        }else{
            that.id = that.rel + '_' + that.title;
        }
        
        // links 
        that.links = [];
        
        that.addLink = function(link){
            if(link.rel !== that.rel){
                throw('Wrong link type! Must be ' + that.rel + '. Is ' + 
                    link.rel);
            }else{
                that.links.push(link);                
            }
            if(link.rel === 'create'){
                that.title = ucase(link.featureClass.title);
            }
            if(typeof link.method === 'undefined'){
                link.method = 'GET';
            }
        }
        
        that.active = function(selected){
            window.action = that;
            var valid_link = false;
            for(var j = 0; j < that.links.length; j++){
                var link = that.links[j];
                for(var i = 0; i < selected.length; i++){
                    var model = selected[i];
                    if(model.getType){
                        model = lingcod.features.model(model);
                    }
                    if(jQuery.inArray(model, link.models) === -1){
                        valid_link = false;
                        break;
                    }
                    if(selected.length > 1){
                        if(!link.select || jQuery.inArray('multiple', link.select.split(' ')) === -1){
                            valid_link = false;
                            break;                            
                        }
                    }
                    valid_link = link;
                }
                if(valid_link){
                    return valid_link;
                }
            };
            return false;
        }
        
        that.getUrl = function(selected){
            if(that.rel === 'create'){
                return that.links[0]['uri-template'];
            }
            var link = that.getLink(selected);
            var uri = link['uri-template'];
            var repl = '{uid}';
            if(uri.indexOf(repl) === -1){
                repl = '{uid+}';
            }
            return uri.replace(repl, selected.join(','));
        }
        
        that.getLink = function(selected){
            if(that.links[0].rel === 'create'){
                return that.links[0];
            }
            return that.active(idsToUniqueClasses(selected));            
        }
        
        // return public api
        return that;
    }
    
    return constructor;
    
})();