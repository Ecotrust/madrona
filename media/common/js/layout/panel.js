// Do not create an infinite number of these components or it may result in
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
    
    close = '<a style="'+s+'" class="close" href="#"><img src="'+lingcod.options.media_url+'common/images/close.png" width="17" height="16" /></a>';
    
    var other_classes = that.options.scrollable ? '' : 'marinemap-panel-noscroll';
    var el = $('<div style="display:none;" class="marinemap-panel '+other_classes+'">'+close+'<div class="content container_12"></div></div>');
    
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
    
    that.show = function(){
        $(el[0]).show();
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
        el.show();
    }
    
    that.showError = function(title, message){
        
    }
    
    that.showUrl = function(url, options){
        var new_url = url;
        that.spin(options.load_msg || "Loading");
        $.ajax({
            url: url,
            method: 'GET',
            complete: function(response, status){
                switch(response.status){
                    case 200:
                        var html = $(response.responseText);

                        that.showContent(html, {showClose: options.showClose});
                        var tabs = html.find('.tabs');
                        if(tabs.length){
                            tabs = tabs.tabs({'spinner': 'loading...'});
                            // tabs.tabs('select', '#Habitat');
                        }
                        if(options && options.success){
                            options.success(response, status);
                        }

                        // Any link with a 'panel_link' class is overridden to open within the panel
                        // WARNING: the link needs to be in a block-level container (p, div, span, etc)
                        // Also, since it uses ajax calls, the host must be the same
                        var panel_links = html.find('a.panel_link');
                        panel_links.click( function(e) {
                            that.showUrl( $(this).attr('href') ,options);
                            e.preventDefault();
                        });

                        // get content
                        // that.showContent
                        break;
                        
                    default:
                        that.showError('A Server Error Occured.', 
                            'Please try again.');
                            
                        if(options && options.error){
                            options.error(response, status);
                        }
                        $(that).trigger('error', response, status);
                }
            }
        });
    }
    
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
    }
                
    return that;
};
