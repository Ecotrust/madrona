(function($){
    var KMLForest = {
        
        _init: function(opts){
            console.log('init');
            this.ge = this.options.ge;
            this.gex = this.options.gex;
            this.element.addClass('marinemap-kml-forest');
            this.kmlObjects = {};
            $(this.element).tree({animate: false})
                .bind('itemToggle', function(e, clickedData, checked){
                    console.log(e, clickedData, checked);
                    for(var i=0; i<clickedData.length; i++){
                        var node = clickedData[i];
                        console.log(node, node.data('kml'));
                        
                        var kml = $(node).data('kml');
                        console.log(kml);
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

        add: function(url, opts){
            console.log('add');
            var options = opts || {};
            // pdl = $('#treetest').tree('add', {
            //     id: 'publicdatalayers',
            //     name: 'Public Data Layers',
            //     classname: 'marinemap-tree-category',
            //     context: true
            // });
            // loadKml('http://marinemap.org/kml_test/Public%20Data%20Layers.kmz');
            // var url=url+'?nodcache=True';
            var self = this;
            google.earth.fetchKml(this.ge, url + '?' + (new Date).valueOf(),
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
                self.addKmlObject(kmlObject);
            });            
        },
        
        addKmlObject: function(kmlObject){
            console.log('addKmlObject');
            this.ge.getFeatures().appendChild(kmlObject);
            this._buildTreeUI(kmlObject);
        },
        
        _buildTreeUI: function(kmlObject){
            console.log('_buildTreeUI');
            // walk the loaded KML object DOM
            var node = $(this.element).tree('add', {
                    id: 'publicdatalayers',
                    name: 'Public Data Layers',
                    classname: 'marinemap-tree-category',
                    context: true,
                    // collapsible: true
            });
            var self = this;
            gex.dom.walk({
                visitCallback: function(context){
                    var child = $(self.element).tree('add', {
                        name: this.getName(),
                        parent: context.current,
                        collapsible: this.getType() == 'KmlFolder',
                        hideByDefault: false,
                        toggle: true,
                        checked: this.getVisibility()
                    });
                    console.log(this.getType());
                    child.data('kml', this);
                    console.log(child.data('kml'));
                    context.child = child;
                },
                rootContext: node,
                rootObject: kmlObject
            });
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
            // uses micro-templating. 
            // See http://ejohn.org/blog/javascript-micro-templating/
            defaultItemTemplate: '<li><h3><%= name %></h3></li>',
            categoryTemplate: '<li><h2><img src="<%= ( obj.icon ? icon : "/marinemap/media/images/silk/icons/folder.png") %>" width="9" height="9" /><%= label %></h2></li>',
            idProperty: 'id',
            modelProperty: 'model',
            modelTemplates: {},
            scrollEl: false,
            contextMenu: function(event, element, id){
                
            },
            animate: true
        }
    });
    
})(jQuery);