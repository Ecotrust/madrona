// Provides an editable instance of kmltree whose behavior is driven by the 
// contents of a workspace document linked to within the target kml file
lingcod.features.kmlEditor = (function(){
    
    // Static Methods
    // ##############
    
    function checkOptions(opts){
        if(!opts || !opts.url || !opts.appendTo || !opts.gex || !opts.panel){
            throw('kmlEditor needs url, appendTo, panel and gex options');
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
        that.panel = options.panel;
        
        // private vars
        var panel = that.panel;
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
        var menus = [];
        var buttons = [];
        var selection;
        // Keep track of previously selected items turned off for editing, in
        // case the user chooses to cancel
        var previousSelection;
        var selectedKmlObjects;
        
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
            that.refresh();
        });
        tbar.addChild(refresh_button, true);
        buttons.push(refresh_button);
        
        tbar.addChild(new goog.ui.ToolbarSeparator(), true);
        
        // add the create button and menu
        create_menu = new goog.ui.Menu();
        create_button = new goog.ui.ToolbarMenuButton('Create New', create_menu);
        create_button.setVisible(false);
        menus.push(create_menu);
        tbar.addChild(create_button, true);
        goog.events.listen(create_menu, 'action', onAction);
        
        // Add attributes button
        attr = new goog.ui.ToolbarButton('');
        attr.setEnabled(false);
        attr.setVisible(false);
        attr.setTooltip("Show the selected feature's attributes");
        goog.events.listen(attr, 'action', onAction);
        tbar.addChild(attr, true);

        // Add edit menu
        edit_menu = new goog.ui.Menu();
        edit_button = new goog.ui.ToolbarMenuButton('Edit', edit_menu);
        edit_button.setEnabled(false);
        edit_button.setVisible(false);
        tbar.addChild(edit_button, true);
        goog.events.listen(edit_menu, 'action', onAction);
        
        
        // Add Downloads/export menu
        download_menu = new goog.ui.Menu();
        download_button = new goog.ui.ToolbarMenuButton('Download', download_menu);
        download_button.setEnabled(false);
        download_button.setVisible(false);
        tbar.addChild(download_button, true);        
        goog.events.listen(download_menu, 'action', onAction);


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

        $(tree).bind('kmlLoaded', onKmlLoad);
        
        $(tree).bind('kmlLoaded', function(event, kmlObject){
            $(that).trigger('kmlLoaded', [event, kmlObject]);
        });
        
        $(tree).bind('dblclick', function(e, kmlObject){
            attr.dispatchEvent('action');
        });
        
        $(tree).bind('kmlLoadError', function(){
            // tbar.setEnabled(true);
            create_button.setEnabled(false);
        });

        $(tree).bind('select', onSelect);
        
        // render the toolbar
        tbar.render(that.el.find('.toolbar')[0]);
        $(options.appendTo).append(that.el);
        
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
            if(selection){
                return;
            }   
            // tbar.setEnabled(true);
            that.workspace = lingcod.features.workspace(data);
            populateCreateMenu(create_menu, create_button, that.workspace);
            populateEditMenu(edit_menu, edit_button, that.workspace);
            populateDownloadMenu(download_menu, download_button, that.workspace);
            attr.action = that.workspace.actions.getByRel('self')[0];
            attr.setCaption(that.workspace.actions.getByRel('self')[0].title);
            attr.setVisible(true);
            refresh_button.setEnabled(true);
        }
        
        function populateCreateMenu(menu, button, workspace){
            while(menu.getItemCount() > 0){
                menu.removeItemAt(0);
            }
            var createActions = workspace.actions.getByRel('create');
            // If there are no actions, disable the menu
            if(createActions.length < 1){
                button.setEnabled(false);
                button.setVisible(false);
            }else{
                button.setVisible(true);
                // button.setEnabled(true);
                jQuery.each(createActions, function(i, action){
                    var item = new goog.ui.MenuItem(action.title);
                    item.action = action;
                    menu.addItem(item);
                });              
            }   
        }
        
        function populateEditMenu(menu, button, workspace){
            while(menu.getItemCount() > 0){
                menu.removeItemAt(0);
            }
            var actions = workspace.actions.getByRel('edit');
            // If there are no actions, disable the menu
            if(actions.length < 1){
                button.setEnabled(false);
                button.setVisible(false);
            }else{
                jQuery.each(actions, function(i, action){
                    var item = new goog.ui.MenuItem(action.title);
                    item.setEnabled(false);
                    item.action = action;
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
            var actions = workspace.actions.getByRel('related');
            // If there are no actions, disable the menu
            if(actions.length < 1){
                button.setEnabled(false);
                button.setVisible(false);
            }else{
                jQuery.each(actions, function(i, action){
                    var item = new goog.ui.MenuItem(action.title);
                    item.setEnabled(false);
                    item.action = action;
                    menu.addItem(item);
                });
                // button.setEnabled(true);
                button.setVisible(true);
            }
            // menu.addItem(new goog.ui.MenuSeparator());
            var as = new goog.ui.MenuItem('as file type...');
            menu.addItem(as);
            as.setEnabled(false);
            var actions = workspace.actions.getByRel('alternate');
            // If there are no actions, disable the menu
            if(actions.length < 1){
                button.setEnabled(false);
                button.setVisible(false);
            }else{
                jQuery.each(actions, function(i, action){
                    var item = new goog.ui.MenuItem(action.title);
                    item.setEnabled(false);
                    item.action = action;
                    menu.addItem(item);
                });
                // button.setEnabled(true);
                button.setVisible(true);
            }
        }
        
        function onSelect(e, selectData){
            if(selectData.length !== 1){
                attr.setEnabled(false);
            }else{
                attr.setEnabled(true);                
            }
            selectData = jQuery.map(selectData, function(d){
                return d.kmlObject;
            });
            selectedKmlObjects = selectData;
            selection = jQuery.map(selectData, function(d){
                return d.getId();
            });
            var i = tbar.getChildCount();
            while(i){
                i--;
                if(child === attr || child === refresh_button){
                    continue;
                }
                var child = tbar.getChildAt(i);
                if(child instanceof goog.ui.ToolbarMenuButton){
                    var menu = child.getMenu();
                    var enabled = false;
                    var j = menu.getChildCount();
                    while(j != 0){
                        j--;
                        var item = menu.getChildAt(j);
                        if(item.action){
                            var active = item.action.active(selectData);
                            if(active){
                                enabled = true;
                                item.setEnabled(true);
                            }else{
                                item.setEnabled(false);                                
                            }
                        }
                    }
                    child.setEnabled(enabled);
                }
            }
        }
        
        // Responds to click on any MenuItem. Each MenuItem has an action 
        // attribute referencing an action from the workspace document. This
        // even listener performs the first component of that action, such as:
        // 
        //      rel = alternate || related
        //          opens the link in a new tab
        // 
        //      rel = self
        //          opens the link in the sidebar
        // 
        //      rel = edit && method = GET
        //          opens the link (likely a form) in the sidebar
        //
        //      rel = edit && ( method = DELETE || method = POST )
        //          performs the specified non-idempotent method on the link
        // 
        // This listener IS NOT responsible for handling the consequent 
        // changes related to non-idempotent actions. For those, onChange must
        // be called to do things such as refresh a kmlEditor instance, select
        // a feature, and/or open new sidebar content.
        function onAction(e){
            previouslySelected = [];
            var action = e.target.action;
            // Set default panel options. panel is an instance var
            var panelOpts = {
                loading_msg: 'Loading ' + action.title,
                showClose: true
            };
            if(!selection || selection.length === 0){
                // In some cases dblclicking a feature on the map results in
                // an empty selection. Oddly only in firefox so far.
                return;
            }
            // Get the specific link from this action, whether generic or not, 
            // that applies to the current selection. Note selection is a 
            // private instance variable set by the onSelect handler
            var link = action.getLink(selection);
            // First check if the user even wants to perform the action before
            // proceeding if a confirm message is provided.
            if(link.confirm){
                if(!confirm(link.confirm)){
                    return;
                }
            }
            // Compile the uri-template against the current selection
            var url = action.getUrl(selection);

            if(link.method === 'GET'){
                // Self and edit links are the only links opened in the 
                // sidebar
                if(action.rel === 'self'){
                    panel.showUrl(url, panelOpts);
                }else if(action.rel in {alternate: 1, related: 1}){
                    // Open all alternate and related links in a new tab. It 
                    // is up to the server to set the Content-Type and
                    // Content-Disposition headers for correct handling by the 
                    // browser
                    window.open(url, '_blank');
                }else{
                    if(action.rel==='create'){
                        tree.clearSelection();
                    }
                    // likely an edit form. It will be up to the panel 
                    // component to appropriately handle forms.
                    panelOpts['showCloseButton'] = false;
                    panelOpts['success'] = function(){
                        lingcod.setupForm = function(){
                            alert('error:setupForm called after clearing?');
                        };
                    }
                    // set a setupForm function that can be called by content
                    // of the panel
                    lingcod.setupForm = function(form){
                        setupForm(form);
                    }
                    panelOpts['loading_msg'] = 'Loading form';
                    panel.showUrl(url, panelOpts);
                    return;
                    
                }
            }else if(link.method === 'DELETE' || link.method === 'POST'){
                tree.clearSelection();
                spin('Performing action');
                $.ajax({
                    url: url,
                    type: link.method,
                    dataType: 'text',
                    error: onError,
                    success: onChange,
                    context: {
                        action: action,
                        link: link
                    }
                });
            }else{
                alert('invalid link method "'+link.method+'"');
            }
        }
                
        function setupForm(form, options){
            options = options || {};
            var el = panel.getEl();
            el.find('.close').hide();
            el.find('input[type=submit]').hide();
            var manipulator;
            if($('#PanelGeometry').length){
                if(selectedKmlObjects.length){
                    selectedKmlObjects[0].setVisibility(0);
                    previouslySelected = selectedKmlObjects[0];                    
                }
                var tabs = el.find('.tabs');
                tabs.bind('tabsshow', function(e){
                    var div = $(this).parent().parent().parent();
                    // scroll to 1, then 0 for the benefit of dumb firefox
                    div.scrollTop(1);
                    div.scrollTop(0);
                });
                // so this is how it might work:
                // var manipulations_needed = manipulators.needed(form);
                var manipulator = new lingcod.Manipulator(gex, form, $('#PanelGeometry'), $('#map_container'));
                $(manipulator).bind('processing', function(){
                    panel.spin('Processing your shape');
                });
                $(manipulator).bind('doneprocessing', function(){
                    panel.stopSpinning();            
                });
                if(manipulator && manipulator.needed){
                    tabs.tabs('select', '#PanelGeometry');
                }else{
                    manipulator = false;
                    tabs.tabs('select', '#PanelAttributes');
                    tabs.tabs('disable', 0);
                    tabs.find('> .ui-tabs-nav').hide();            
                }                
            }

            opts = {
                // Forcing submission of content thru iframe all the time, no
                // matter whether a file upload field is associated with the 
                // feature. I hate using iframes for this, but they are 
                // necessary for uploads so we may as well be consistent in 
                // their use with all forms.
                iframe: true,
                beforeSubmit: function(a,b,c) {
                    if(manipulator){
                        var errMsg = false;
                        if(manipulator.isDefiningShape()){
                            if(manipulator.isInvalidGeometry()){
                                errMsg = 'The shape you defined is invalid. Please correct any mistakes using the Geometry form.';
                            }else if(manipulator.isDefiningNewShape()){
                                errMsg = 'You must finish defining your shape before creating this feature. Double-Click on the last vertex to finish drawing your shape.';
                            }else{
                                errMsg = 'You must finish defining your shape before creating this feature. Click "Done Editing", when you are finished';
                            }
                        }else if(manipulator.isShapeDefined() === false){
                            errMsg = 'You must create a geometry for this feature before continuing. Click on "Draw Shape" to begin.';
                        }
                        if(errMsg){
                            tabs.tabs('select', '#PanelGeometry');
                            alert(errMsg);
                            return false;
                        }else{
                            // can proceed with form submission
                            manipulator.destroy();
                        }
                    }
                    panel.spin('Saving changes');
                    $(that).trigger('saving', ["Saving changes"]);
                    return true;
                },
                success: function(text, status, req, formel){
                    $(that).trigger('doneSaving');
                    if(text.match('<form')){
                        // Validation error
                        // Set default panel options. panel is an instance var
                        var panelOpts = {
                            loading_msg: 'Loading ' + action.title,
                            showClose: true
                        };
                        panelOpts['showCloseButton'] = false;
                        panelOpts['success'] = function(){
                            lingcod.setupForm = function(){
                                alert('error:setupForm called after clearing?');
                            };
                        }
                        // set a setupForm function that can be called by content
                        // of the panel
                        lingcod.setupForm = function(form){
                            setupForm(form);
                        }
                        panel.close();
                        panel.stopSpinning();
                        panel.showText(text, panelOpts);
                    }else{
                        panel.close();
                        panel.stopSpinning();
                        var info = jQuery.parseJSON(text);
                        if(info['status'] != 200 && info['status'] != 201){
                            unspin();
                            alert('There was an error saving your feature.');
                        }else{
                            onChange(text, status, req);
                        }
                    }
                }
            };
            $(form).ajaxForm(opts);

            el.find('.submit_button').click(function(){
                form.trigger('submit');
            });
            el.find('.cancel_button').click(function(){
                if(previouslySelected){
                    previouslySelected.setVisibility(true);                    
                }
                if(manipulator){
                    manipulator.destroy();
                }
                panel.close();
                if(options.cancel){
                    options.cancel();
                }
            });
            if(tabs && tabs.length && $('.errorlist').length){
                tabs.tabs('select', '#PanelAttributes');
            }
            panel.show();
            if($('#PanelAttributes').length){
                $('#PanelAttributes').parent().parent().parent().parent().scrollTop(1).scrollTop(0);                
            }

            $(that).trigger('form_shown', [panel, null]);
        };
        
        function onError(xhr, status, errorThrown){
            alert('failed to perform '+
                this.action.title+' action.\n'+status+'\n'+errorThrown);
            unspin();
        }
        
        function onChange(data, status, xhr){
            unspin();
            // It's now up to lingcod.js to determine which editor needs to 
            // perform a refresh, selection, etc
            // Delegating to lingcod.js should give us more flexibility. There
            // is no way to tell kmlEditor whether it is the shared component
            // or the myshapes component. the original design was intended to
            // support flexible numbers of kmleditors to be defined so this
            // wouldn't make much sense. anyhoo...
            $(that).trigger('edit', [data, status, xhr, this]);
        }
        
        function spin(msg){
            tbar.setEnabled(false);
            tree.showLoading(msg);
        }
        
        function unspin(){
            tbar.setEnabled(true);
            tree.hideLoading();
        }
        
        // Public API methods
        // ##################
        
        that.clearSelection = tree.clearSelection;
        
        that.refresh = function(callback){
            tbar.setEnabled(false);
            var cback = function(e, kmlObject){
                tbar.setEnabled(true);
                create_button.setEnabled(true);
                callback(e, kmlObject);
            }
            $(tree).one('kmlLoaded', cback);
            tree.refresh(true);
        };
                
        return that;
    }
})();