
/**
 * Creates a new Formats object.
 *  Do not create an indeterminent number of these components or it may result in
 *  memory leaks
 *
 * @constructor
 */
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
    var loader;
    
    if(!that.options.showCloseButton){
        s = 'display:none';
    }
    
    var close = '<a style="'+s+'" class="close" href="#"><img src="'+lingcod.options.media_url+'common/images/close.png" width="17" height="16" /></a>';
    
    var other_classes = that.options.scrollable ? '' : 'marinemap-panel-noscroll';
    var el = $('<div style="display:none;" class="marinemap-panel '+other_classes+'"><div class="loadingMask"><span>Loading</span></div><div class="panelMask"></div>'+close+'<div class="content container_12"><div class="panel"></div></div></div>');
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
        if(loader && loader.destroy){
            loader.destroy();
        }
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
    
    // Returns the names of all open tabs as a list, ie: root->parent->child
    var getActiveTabs = function(element, list){
        var list = list || [];
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
    
    that.showUrl = function(url, options){
        that.spin(options.load_msg || "Loading");
        $(that).trigger('panelloading');        
        loader = lingcod.contentLoader($.extend({}, {
            url: url,
            activeTabs: options.syncTabs ? getActiveTabs(el) : false,
            error: options.error,
            behaviors: applyBehaviors,
            target: el.find('.content'),
            beforeCallbacks: function(){
                that.stopSpinning();
                el.find('a.close').show();
                that.show();
            }
        }, options));
        loader.load();
    };
    
    // Applies default behaviors for sidebar content that are defined by css
    // classes and html tags such as datagrids, links that open in the same 
    // sidebar, tooltips, etc.
    // 
    // New functions will be added to this section over time, and 
    // documentation should be added to the sidebar-content author guide.
    var applyBehaviors = function(el){
        
        // Any link with a 'panel_link' class is overridden to open within the 
        // same panel.
        // WARNING: the link needs to be in a block-level container 
        // (p, div, span, etc). Also, since it uses ajax calls, the host must 
        // be the same
        el.find('a.panel_link').click( function(e) {
            that.showUrl( $(this).attr('href') ,options);
            e.preventDefault();
        });
    }    
    
    // Methods needed for test management
    that.destroy = function(){
        that.getEl().remove();
        if(that.shown){
            that.close();
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


// Takes an html fragment and extracts and stores and style or script tags
// from it. The resulting html can then be added to the page. This class also
// exposes a method for adding stylesheets to the page and extracting 
// callbacks within the content and providing them with references to the tabs
// they are to be associated with.
lingcod.layout.SanitizedContent = function(html){
    
    // these instance variables will be available, but are not 
    // particularly useful. Use instance methods instead.
    this.js = [];
    this.styles = [];
    this.html;
    
    var rscript = /<script(.|\s)*?\/script>/g;
    var rstyle = /<style(.|\s)*?\/style>/g;
    
    // extract script tags. NOT intended to work for src="..."-type tags
    var matches = html.match(rscript);
    if(matches){
        for(var i = 0; i<matches.length; i++){
            var match = matches[i];
            this.js.push(matches[i].replace(/<script(.|\s)*?>/, '')
                .replace('</script>', ''));
        }
    }
    
    // extract style tags
    var matches = html.match(rstyle);
    if(matches){
        for(var i = 0; i<matches.length; i++){
            this.styles.push({
                id: $(matches[i]).attr('id'),
                style: matches[i].replace(/<style(.|\s)*?>/, '').replace('</style>', '')
            });
        }            
    }
    
    // Set an instance variable to the html fragment with style and css
    // tags removed
    this.html = jQuery.trim(html.replace(rstyle, '').replace(rscript, ''));
    return this;
};

// Adds new style tags to the head of the document that were found in the
// sanitized fragment. If a style tag has an ID attribute, and has already
// been added to the document, it won't be added again.
lingcod.layout.SanitizedContent.prototype.addStylesToDocument = function(){
    for(var i = 0; i < this.styles.length; i++){
        var style = this.styles[i];
        if(!style.id || $('#'+style.id).length < 1){
            var ss1 = document.createElement('style');
            if(style.id){
                $(ss1).attr('id', style.id);
            }
            ss1.setAttribute("type", "text/css");
            if (ss1.styleSheet) {   // IE
                ss1.styleSheet.cssText = style.style;
            } else {                // the world
                var tt1 = document.createTextNode(style.style);
                ss1.appendChild(tt1);
            }
            var hh1 = document.getElementsByTagName('head')[0];
            hh1.appendChild(ss1);
        }
    }
};

// Extracts all callbacks defined in the html fragment by onPanelShow and
// onTabShow calls and returns them as an object with keys 'tabs'
// and 'panel'. 'tabs' is an object keyed 
lingcod.layout.SanitizedContent.prototype.extractCallbacks = function(){
    var returnObj = {
        panel: {},
        tabs: {}
    };
    
    // Create functions for the eval'd code to call
    
    function addCallback(type, target, callback){
        if(target && !callback){
            callback = target;
            target = false;
        }
        if(target){
            if(!returnObj.tabs[target]){
                returnObj.tabs[target] = {};
            }
            if(!returnObj.tabs[target][type]){
                returnObj.tabs[target][type] = [];
            }
            returnObj.tabs[target][type].push(callback);            
        }else{
            if(!returnObj.panel[type]){
                returnObj.panel[type] = [];
            }
            returnObj.panel[type].push(callback);
        }        
    }
    
    lingcod.onShow = function(target, callback){
        addCallback('show', target, callback);
    };
    
    lingcod.onHide = function(target, callback){
        addCallback('hide', target, callback);
    };
    
    lingcod.onUnhide = function(target, callback){
        addCallback('unhide', target, callback);
    };
    
    lingcod.beforeDestroy = function(target, callback){
        if(!callback){
            callback = target;
        }
        addCallback('destroy', false, callback);
    };
    
    // will create a script tag, append it so it runs, then remove the tag
    jQuery.globalEval(this.js.join(';\n'));
    
    // remove the event registration functions to ensure no overlap
    // lingcod.onShow = lingcod.onHide = lingod.onUnhide = lingcode.beforeDestroy = false;
    
    return returnObj;
}

lingcod.layout.SanitizedContent.prototype.cleanHtml = function(){
    return this.html;
}

// contentLoader loads the specified url in a hidden staging area. The 
// callback function provides a reference to the loaded content, which should 
// be moved into a space for interaction with the user.
// This function can be called with just a url and callback, or with an 
// optional opentabs argument. This argument should be an array of tab names
// (in order) that should be opened before firing the callback.
// 
// Examples
// lingcod.contentLoader('/my/url.html', ['firstTab', 'childTab'], function(domRef){
//      $(domRef).detach();
//      $('#sidebar .content').append(domRef);
// });
lingcod.contentLoader = (function(){
    
    return function(options){
        
        if(!options.url || !options.target){
            throw('lingcod.contentLoader: must specify a url and target');
        }
        
        options.error = options.error || function(){ 
            alert('error loading content from '+options.url);
        };
        
        options.beforeCallbacks = options.beforeCallbacks || function(){};
        options.afterCallbacks = options.afterCallbacks || function(){};
        options.success = options.success || function(){};
        
        var that = {};
        var callbacks = false;
        var still_staging = true;
        var staging = $('<div class="marinemap-panel-staging"></div>');
        $(document.body).prepend(staging);
        
        // Finds any onShow callbacks via the mm:onshow data attribute and fires
        // them unless instance.still_staging is true
        function fireCallbacks(types, el){
            if(typeof types === 'string'){
                types = [types];
            }
            el.each(function(){
                var a = $(this);
                var callbacks = a.data('mm:callbacks');
                if(callbacks){
                    for(var j = 0; j < types.length; j++){
                        var type = types[j];
                        if(!still_staging && callbacks[type] && callbacks[type].length){
                            for(var i = 0; i < callbacks[type].length; i++){
                                callbacks[type][i]();
                            }
                            if(type === 'show' || type === 'destroy'){
                                delete callbacks[type];
                            }
                        }
                    }
                    a.data('mm:callbacks', callbacks);                    
                }
            });
        };
                
        // removes script and style tags from html and returns. Also Adds 
        // found style tags to the document and assigns callbacks defined in 
        // those script tags to 'callbacks'. Meant to be assigned to 
        // dataFilter option of a jQuery.ajax call.
        var dataFilter = function(html, type){
            if(callbacks){
                throw('callbacks not handled before fetching new content!');
            }
            var content = new lingcod.layout.SanitizedContent(html);
            content.addStylesToDocument();
            callbacks = content.extractCallbacks();
            return content.cleanHtml();
        };
        
        // Finds any div with a class of .tabs and applies the jqueryui tabs
        // widget to it with suitable options.
        var enableTabs = function(el){
            var tabs = el.find('div.tabs');
            if(tabs.length){
                tabs.tabs({
                    'spinner': '<img id="loadingTab" src="'+lingcod.options.media_url+'common/images/small-loader.gif" />loading...', 
                    ajaxOptions: {
                        error: function(){
                            $('#loadingTab').parent().parent().remove();
                            alert('An error occured attempting to load this tab. If the problem persists, please contact help@marinemap.org for assistance.');
                        },
                        dataFilter: dataFilter
                    },
                    load: function(event, ui){
                        var p = $(ui.panel);
                        enableTabs(p);
                        attachCallbacks($(ui.tab));
                        // Fire the newly loaded tab's callbacks
                        fireCallbacks(['show', 'unhide'], $(ui.tab));
                        // Fire events of any subtabs of the loaded tab that 
                        // are selected
                        fireCallbacks(['show', 'unhide'], p.find('.ui-tabs-selected a'));
                        var after = $(ui.tab).data('mm:aftershow');
                        if(after && !$(ui.tab).parent().hasClass('ui-state-processing')){
                            $(ui.tab).removeData('mm:aftershow')
                            after();
                        }
                    },
                    show: function(event, ui){
                        fireCallbacks(['show', 'unhide'], $(ui.tab));
                        // first find disabled tabs at this level and fire callbacks
                        $(this).find('ul.ui-tabs-nav:first a').each(function(){
                            if(!$(this).parent().hasClass('ui-tabs-selected')){
                                fireCallbacks('hide', $(this));
                            }
                        });
                        // find now-hidden selected subtabs and fire callbacks
                        var selected_subtab = $(this).find('.ui-tabs-hide li.ui-tabs-selected a');
                        if(selected_subtab.length){
                            fireCallbacks('hide', selected_subtab);
                        }
                        fireCallbacks(['show', 'unhide'], 
                            $(ui.panel).find('li.ui-tabs-selected a'));
                        var after = $(ui.tab).data('mm:aftershow');
                        if(after && !$(ui.tab).parent().hasClass('ui-state-processing')){
                            $(ui.tab).removeData('mm:aftershow')
                            after();
                        }
                    },
                    cache: true
                });
            }
        };
        
        // Used to sync open tabs with another panel if options.activeTabs is 
        // populated. Recursively calls itself while opening async tabs.
        var followTabs = function(element, callback){
            if(options.activeTabs && options.activeTabs.length > 0){
                var t = options.activeTabs.shift();
                var link = element.find('div.tabs > ul li a').filter(function(){
                    return $(this).text() === t;
                });
                if(link.length === 0){
                    followTabs(null, callback);
                    return;
                }
                var tabs = link.parent().parent().parent();
                // enableTabs(tabs.parent());
                var cback = function(){
                    attachCallbacks(tabs);
                    followTabs(tabs, callback);
                };
                if(link.parent().hasClass('ui-tabs-selected')){
                    cback();
                }else{
                    link.data('mm:aftershow', cback);
                    link.click();                        
                }
            }else{
                callback();
            }
        };
        
        // Given an element, will assign onPanelShow callbacks to that 
        // element. It will also find any tabs within the element associated
        // with callbacks['tabs'] callbacks and assign them. Uses jQuery.data
        // function and adds callbacks using a key of "mm:onshow"
        var attachCallbacks = function(el){
            el.data('mm:callbacks', callbacks['panel']);
            if(callbacks.tabs){
                if(el.is('a')){
                    var el = el.parent().parent().parent()
                        .find(el.attr('href'));
                }
                for(var key in callbacks['tabs']){
                    var t = el.find('.ui-tabs-nav li a[href='+key+']');
                    t.data('mm:callbacks', callbacks.tabs[key]);
                }
            }
            callbacks = false; // must do this or error will be thrown            
        };

        that.destroy = function(){
            fireCallbacks('destroy', $(jQuery.merge(options.target.toArray(), options.target.find('.tabs, .ui-tabs-nav li a').toArray())));            
        };

        that.load = function(){
            $.ajax({
                url: options.url,
                dataFilter: dataFilter,
                error: options.error,
                success: function(data, status, xhr){
                    staging.html(data);
                    if(options.behaviors){
                        options.behaviors(staging);
                    }
                    enableTabs(staging);
                    attachCallbacks(staging);
                    followTabs(staging, function(){
                        // move staged content to target
                        options.target.html('');
                        var contents = staging.children();
                        contents.detach();
                        options.target.append(contents);
                        // fire callbacks
                        options.beforeCallbacks();
                        still_staging = false;
                        fireCallbacks(['show', 'unhide'], staging);
                        fireCallbacks(['show', 'unhide'], contents.find('.ui-tabs-selected a'));
                        options.target.data('mm:callbacks', staging.data('mm:callbacks'));
                        options.afterCallbacks();
                        options.success();
                        staging.remove();
                    });
                }
            });
        };
        return that;
    };
    
})();
