(function($){
    var KMLForest = {
        
        // options: {ge, gex, animate}
        _init: function(opts){
            this.ge = this.options.ge;
            this.gex = this.options.gex;
            this.element.addClass('marinemap-kml-forest');
            this.kmlObjects = {};
            $(this.element).tree({animate: this.options.animate})
                .bind('itemToggle', function(e, clickedData, checked){
                    for(var i=0; i<clickedData.length; i++){
                        var node = clickedData[i];
                        
                        var kml = $(node).data('kml');
                        kml.setVisibility(checked);
                        var c = kml;
                        while (c && 'setVisibility' in c) {
                            c.setVisibility(checked);
                            c = c.getParentNode();
                            //store.setValue(item, 'checked' 
                        }
                    }
                });
        },

        // options = {parent, cachebust, }
        add: function(url, opts){
            console.log('add', url);
            var options = opts || {};
            var self = this;
            if(!url.match('http')){
                url = window.location + url;
                url = url.replace(/(\w)\/\//g, '$1/');
            }
            if(options['cachebust']){
                url = url + '?' + (new Date).valueOf();
            }
            google.earth.fetchKml(this.ge, url,
            function(kmlObject) {
                if (!kmlObject) {
                    // show error
                    setTimeout(function() {
                        alert('Error loading KML.');
                    },
                    0);
                    return;
                }
                self.kmlObjects[url] = kmlObject;
                self._addKmlObject(kmlObject, options.callback);
            });            
        },
        
        _addKmlObject: function(kmlObject, callback){
            console.log('addKmlObject');
            this.ge.getFeatures().appendChild(kmlObject);
            this._buildTreeUI(kmlObject, callback);
        },
        
        _buildTreeUI: function(kmlObject, callback){
            // walk the loaded KML object DOM
            // var node = $(this.element).tree('add', {
            //         id: 'publicdatalayers',
            //         name: 'Public Data Layers',
            //         classname: 'marinemap-tree-category',
            //         context: true,
            //         // collapsible: true
            // });
            var self = this;
            var topNode;
            gex.dom.walk({
                visitCallback: function(context){
                    var child = $(self.element).tree('add', {
                        name: this.getName() || "No name specified in kml",
                        parent: context.current,
                        collapsible: !(this == kmlObject) && this.getType() == 'KmlFolder',
                        hideByDefault: false,
                        toggle: !(this == kmlObject),
                        classname: (this == kmlObject) ? 'marinemap-tree-category' : undefined,
                        checked: this.getVisibility()
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
        },
        
        remove: function(options){
            
        },
        
        refresh: function(kml){
            
        },
        
        getKmlObject: function(url){
            
        }
    }

    $.widget('marinemap.kmlForest', KMLForest);
    
    $.extend($.marinemap.kmlForest, {
        getter: ['getKmlObject'],
        defaults: {
            animate: false
        }
    });
    
})(jQuery);