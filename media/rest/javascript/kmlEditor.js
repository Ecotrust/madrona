lingcod.rest.kmlEditor = function(options){
    
    if(!options || !options.url || !options.appendTo || !options.gex || !options.ge || !options.div || !options.client){
        throw('kmlEditor needs url, appendTo, ge, gex, client, and div options');
    }
                    
    var kmlLoaded = function(e, kml){
        tbar.setEnabled(true);
        $(tree).unbind('kmlLoaded', kmlLoaded);
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
    
    var refresh = function(callback){
        tbar.setEnabled(false);
        var cback = function(e, kmlObject){
            tbar.setEnabled(true);
            $(tree).unbind('kmlLoaded', cback);
            callback(e, kmlObject);
        }
        $(tree).bind('kmlLoaded', cback);
        tree.refresh(true);
        setSelectionMenuItemEnabled(false);
    }
    
    that.refresh = refresh;
    
    var setSelectionMenuItemEnabled = function(enabled){
        for(var i=0;i<enableWhenSelected.length;i++){
            enableWhenSelected[i].setEnabled(enabled);
        }
    }
    
    var tbar = new goog.ui.Toolbar();
    var create_menu = new goog.ui.Menu();

    if (!options.shared) {
        var create_button = new goog.ui.ToolbarMenuButton('Create New', create_menu);
        tbar.addChild(create_button, true);
        goog.events.listen(create_menu, 'action', function(e) {
            tree.clearSelection();
            options.client.create(e.target.mm_data, {
                success: function(location){
                    refresh(function(){
                        var node = tree.getNodesById(location);
                        tree.selectNode(node, tree.lookup(node));
                        options.client.show(tree.lookup(node));
                    });
                },
                error: function(){
                    alert('An error occured while saving your data. If the problem persists, please contact an administrator at help@marinemap.org.');
                }
            });
        });
    }
    
    // For testing purposes only, will be removed on launch
    var ref = new goog.ui.ToolbarButton('Refresh');
    ref.setEnabled(true);
    goog.events.listen(ref, 'action', function(e) {
        refresh();
    });
    tbar.addChild(ref, true);
    
    tbar.addChild(new goog.ui.ToolbarSeparator(), true);
        
    
    var attr = new goog.ui.ToolbarButton('Attributes');
    attr.setEnabled(false);
    attr.setTooltip("Show the selected feature's attributes");
    goog.events.listen(attr, 'action', function(e) {
        options.client.show(tree.lookup(that.selected));
    });
    tbar.addChild(attr, true);
    
    if (!options.shared) {
        var edit = new goog.ui.ToolbarButton('Edit');
        edit.setEnabled(false);
        goog.events.listen(edit, 'action', function(e) {
            tbar.setEnabled(false);
            options.ge.setBalloon(null);
            var kmlObject = tree.lookup(that.selected);
            kmlObject.setVisibility(false);
            options.client.update(kmlObject, {
                success: function(location){
                    tbar.setEnabled(true);
                    refresh(function(){
                        var node = tree.getNodesById(location);
                        tree.selectNode(node, tree.lookup(node));
                        options.client.show(tree.lookup(node));
                    });
                },
                cancel: function(){
                    tbar.setEnabled(true);
                    kmlObject.setVisibility(true);
                    tree.selectById(kmlObject.getId());
                },
                error: function(){
                    tbar.setEnabled(true);
                    alert('An error occured while saving your data. If the problem persists, please contact an administrator at help@marinemap.org.');
                    kmlObject.setVisibility(true);
                    tree.selectById(kmlObject.getId());
                }
            });
        });
        tbar.addChild(edit, true);
    }

    if (!options.shared) {
        var del = new goog.ui.ToolbarButton('Delete');
        del.setEnabled(false);
        goog.events.listen(del, 'action', function(e) {
            tbar.setEnabled(false);
            var kmlObject = tree.lookup(that.selected);
            options.client.destroy(kmlObject, {
                success: function(location){
                    tbar.setEnabled(true);
                    refresh();
                },
                error: function(){
                    tbar.setEnabled(true);
                    alert('An error occured while trying to delete this feature.');
                },
                cancel: function(){
                    tbar.setEnabled(true);
                }
            });
        });
        tbar.addChild(del, true);
    }


        
    var export_menu = new goog.ui.Menu();
    // export_menu.addItem(new goog.ui.MenuItem('to kml (Google Earth)'));
    // export_menu.addItem(new goog.ui.MenuItem('to shapefile'));
    var export_button = new goog.ui.ToolbarMenuButton('Export', export_menu);
    export_button.setEnabled(false);
    tbar.addChild(export_button, true);
    
    if (options.allow_copy) {
        var copy = new goog.ui.ToolbarButton('Copy');
        copy.setEnabled(false);
        copy.setTooltip("Copy the selected feature");
        goog.events.listen(copy, 'action', function(e) {
            kmlObject = tree.lookup(that.selected);
            options.client.copy(kmlObject, {
                success: function(location){
                    tbar.setEnabled(true);
                    // MP TODO : If we're in the shared shapes panel,
                    // switch to myshapes and refresh on that kml-tree
                    refresh(function(){
                        tree.clearSelection();
                        var node = tree.getNodesById(location);
                        tree.selectNode(node, tree.lookup(node));
                        // options.client.show(tree.lookup(node));
                    });
                },
                error: function(){
                    tbar.setEnabled(true);
                    alert('An error occured while copying. If the problem persists, please contact an administrator at help@marinemap.org.');
                    kmlObject.setVisibility(true);
                    tree.selectById(kmlObject.getId());
                }
            });
        });
        tbar.addChild(copy, true);
    }
    
    if (!options.shared) {
        var share = new goog.ui.ToolbarButton('Share');
        share.setEnabled(false);
        share.setTooltip("Share the selected feature");
        goog.events.listen(share, 'action', function(e) {
            options.client.share(tree.lookup(that.selected), {
                success: function(){
                    tbar.setEnabled(true);
                    refresh();
                }
            });
        });
        tbar.addChild(share, true);
    }
    
    if (options.shared && options.allow_copy) {
        var enableWhenSelected = [attr, export_button, copy];
    } else if (options.shared && !options.allow_copy) {
        var enableWhenSelected = [attr, export_button];
    } else {
        var enableWhenSelected = [attr, edit, del, export_button, copy, share];
    }

    
    tbar.render(that.el.find('.toolbar')[0]);

    $(options.appendTo).append(that.el);
    
    var visitFunction = function(kmlObject, config){
        var kml = lingcod.parseKml(kmlObject.getKml());
        var self = kml.find('kml>Placemark>[nodeName=atom:link][rel=self], kml>NetworkLink>[nodeName=atom:link][rel=self], kml>Folder>[nodeName=atom:link][rel=self]');
        if(self.length === 1){
            config.fireEvents = true;
            config.select = true;
            config['customClass'] = self.attr('mm:model') || '';
        }
        return config;
    };
    
    var tree = lingcod.kmlTree({
        url: options.url,
        ge: options.ge, 
        gex: options.gex, 
        animate: false, 
        map_div: options.div, 
        element: that.kmlEl,
        trans: lingcod.options.media_url + 'common/images/transparent.gif',
        title: false,
        visitFunction: visitFunction,
        bustCache: true,
        restoreState: true,
        supportItemIcon: true
    });
    that.tree = tree;
    
    that.clearSelection = tree.clearSelection;
    
    $(tree).bind('select', function(e, node, kmlObject){
        if(options.client.inShowState){
            var selectedTab = options.client.panel.getEl().find('.ui-tabs-selected:first a').text();
            options.client.show(kmlObject, {success: function(){
                options.client.panel.getEl().find('.ui-tabs li:contains('+selectedTab+') a').click();
            }});
        }
        that.selected = node;
        setSelectionMenuItemEnabled(!!node);
        // clear export menu
        while(export_menu.getItemCount() > 0){
            var item = export_menu.getItemAt(0);
            export_menu.removeItemAt(0);
            item.dispose();
        }
        if(that.selected){
            addExportItems(export_menu, kmlObject);
        }
    });
    
    var addExportItems = function(menu, kmlObject){
        lingcod.parseKml(kmlObject.getKml()).find('kml>Folder>[nodeName=atom:link][rel=alt], kml>NetworkLink>[nodeName=atom:link][rel=alt], kml>Placemark>[nodeName=atom:link][rel=alt],').each(function(){
            var title = $(this).attr('title');
            var href = $(this).attr('href');
            var item = new goog.ui.MenuItem(title);
            menu.addItem(item);
            goog.events.listen(item, 'action', function(e) {
                window.location = href;
            });
        });
    }
    
    $(tree).bind('dblclick', function(e, node, kmlObject){
        options.client.show(kmlObject);
    });
    
    $(options.client).bind('saving', function(e, msg){
        tree.showLoading(msg);
    });
    
    $(options.client).bind('doneSaving', function(e, msg){
        tree.hideLoading();
    });
    
    
    tbar.setEnabled(false);
    $(tree).bind('kmlLoaded', kmlLoaded);
    tree.load(true);
    
    return that;
}
