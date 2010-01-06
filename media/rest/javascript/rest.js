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
    
    // Reads a kml document (from a string) and returns an array of objects 
    // that can be used as input to client.create().
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
        var kml = kmlFeatureObject.getKml();
        var self = $(kml).find('atom\\:link[rel=self]');
        var form = $(kml).find('atom\\:link[rel=marinemap.update_form]');
        if(self.length === 1 && form.length === 1){
            return {
                title: self.attr('title'),
                location: self.attr('href'),
                model: self.attr('mm:model'),
                form_icon: self.attr('mm:icon'),
                form_link: form.attr('href'),
                form_title: form.attr('title')
            }
        }else{
            throw('REST Client: Could not parse resource.');
        }
    }
    
    that.parseResource = parseResource;
    
    var onsubmit = function(e, form, options){
        var action = $(form).attr('action');
        $.ajax({
            url: action,
            type: 'POST',
            data: $(form).serialize(),
            complete: function(req, status){
                switch(req.status){
                    case 201:
                        // new object created, get location header
                        panel.close();
                        if(options && options.success){
                            options.success(
                                req.getResponseHeader('Location'));
                        }
                        break;
                    
                    case 200:
                        // object edited successfully
                        if(options.success){
                            panel.close();
                            options.success(options.location);
                        }                        
                        break;

                    case 400:
                        // validation error
                        options['validation_error'] = true;
                        setupForm(req.responseText, options);
                        break;
                    
                    default:
                        // serious error
                }
            }
        });
        // on error
        // panel.showError('title', 'msg');
        // if(options && options['error']){
        //     error(title, msg);
        // }
    }
    
    var setupForm = function(text, options){
        var geo_panel = $('#geopanel').html();
        var content = $('<div><div class="tabs"><ul><li><a href="#PanelGeometry"><span>Geometry</span></a></li><li><a href="#PanelAttributes"><span>Attributes</span></a></li></ul><div id="PanelGeometry">'+geo_panel+'</div><div id="PanelAttributes"></div><div class="form_controls"><a href="#" class="submit_button button" onclick="this.blur(); return false;"><span>Submit</span></a><a href="#" class="cancel_button button red" onclick="this.blur(); return false;"><span>Cancel</span></a><br class="clear" /></div></div>');
        var html = $(text);
        var h1 = html.find('h1');
        h1.remove();
        content.prepend(h1);
        html.find('input[type=submit]').hide();
        var form = html.find('form');
        content.find('#PanelAttributes').append(html);
        form.submit(function(e){
            onsubmit(e, form, options);
            return false;
        });
        content.find('.submit_button').click(function(){
            form.trigger('submit');
        });
        content.find('.cancel_button').click(function(){
            panel.close();
        });
        panel.addContent(content);
        var tabs = content.find('.tabs').tabs();
        tabs.bind('tabsshow', function(e){
            var div = $(this).parent().parent().parent();
            console.log(div);
            // scroll to 1, then 0 for the benefit of dumb firefox
            div.scrollTop(1);
            div.scrollTop(0);
        });
        // so this is how it might work:
        // var manipulations_needed = manipulators.needed(form);
        
        // This boolean test is by no means a recommended impementation Scott,
        // just something I did to tide me over while working on form styles.
        var manipulations_needed = html.find('#id_geometry_orig').length === 1;
        if(manipulations_needed){
            // fill in the geometry tab:
            // $('#PanelGeometry')...
            tabs.tabs('select', '#PanelGeometry');
        }else{
            tabs.tabs('select', '#PanelAttributes');
            tabs.tabs('disable', 0);
            tabs.find('> .ui-tabs-nav').hide();
        }
        if(options.validation_error){
            tabs.tabs('select', '#PanelAttributes');
        }
        panel.show();
    }
    
    var create = function(config, options){
        options = options || {};
        $.ajax({
            cache: false,
            url: config.href,
            type: 'GET',
            success: function(data, status){
                if(status === 'success'){
                    setupForm(data, options);
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
    
    var getConfig = function(configOrFeature){
        if(typeof configOrFeature === 'object' && configOrFeature.getType){
            return parseResource(configOrFeature);
        }else{
            return configOrFeature;
        }
    }
    
    var update = function(configOrFeature, options){
        var config = getConfig(configOrFeature);
        var options = options || {};
        options.location = config.location;
        $.ajax({
            cache: false,
            url: config.form_link,
            type: 'GET',
            success: function(data, status){
                if(status === 'success'){
                    setupForm(data, options);
                }else{
                    throw('could not get form at '+config.form_link);
                }
            },
            error: function(e, b){
                if(options && options.error){
                    options.error(e, b);
                }
            }
        });
    }

    that.update = update;
    
    var destroy = function(configOrFeature, options){
        var config = getConfig(configOrFeature);
        var options = options || {};
        var answer;
        if(options.confirm !== false){
            answer = confirm(
                'Are you sure you want to delete "'+config.title+'"?');
        }else{
            answer = true;
        }
        if(answer){
            $.ajax({
                url: config.location,
                type: 'DELETE',
                complete: function(response, status){
                    if(status === 'success'){
                        if(options.success){
                            options.success(config.location);
                        }
                    }else{
                        // show an error
                        panel.showError('Server Error', 'Could not delete.');
                        if(options.error){
                            options.error(response, status);
                        }
                    }
                }
            });
        }else{
            if(options.cancel){
                cancel(config.location);
            }
        }
    }
    
    that.destroy = destroy;
    
    // client.show
    // ===========
    // Show a feature's attributes in the panel.
    // 
    // Returns a config object for the passed feature.
    // 
    // @param {KmlFeatureObject or Object} configOrFeature, the feature to show 
    // or a config object for a feature.
    // 
    // @param {Object} options, an object with optional success and error 
    // callbacks.
    // 
    // Usage:
    //      var config = client.show(kmlFeatureObject, {
    //          success: function(location){
    //              do something
    //          },
    //          error: function(response, status){
    //              do something
    //          }
    //      });
    // 
    // now I can call client.show with config:
    //      client.show(config, options);
    // 
    var show = function(configOrFeature, options){
        options = options || {};
        var config = getConfig(configOrFeature);
        options['load_msg'] = 'Loading '+config['title'];
        panel.showUrl(config['location'], options);
    }
    
    that.show = show;
    
    // Private methods
 
    // to make up for the fact that the Location header returns the full path,
    // and get_absolute_url calls for each resource in the kml will not 
    // actually return an absolute url.
    // See http://code.djangoproject.com/wiki/ReplacingGetAbsoluteUrl
    function getPath(url) {
        return $('<a/>').attr('href',url)[0].pathname.replace(/^[^\/]/,'/');
    }
    
    that.getPath = getPath;
    
    
    // METHODS TO AID IN TESTING
    // =========================
    
    // Inefficient. Really only for testing
    // Finds Kml Feature within a text file that contains a Feature with 
    // matching location.
    var findResourceInString = function(location, text){
        var path = getPath(location);
        var link = $(text).find('atom\\:link[href='+path+']');
        if(link.length === 0){
            var link = $(text).find('atom\\:link[href='+location+']');            
        }
        if(link.length){
           return link.parent();
        }else{
            return false;
        }
    }
    
    that.findResourceInString = findResourceInString;
    
    // Inefficient, only for testing.
    // Given the location of a resource and a kmlObject that contains it,
    // find the KmlFeatureObject that represents it.
    var findResource = function(location, kmlObject){
        var resource = false;
        gex.dom.walk({
            rootObject: kmlObject,
            visitCallback: function(context){
                var text = this.getKml();
                var result = findResourceInString(location, text);
                if(result){
                    resource = this;
                    // don't return false. We have to continue deeper to make
                    // sure we're not selecting a container element.
                }
            }
        });
        return resource;
    }
    
    that.findResource = findResource;
           
    return that;
}