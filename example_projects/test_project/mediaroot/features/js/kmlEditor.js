// Provides an editable instance of kmltree whose behavior is driven by the 
// contents of a workspace document linked to within the target kml file
lingcod.features.kmlEditor = (function(){
    
    // Static Methods
    // ##############
    
    function checkOptions(opts){
        if(!opts || !opts.url || !opts.appendTo || !opts.gex){
            throw('kmlEditor needs url, appendTo, and gex options');
        }
        return opts;
    }

    
    // Constructor
    return function(options){
        
        options = checkOptions(options);
        
        // public api
        var that = {};
        
        // public vars
        that.workspace;
        that.tree;
        that.el;
        
        // private vars
        var tbar;
        var create_menu;
        var refresh_button;
        var tree;
        var kmlEl;
        var create_button;
        var attr;
        var edit;
        var download_button;
        var download_menu;
        var edit_button;
        var edit_menu;
        
        // Create html skeleton for the editor, toolbar menu, and tree
        that.el = $([
            '<div class="kmlEditor">',
                '<h1 class="name"></h1>',
                '<div class="toolbar"></div>',
                '<div class="kmllist kmlEditor"></div>',
            '</div>'
        ].join(''));
        
        kmlEl = that.el.find('.kmllist');
        
        // Setup toolbar as much as possible before workspace is loaded
        tbar = new goog.ui.Toolbar();
        // tbar.setEnabled(false);
        
        // add refresh button
        refresh_button = new goog.ui.ToolbarButton('Refresh');
        refresh_button.setEnabled(false);
        goog.events.listen(refresh_button, 'action', function(e) {
            refresh();
        });
        tbar.addChild(refresh_button, true);
        
        tbar.addChild(new goog.ui.ToolbarSeparator(), true);
        
        // add the create button and menu
        create_menu = new goog.ui.Menu();
        create_button = new goog.ui.ToolbarMenuButton('Create New', create_menu);
        create_button.setVisible(false);
        tbar.addChild(create_button, true);
        
        // Add attributes button
        attr = new goog.ui.ToolbarButton('');
        attr.setEnabled(false);
        attr.setVisible(false);
        attr.setTooltip("Show the selected feature's attributes");
        goog.events.listen(attr, 'action', function(e) {
            // options.client.show(lookup(that.selected));
        });
        tbar.addChild(attr, true);

        // Add edit menu
        edit_menu = new goog.ui.Menu();
        edit_button = new goog.ui.ToolbarMenuButton('Edit', edit_menu);
        edit_button.setEnabled(false);
        edit_button.setVisible(false);
        tbar.addChild(edit_button, true);
        
        // Add Downloads/export menu
        download_menu = new goog.ui.Menu();
        download_button = new goog.ui.ToolbarMenuButton('Download', download_menu);
        download_button.setEnabled(false);
        download_button.setVisible(false);
        tbar.addChild(download_button, true);
        
        
        
        
        // goog.events.listen(create_menu, 'action', function(e) {
        //     console.log(e.target.link);
        //     tree.clearSelection();
        //     options.client.create(e.target.mm_data, {
        //         success: function(location){
        //             refresh(function(){
        //                 var node = tree.getNodesById(location);
        //                 tree.selectNode(node, lookup(node));
        //                 options.client.show(lookup(node));
        //             });
        //         },
        //         error: function(){
        //             alert('An error occured while saving your data. If the problem persists, please contact an administrator at help@marinemap.org.');
        //         }
        //     });
        // });


        // render the toolbar

        // create the instance of kmltree
        var tree = kmltree({
            url: options.url,
            gex: options.gex,
            mapElement: $('#map'), 
            element: kmlEl,
            bustCache: true,
            restoreState: true,
            supportItemIcon: true,
            multipleSelect: true,
            selectable: true
        });
        
        that.tree = tree;
        tree.load();
        
        tbar.render(that.el.find('.toolbar')[0]);
        
        $(options.appendTo).append(that.el);

        

        $(tree).bind('kmlLoaded', onKmlLoad);
        
        $(tree).bind('kmlLoaded', function(event, kmlObject){
            $(that).trigger('kmlLoaded', [event, kmlObject]);
        });
        
        $(tree).bind('kmlLoadError', function(){
            // tbar.setEnabled(true);
            create_button.setEnabled(false);
        });
        
        function onKmlLoad(e, kmlObject){
            var kml = $($.parseXML(kmlObject.getKml()));
            var link = kml.find('[nodename=atom:link][rel=workspace]');
            if(link.length < 1){
                alert('kml file did not have workspace document link');
            }
            $.ajax({
                url: link.attr('href'),
                dataType: 'json',
                success: onWorkspaceLoad,
                error: function(){
                    // tbar.setEnabled(true);
                    alert('error loading workspace document');
                }
            });
            // var a = that.kmlEl.find('> .marinemap-tree-category > a');
            // that.kmlEl.find('> .marinemap-tree-category > span.badges').remove();
            // that.el.find('h1').text(a.text());        
            // a.hide();
        }
        
        function onWorkspaceLoad(data, textStatus){            
            // tbar.setEnabled(true);
            that.workspace = lingcod.features.workspace(data);
            populateCreateMenu(create_menu, create_button, that.workspace);
            populateEditMenu(edit_menu, edit_button, that.workspace);
            populateDownloadMenu(download_menu, download_button, that.workspace);
            attr.setCaption(that.workspace.actions.getByRel('self')[0].title);
            attr.setVisible(true);
            refresh_button.setEnabled(true);
        }
        
        function populateCreateMenu(menu, button, workspace){
            while(menu.getItemCount() > 0){
                menu.removeItemAt(0);
            }
            var createLinks = workspace.actions.getByRel('create');
            // If there are no links, disable the menu
            if(createLinks.length < 1){
                button.setEnabled(false);
                button.setVisible(false);
            }else{
                button.setVisible(true);
                // button.setEnabled(true);
                jQuery.each(createLinks, function(i, link){
                    var item = new goog.ui.MenuItem(link.title);
                    item.link = link;
                    menu.addItem(item);
                });              
            }   
        }
        
        function populateEditMenu(menu, button, workspace){
            while(menu.getItemCount() > 0){
                menu.removeItemAt(0);
            }
            var links = workspace.actions.getByRel('edit');
            // If there are no links, disable the menu
            if(links.length < 1){
                button.setEnabled(false);
                button.setVisible(false);
            }else{
                jQuery.each(links, function(i, link){
                    var item = new goog.ui.MenuItem(link.title);
                    item.setEnabled(false);
                    item.link = link;
                    menu.addItem(item);
                });
                // button.setEnabled(true);
                button.setVisible(true);
            }   
        }
        
        function populateDownloadMenu(menu, button, workspace){
            while(menu.getItemCount() > 0){
                menu.removeItemAt(0);
            }
            var links = workspace.actions.getByRel('related');
            // If there are no links, disable the menu
            if(links.length < 1){
                button.setEnabled(false);
                button.setVisible(false);
            }else{
                jQuery.each(links, function(i, link){
                    var item = new goog.ui.MenuItem(link.title);
                    item.setEnabled(false);
                    item.link = link;
                    menu.addItem(item);
                });
                // button.setEnabled(true);
                button.setVisible(true);
            }
            // menu.addItem(new goog.ui.MenuSeparator());
            var as = new goog.ui.MenuItem('as file type...');
            menu.addItem(as);
            as.setEnabled(false);
            var links = workspace.actions.getByRel('alternate');
            // If there are no links, disable the menu
            if(links.length < 1){
                button.setEnabled(false);
                button.setVisible(false);
            }else{
                jQuery.each(links, function(i, link){
                    var item = new goog.ui.MenuItem(link.title);
                    item.setEnabled(false);
                    item.link = link;
                    menu.addItem(item);
                });
                // button.setEnabled(true);
                button.setVisible(true);
            }
        }
                
        return that;
    }
})();