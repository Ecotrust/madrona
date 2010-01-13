lingcod.kmlForest = function(opts){
    var that = {};
        
    var defaults = {
        animate: false,
         //matches google earth desktop behavior if set to false
        selectToggles: false
    }
    
    var opts = $.extend({}, defaults, opts);
        
    that.options = opts;
    
    if(!opts.ge || !opts.gex || opts.div || !opts.element){
    }else{
        throw('Google earth instance, earth-api-utility-library instance, element, and/or map div not specified in options.');
    }
    
    opts.element.addClass('marinemap-kml-forest');
    var kmlObjects = {};
    
    var itemToggle = function(e, clickedData, checked){
        for(var i=0; i<clickedData.length; i++){
            var node = clickedData[i];
            if($(node).hasClass('toggle')){
                var kml = $(node).data('kml');
                kml.setVisibility(checked);
            }
        }
    }
    
    var itemDoubleClick = function(e, target, ev){
        var kml = target.data('kml');
        if(kml.getType() == 'KmlTour'){
            opts.ge.getTourPlayer().setTour(kml);
        }else{
            // do something
            var aspectRatio = $(opts.div).width() / $(opts.div).height();
            opts.gex.util.flyToObject(kml, {
                boundsFallback: true,
                aspectRatio: aspectRatio
            });
        }
    }
    
    var itemClick = function(e, target, ev){
        var kml = target.data('kml');
        if(target.hasClass('description')){
            target.find('input[checked=false]').click();
            kml.setVisibility(true);
            var balloon = opts.ge.createFeatureBalloon('');
            balloon.setFeature(kml);
            balloon.setMinWidth(400);
            opts.ge.setBalloon(balloon);
        }else{
            opts.ge.setBalloon(null);
        }
        // $(opts.element).trigger('itemClick');
    }
            
    that.tree = new lingcod.Tree({
        element: opts.element,
        animate: opts.animate
    });
    $(that.tree).bind('itemToggle', itemToggle)
    $(that.tree).bind('itemDoubleClick', itemDoubleClick)
    $(that.tree).bind('itemClick', itemClick)

    var processKmlObject = function(kmlObject, original_url, callback){
        if (!kmlObject) {
            // show error
            setTimeout(function() {
                alert('Error loading KML - '+original_url);
            },
            0);
            return;
        }
        kmlObjects[original_url] = kmlObject;
        addKmlObject(kmlObject, callback);
    }
    
    var add = function(url, options){
        var options = options || {};
        if(url in kmlObjects){
            throw('KML file with url '+url+' already added.');
        }
        var original_url = url;
        if(options.native_xhr){
            $.ajax({
                url: url,
                type: 'GET',
                cache: !options.cachebust,
                success: function(data, status){
                    var kmlObject = opts.ge.parseKml(data);
                    processKmlObject(kmlObject, original_url, options.callback);
                },
                error: function(){
                    processKmlObject();
                },
                dataType: 'html'
            });
        }else{
            // can be removed when the following ticket is resolved:
            // http://code.google.com/p/earth-api-samples/issues/detail?id=290&q=label%3AType-Defect&sort=-stars%20-status&colspec=ID%20Type%20Summary%20Component%20OpSys%20Browser%20Status%20Stars
            if(!url.match('http')){
                url = window.location.protocol + "//" + window.location.host + "/" + url;
                url = url.replace(/(\w)\/\//g, '$1/');
            }
            if(options.cachebust){
                url = url + '?' + (new Date()).valueOf();
            }
            google.earth.fetchKml(opts.ge, url, function(kmlObject){
                processKmlObject(kmlObject, original_url, options.callback);
            });
        }
    }
    
    that.add = add;
    
    var addKmlObject = function(kmlObject, callback){
        opts.ge.getFeatures().appendChild(kmlObject);
        buildTreeUI(kmlObject, callback);
    }
    
    var buildTreeUI = function(kmlObject, callback){
        var topNode;
        opts.gex.dom.walk({
            visitCallback: function(context){
                var type = this.getType();
                var child = that.tree.add({
                    name: this.getName() || "No name specified in kml",
                    parent: context.current,
                    collapsible: !(this == kmlObject) && (type == 'KmlFolder' || type == 'KmlDocument' || type == 'KmlNetworkLink'),
                    open: this.getOpen(),
                    hideByDefault: false,
                    toggle: !(this == kmlObject),
                    classname: (this == kmlObject) ? 'marinemap-tree-category' : this.getType(),
                    checked: this.getVisibility(),
                    select: false,
                    snippet: this.getSnippet(),
                    doubleclick: true,
                    description: this.getDescription()
                });
                if(this == kmlObject){
                    topNode = child;
                }
                child.data('kml', this);
                context.child = child;
            },
            rootContext: false,
            rootObject: kmlObject
        });
        if(callback){
            callback(kmlObject, topNode);
        }
    }
    
    var clear = function(){
        for(var key in kmlObjects){
            remove(key);
        }
    }
    
    that.clear = clear;
    
    var remove = function(url){
        var obj = kmlObjects[url];
        var found = false;
        $(opts.element).find('> li').each(function(){
            if($(this).data('kml') == obj){
                $(this).remove();
                found = true;
                return;
            }
        });
        if(!found){
            throw('Could not find node in kmlForest that represents the kml object.');
        }
        delete kmlObjects[url];
        opts.gex.dom.removeObject(obj);
    }
    
    that.remove = remove;
    
    var refresh = function(url, options){
        remove(url);
        add(url, options);
    }
    
    that.refresh = refresh;
    
    var getByUrl = function(url){
        if(kmlObjects[url]){
            return kmlObjects[url];
        }else{
            throw('Could not find kmlObject with that url.');
        }
    }
    
    that.getByUrl = getByUrl;
    
    var length = function(){
        var length = 0;
        for(var key in kmlObjects){
            length += 1;
        }
        return length;
    }
    
    that.length = length;
    
    return that;
}