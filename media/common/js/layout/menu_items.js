lingcod.menu_items = (function(){
    var that = {};
    
    that.panels = [];
    
    var init = function(el){
        that.el = el;
        that.el.find('li.item').each(function(){
            self = $(this);
            var els = $('<a style="display:none;" class="close" href="#"><img src="'+lingcod.options.media_url+'common/images/tool_window_pointer.png" width="23" height="36" /></a></a>');
            els.click(function(){
                closeAll();
                return false;
            });
            self.append(els)
            that.menuLink = self.find('span a');
            that.menuLink.click(function(){
                closeAll();
                var parent = $(this).parent().parent()[0];
                openItem(parent);
                return false;
            });
            var href = that.menuLink.attr('href');
            var content = $(href);
            if(content){
                var panel = lingcod.panel({
                    content: content,
                    hideOnly: true,
                    showCloseButton: false
                });
                panel.getEl().css('z-index', '11');
                $.data(self[0], 'panel', that.panels.length)
                that.panels.push(panel);
            }
        });
    }
    
    that.init = init;
    
    var closeAll = function(){
        var open = that.el.find('li.item.toggled');
        if(open.length === 1){
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
    }
    
    that.closeAll = closeAll;
    
    var openItem = function(item){
        lingcod.maskSidebar();
        item = $(item);
        item.addClass('toggled');
        item.find('a.close').show();
        if(item.data('panel') || item.data('panel') === 0){
            var panel = that.panels[item.data('panel')];
            panel.show();
        }else{
            // console.log('couldnt get index');
        }
    }
    
    that.openItem = openItem;
    
    return that;
})();