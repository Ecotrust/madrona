lingcod.rest.kmlEditor = function(options){
    
    if(!options || !options.url || !options.appendTo || !options.gex || !options.ge || !options.div || !options.client){
        throw('kmlEditor needs url, appendTo, ge, gex, client, and div options');
    }
                    
    var kmlLoaded = function(kml){
        var configs = options.client.parseDocument(kml.getKml());
        while(create_menu.getItemCount() > 0){
            create_menu.removeItemAt(0);
        }
        for(var key in configs){
            var config = configs[key];
            var item = new goog.ui.MenuItem(config.title);
            create_menu.addItem(item);
            item.mm_data = config;
        }
        that.kmlEl.addClass('kmlEditor');
        var a = that.kmlEl.find('> .marinemap-tree-category > a');
        that.kmlEl.find('> .marinemap-tree-category > span.badges').remove();
        that.el.find('h1').text(a.text());        
        a.hide();
    }
    
    var that = {};
    
    that.el = $('<div class="kmlEditor"><h1 class="name"></h1><div class="toolbar"></div><div class="kmllist"></div></div>');
    
    that.kmlEl = that.el.find('.kmllist');
    
    var tbar = new goog.ui.Toolbar();
    var create_menu = new goog.ui.Menu();
    var create_button = new goog.ui.ToolbarMenuButton('Create New', create_menu);
    tbar.addChild(create_button, true);
    goog.events.listen(create_menu, 'action', function(e) {
        options.client.create(e.target.mm_data, {
            success: function(location){
                // possible memory leak!!!!!!!
                forest.refresh(options.url, {
                    cachebust: true, 
                    callback: kmlLoaded                    
                });
            }
        });
    });
    tbar.addChild(new goog.ui.ToolbarSeparator(), true);
    
    var attr = new goog.ui.ToolbarButton('Attributes');
    attr.setEnabled(false);
    tbar.addChild(attr, true);
    
    var edit = new goog.ui.ToolbarButton('Edit');
    edit.setEnabled(false);
    tbar.addChild(edit, true);
        
    var export_menu = new goog.ui.Menu();
    export_menu.addItem(new goog.ui.MenuItem('to kml (Google Earth)'));
    export_menu.addItem(new goog.ui.MenuItem('to shapefile'));
    var export_button = new goog.ui.ToolbarMenuButton('Export', export_menu);
    export_button.setEnabled(false);
    tbar.addChild(export_button, true);
    
    var copy = new goog.ui.ToolbarButton('Copy');
    copy.setEnabled(false);
    tbar.addChild(copy, true);
    
    var share = new goog.ui.ToolbarButton('Share');
    share.setEnabled(false);
    tbar.addChild(share, true);
    
    
    tbar.render(that.el.find('.toolbar')[0]);

    $(options.appendTo).append(that.el);
    
    var forest = lingcod.kmlForest({
        ge: options.ge, 
        gex: options.gex, 
        div: options.div,
        element: that.kmlEl
    });
    
    // $(forest.tree).bind('itemClick', function(){
    //     console.log('itemClick hayooo!', this);
    // });
    
    forest.add(options.url, {
        cachebust: true, 
        callback: kmlLoaded
    });
    
    return that;
}