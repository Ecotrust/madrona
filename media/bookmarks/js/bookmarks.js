function setupBookmarkFeatureUI() {
    $('#bookmark-close').click(function(){
        $('.cancel_button').click();
        $('#bookmark-close').hide();
        return false;
    });

    $('#bookmark-menu-link').click( function(e) {
        e.preventDefault();
        var url = "/features/bookmark/form/";
        var panelOpts = {
            loading_msg: 'Loading Bookmark Form',
            showClose: true
        };
        var panel = lingcod.editors[0].panel;

        function setupForm(form, options){
            options = options || {};
            var el = panel.getEl();
            el.find('.close').hide();
            el.find('input[type=submit]').hide();
            var manipulator;

            opts = {
                // Forcing submission of content thru iframe all the time
                iframe: true,
                beforeSubmit: function(a,b,c) {
                    panel.spin('Please wait while we save your bookmark.');
                    $(that).trigger('saving', ["Saving changes"]);
                    return true;
                },
                success: function(text, status, req, formel){
                    $(that).trigger('doneSaving');
                    if(text.match('<form') || text.match('<FORM')){ // for ie8
                        // Validation error
                        // Set default panel options. panel is an instance var
                        var panelOpts = {
                            loading_msg: 'Loading form', 
                            // loading_msg: 'Loading ' + action.title, 
                            // ^^^ action.title was causing js error and stalling the app 
                            // when a form was returned with validation errors
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
                            tree.refresh();
                            alert('There was an error saving your feature.');
                        }else{
                            $(lingcod.editors[0]).trigger('edit', [text, status, req, this]);
                        }
                    }
                }
            };
            var a = $(form).attr('action');
            if(typeof a !== 'undefined') {
                if(a[a.length - 1] !== '/'){
                    // For the benefit of IE
                    $(form).attr('action', a + '/');
                }
            }
            $(form).ajaxForm(opts);

            el.find('.submit_button').click(function(){
                $('#bookmark-close').hide();
                form.trigger('submit');
            });
            el.find('.cancel_button').click(function(){
                $('#bookmark-close').hide();
                panel.close();
                if(options.cancel){
                    options.cancel();
                }
            });
            var tabs = el.find('.tabs');
            tabs.bind('tabsshow', function(e){
                var div = $(this).parent().parent().parent();
                // scroll to 1, then 0 for the benefit of dumb firefox
                div.scrollTop(1);
                div.scrollTop(0);
            });
            tabs.tabs('select', '#PanelAttributes');
            tabs.tabs('disable', 0);
            tabs.find('> .ui-tabs-nav').hide();            
            if(tabs && tabs.length && $('.errorlist').length){
                tabs.tabs('select', '#PanelAttributes');
            }
            panel.show();
            if($('#PanelAttributes').length){
                $('#PanelAttributes').parent().parent().parent().parent().scrollTop(1).scrollTop(0);                
            }

            $(that).trigger('form_shown', [panel, null]);
        };
        ///////////////////////////END setupForm///////////////////////

        // bind the setupForm function that can be called by content of the panel
        lingcod.setupForm = function(form){
            setupForm(form);
        }
        //lingcod.menu_items.closeAll();
        //$('.panelMask').hide();
        panel.showUrl(url, panelOpts);
    });
}
