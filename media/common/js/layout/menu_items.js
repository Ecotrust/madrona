lingcod.menu_items = (function(){
    var that = {};
    
    that.panels = [];
    
    var init = function(el){
        that.el = el;
        that.el.find('li.item').each(function(){
            var self = $(this);
            var els = $('<a style="display:none;" class="close" href="#"><img src="'+lingcod.options.media_url+'common/images/tool_window_pointer.png" width="23" height="36" /></a></a>');
            els.click(function(){
                closeAll();
                return false;
            });
            self.append(els)
            menuLink = self.find('span a');
            menuLink.click(function(){
                if(!that.el.hasClass('disabled')){
                    closeAll();
                    var parent = $(this).parent().parent()[0];
                    openItem(parent);                    
                }
                return false;
            });
            var href = menuLink.attr('href');
            var content = $(href);
            if(content){
                var panel = lingcod.panel({
                    scrollable: !self.hasClass('autosize'),
                    content: content,
                    hideOnly: true,
                    showCloseButton: false,
                    appendTo: $('#panel-holder')
                });
                panel.getEl().css('z-index', '11');
                panel.getEl().addClass('marinemap-menu-items');
                $.data(self[0], 'panel', that.panels.length)
                that.panels.push(panel);
            }
        });
    }
    
    that.init = init;
    
    var closeAll = function(){
        var open = that.el.find('li.item.toggled');
        if(open.length === 1){
            $('.marinemap-panel:visible').each(function(){
                $(this).find('.panelMask').hide();
            });
            open.removeClass('toggled')
            open.find('a.close').hide();
            open.each(function(){
                var item = $(this);
                var panel = that.panels[item.data('panel')];
                if(panel){
                    panel.hide();
                }else{
                }
            });
        }
        // lingcod.unmaskSidebar();
        
        // This is to prevent multiple menu items from appearing at once
        // BUT it causes some strange behavior: clicking on the bookmark edit form panel
        // causes the panel to close. Maybe having the bookmark panel PLUS the data layers
        // panel open at the same time *would* be desireable... "it's a feature not a bug" ? 
        // $("#bookmark-close").click();
    }
    
    that.closeAll = closeAll;
    
    var openItem = function(item){
        lingcod.maskSidebar();
        item = $(item);
        item.addClass('toggled');
        item.find('a.close').show();
        if(item.data('panel') || item.data('panel') === 0){
            $('.marinemap-panel:visible').each(function(){
                $(this).find('.panelMask').show();
            });
            var panel = that.panels[item.data('panel')];
            panel.show();
        }else{
            // couldn't get index
        }
    }
    
    that.openItem = openItem;
    
    var disable = function(){
        that.el.addClass('disabled');
    };
    
    that.disable = disable;
    
    var enable = function(){
        that.el.removeClass('disabled');
    };
    
    that.enable = enable;
    
    return that;
})();
