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
    
    // var create_menu_children = function(){
    //     var children = [];
    //     var attr = new goog.ui.MenuItem('View Attributes');
    //     children.push(attr);
    //     var edit = new goog.ui.MenuItem('Edit');
    //     children.push(edit);
    //     var copy = new goog.ui.MenuItem('Copy');
    //     children.push(copy);
    //     var share = new goog.ui.MenuItem('Share');
    //     children.push(share);
    //     children.push(new goog.ui.MenuSeparator());
    //     return children;
    // }
    
    var refresh = function(){
        forest.refresh(options.url, {
            cachebust: true, 
            callback: kmlLoaded                    
        });
        setSelectionMenuItemEnabled(false);
    }
    
    var setSelectionMenuItemEnabled = function(enabled){
        for(var i=0;i<enableWhenSelected.length;i++){
            enableWhenSelected[i].setEnabled(enabled);
        }
    }
    
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
                setSelectionMenuItemEnabled(false);
            },
            error: function(){
                alert('An error occured while saving your data. If the problem persists, please contact an administrator at help@marinemap.org.');
            }
        });
    });
    tbar.addChild(new goog.ui.ToolbarSeparator(), true);
    
    var attr = new goog.ui.ToolbarButton('Attributes');
    attr.setEnabled(false);
    attr.setTooltip("Show the selected feature's attributes");
    goog.events.listen(attr, 'action', function(e) {
        options.client.show(that.selected.data('kml'));
    });
    tbar.addChild(attr, true);
    
    var edit = new goog.ui.ToolbarButton('Edit');
    edit.setEnabled(false);
    goog.events.listen(edit, 'action', function(e) {
        var kmlObject = that.selected.data('kml');
        options.gex.dom.removeObject(kmlObject);
        options.client.update(kmlObject, {
            success: function(location){
                refresh();
            },
            cancel: function(){
                options.ge.getFeatures().appendChild(kmlObject);
            },
            error: function(){
                alert('An error occured while saving your data. If the problem persists, please contact an administrator at help@marinemap.org.');
                options.ge.getFeatures().appendChild(kmlObject);
            }
        });
    });
    tbar.addChild(edit, true);

    var del = new goog.ui.ToolbarButton('Delete');
    del.setEnabled(false);
    goog.events.listen(del, 'action', function(e) {
        var kmlObject = that.selected.data('kml');
        options.client.destroy(kmlObject, {
            success: function(location){
                refresh();
            },
            error: function(){
                alert('An error occured while trying to delete this feature.');
            }
        });
    });
    tbar.addChild(del, true);


        
    var export_menu = new goog.ui.Menu();
    // export_menu.addItem(new goog.ui.MenuItem('to kml (Google Earth)'));
    // export_menu.addItem(new goog.ui.MenuItem('to shapefile'));
    var export_button = new goog.ui.ToolbarMenuButton('Export', export_menu);
    export_button.setEnabled(false);
    tbar.addChild(export_button, true);
    
    var copy = new goog.ui.ToolbarButton('Copy');
    copy.setEnabled(false);
    tbar.addChild(copy, true);
    
    var share = new goog.ui.ToolbarButton('Share');
    share.setEnabled(false);
    tbar.addChild(share, true);
    
    var enableWhenSelected = [attr, edit, del, export_button, copy, share];
    
    tbar.render(that.el.find('.toolbar')[0]);

    $(options.appendTo).append(that.el);
    
    // var pm = new goog.ui.PopupMenu();
    // var items = create_menu_children();
    // for(var i=0;i<items.length; i++){
    //     pm.addItem(items[i]);
    // }
    
    var forest = lingcod.kmlForest({
        ge: options.ge, 
        gex: options.gex, 
        div: options.div,
        element: that.kmlEl
        // contextMenu: pm
    });
    
    $(forest.tree).bind('itemSelect', function(e, selected, previously){
        that.selected = selected;
        setSelectionMenuItemEnabled(!!selected);
        // clear export menu
        while(export_menu.getItemCount() > 0){
            var item = export_menu.getItemAt(0);
            export_menu.removeItemAt(0);
            item.dispose();
        }
        if(that.selected){
            var kmlObject = that.selected.data('kml');
            addExportItems(export_menu, kmlObject);
        }
    });
    
    var addExportItems = function(menu, kmlObject){
        $(kmlObject.getKml()).find('atom\\:link[rel=alt]').each(function(){
            var title = $(this).attr('title');
            var href = $(this).attr('href');
            var item = new goog.ui.MenuItem(title);
            menu.addItem(item);
            goog.events.listen(item, 'action', function(e) {
                window.location = href;
            });
        });
    }
    
    $(forest.tree).bind('itemDoubleClick', function(e, item){
        var kmlObject = item.data('kml');
        if(kmlObject && $(kmlObject.getKml()).find('atom\\:link[rel=self]').length === 1){
            options.client.show(item.data('kml'));
        }
    });
    
    // $(forest.tree).bind('itemContext', function(e, d, item){
    //     var kmlObject = item.data('kml');
    //     if(kmlObject && $(kmlObject.getKml()).find('atom\\:link[rel=self]').length === 1){
    //         var pm = new goog.ui.PopupMenu();
    //         var items = create_menu_children();
    //         for(var i=0;i<items.length; i++){
    //             pm.addItem(items[i]);
    //         }
    //         pm.render(document.body);
    // 
    //         pm.attach(
    //             item[0],
    //             goog.positioning.Corner.TOP_LEFT,
    //             goog.positioning.Corner.BOTTOM_LEFT);
    // 
    //         // pm.attach(item[0]);
    //     }
    // });
    
    forest.add(options.url, {
        cachebust: true, 
        callback: kmlLoaded
    });
    
    return that;
}