// Do not create an indeterminent number of these components or it may result in
// memory leaks
lingcod.panel = function(options){
    
    var defaults = {
        hideOnly: false,
        showCloseButton: true,
        content: false,
        appendTo: window.document.body,
        scrollable: true
    }
    
    var that = {
        options: $.extend({}, defaults, options),
        shown: false
    };
    
    if(lingcod && lingcod.addPanel){
        lingcod.addPanel(that);
    }
    
    var s = '';
    if(!that.options.showCloseButton){
        s = 'display:none';
    }
    
    var close = '<a style="'+s+'" class="close" href="#"><img src="'+lingcod.options.media_url+'common/images/close.png" width="17" height="16" /></a>';
    
    var other_classes = that.options.scrollable ? '' : 'marinemap-panel-noscroll';
    var el = $('<div style="display:none;" class="marinemap-panel '+other_classes+'"><div class="loadingMask"><span>Loading</span></div><div class="panelMask"></div>'+close+'<div class="content container_12"></div></div>');
    el.data('panelComponent', that);
    var anotherel = el;
        
    el.find('a.close').click(function(){
        that.close();
    });
    
    var content = el.find('.content');
    
    $(that.options.appendTo).append(el);
    
    if(that.options.content && $(that.options.content).length){
        var c = $(that.options.content);
        c.remove();
        content.append(c);
    }

    that.showContent = function(elements, opts){
        that.addContent(elements);
        if(opts && opts.showClose){
            el.find('a.close').show();
        }
        that.show();
    }
    
    that.addContent = function(elements){
        if(!that.options.content){
            content.html('');
            content.append(elements);            
        }
    }
    
    that.show = function(animate){
        $(el[0]).show();
        $(el[0]).find('.marinemap-table').each(function(){
            lingcod.ui.table(this);
        });
        $(el[0]).scrollTop(0);
        that.shown = true;
        $(that).trigger('panelshow', that);       
    }
    
    that.close = function(){
        $(el[0]).scrollTop(1).scrollTop(0);
        if(options.showCloseButton === false){
            el.find('a.close').hide();
        }
        if(!that.options.hideOnly){
            el.hide();
            that.shown = false;
            el.find('div.content').html('');
            $(that).trigger('panelclose', that);
        }
    }
    
    that.spin = function(message){
        if(el.is(':visible')){
            el.find('.loadingMask span').text(message || "Loading")
            el.find('.loadingMask').show();
        }else{
            lingcod.showLoadingMask(message);
        }
    };
    
    that.stopSpinning = function(){
        lingcod.hideLoadingMask();
        el.find('.loadingMask').hide();
    };
    
    that.showError = function(title, message){
        
    };
    
    var getActiveTabs = function(element, list){
        var selected = element.find('.ui-tabs:first .ui-tabs-selected:first > a');
        var href = selected.attr('href');
        var name = selected.text()
        list.push(name);
        var panel = $(href);
        if(panel.find('.ui-tabs').length){
            getActiveTabs(panel, list);
        }
        return list;
    };
    
    var tabOptions = {
        'spinner': '<img id="loadingTab" src="'+lingcod.options.media_url+'common/images/small-loader.gif" />loading...', 
        ajaxOptions: {
            error: function(){
                $('#loadingTab').parent().parent().remove();
                alert('An error occured attempting to load this tab. If the problem persists, please contact help@marinemap.org for assistance.');
            },
            beforeSend: function(a){
                lingcod.loadingTabLink = el.find('.ui-tabs-nav >  .ui-state-processing a');
                if(!lingcod.loadingPanel){
                    lingcod.loadingPanel = el;                    
                }
            }
        },
        cache: true
    };
    
    var enableTabs = function(htmlEl, options){
        var options = options || tabOptions
        var tabs = htmlEl.find('.tabs');
        if(tabs.length){
            // tabOptions['idPrefix'] = String((new Date()).getTime());
            tabs = tabs.tabs(options);
            return tabs;
        }else{
            return false;
        }
    };
    
    var enableTabsWithListeners = function(htmlEl){
        var options = $.extend({}, tabOptions, {
            load: onTabsLoad,
            show: onTabsShow
        });
        enableTabs(htmlEl, options)
    };
    
    var addTabsListeners = function(tabs){
        tabs.each(function(){
            $(this).bind('tabsshow', onTabsShow);
            $(this).bind('tabsload', onTabsLoad);
        });
    };
    
    that.showUrl = function(url, options){
        var new_url = url;
        that.spin(options.load_msg || "Loading");
        $(that).trigger('panelloading');
        var activeTabs = [];
        if(options.syncTabs){
            getActiveTabs(el, activeTabs);
        }
        // Set a global var to point to this panel so callbacks can be assigned
        // if(!lingcod.loadingPanel){
            lingcod.loadingPanel = el;            
        // }else{
            // throw('ERROR: lingcod.loadingPanel already set!');
        // }
        $.ajax({
            url: url,
            method: 'GET',
            complete: function(response, status){
                showUrlCallback(response, status, activeTabs, options);
            }
        });
    };
    
    var onTabsLoad = function(event, ui){
        lingcod.loadingPanel = el;
        lingcod.loadingTabLink = ui.tab;
        enableTabsWithListeners($(this));

        // in affect an afterLoad event
        setTimeout(function(){
            lingcod.loadingPanel = false;
            
        }, 10);
    };
    
    
    var onTabsShow = function(event, ui){
        var callback = $(ui.tab).data('mm:ontabshow');
        if(callback){
            callback(ui);
            $(ui.tab).data('mm:ontabshow', false);
        }
    };
    
    
    // var attachTabListeners = function(tabs){
    //     tabs.each(function(){
    //         $(this).bind('tabsload', function(){
    //             
    //         });
    //     });
    // };
    
    var showUrlCallback = function(response, status, tabs, options){
        switch(response.status){
            case 200:
                var html = $('<div></div>');
                html[0].innerHTML = response.responseText;
                var html = html.children();                
                // Any link with a 'panel_link' class is overridden to open within the panel
                // WARNING: the link needs to be in a block-level container (p, div, span, etc)
                // Also, since it uses ajax calls, the host must be the same
                var panel_links = html.find('a.panel_link');
                panel_links.click( function(e) {
                    that.showUrl( $(this).attr('href') ,options);
                    e.preventDefault();
                });
                if(tabs.length > 0){
                    var staging = $('<div class="marinemap-panel-staging"></div>');
                    lingcod.loadingPanel = staging;
                    $(document.body).prepend(staging);
                    staging.html(html);
                    enableTabs(staging);
                    followTabs(staging, tabs, options);
                }else{
                    that.stopSpinning();
                    that.showContent(html, {showClose: options.showClose});
                    var tabs_present = enableTabsWithListeners(html);
                    lingcod.loadingPanel = false;
                    if(options && options.success){
                        options.success(response, status);
                    }
                }
                break;
                
            default:
                lingcod.loadingPanel = false;
                that.stopSpinning();
                that.showError('A Server Error Occured.', 
                    'Please try again.');
                    
                if(options && options.error){
                    options.error(response, status);
                }
                $(that).trigger('error', response, status);
        }
    };
    
    var followTabs = function(element, tabs_to_select, options){
        if(tabs_to_select.length > 0){
            var link = element.find('li a:contains('+tabs_to_select.shift()+')');
            if(link.length === 0){
                followTabs(element, [], options);
                return;
            }
            var tabs = link.parent().parent().parent();
            enableTabs(tabs.parent());
            var cback = function(){
                followTabs(element, tabs_to_select, options);
            }
            if(link.parent().hasClass('ui-tabs-selected')){
                cback();
            }else{
                $(tabs).bind('tabsshow', function(event, ui){
                    $(tabs).unbind('tabsshow');
                    cback();
                });
                // tabsshow fires before content is added to the document, so
                // this sloppy settimeout function is necessary.
                lingcod.loadingTabLink = link;
                setTimeout(function(){
                    link.click();
                }, 5);
            }
        }else{
            lingcod.loadingTabLink = false;
            lingcod.loadingPanel = false;
            var p = element.find('.panel')[0];
            $(el.find('.panel')[0]).replaceWith(p);
            element.remove();
            that.stopSpinning();
            addTabsListeners(el.find('.tabs'));
            // enableTabsWithListeners(el.find('.tabs'));
            el.find('.ui-tabs-selected a').each(function(){
                onTabsShow({}, {
                    tab: $(this), 
                    panel: el.find($(this).attr('href') + '.ui-tabs-panel')
                });
            });
            if(options && options.success){
                options.success();
            }
            // finished following
        }
    };
    
    // Methods needed for test management        
    that.destroy = function(){
        that.getEl().remove();
        if(lingcod && lingcod.removePanel){
            if(that.shown){
                that.close();
            }
            lingcod.removePanel(that);
        }
    }
    
    that.getEl = function(){
        return el;
    }
    
    that.hide = function(){
        $(el[0]).scrollTop(0);
        el.hide();
        that.shown = false;
        $(that).trigger('panelhide', that);
        if(options.showCloseButton === false){
            el.find('a.close').hide();
        }
        $(that).trigger('panelhide');
    }
                
    return that;
};

// Use within a template to fire a callback when the panel is loaded.
// Right now, it only supports content that was loaded as part of a tab.
// TODO: support callback for panels that contain no tabs
lingcod.onPanelShow = function(callback){
    if(lingcod.loadingTabLink){
        if(lingcod.loadingTabLink.is('a')){
            lingcod.loadingTabLink.data('mm:ontabshow', callback);            
        }else{
            throw('loadingTabLink is not a link');
        }
    }else{
        throw('loadingTabLink not found')
    }
};

// Use within a template to fire a callback when a specific tab within a panel
// Åis loaded.
lingcod.onTabShow = function(id, callback){
    if(!lingcod.loadingPanel){
        throw('attempting to set lingcod.onTabShow callback without loadingPanel set.');
    }
    var link = $(lingcod.loadingPanel).find('a[href='+id+']');
    if(link.length === 1){
        link.data('mm:ontabshow', callback);
    }else{
        throw('Could not find tab to assign callback: '+id);
    }
};
