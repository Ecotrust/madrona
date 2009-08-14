(function($){
    $.widget("ui.panelManager", {
        _init: function() {
            this.duration = 400;
            // uncomment if using animateFromRight/Left methods
            // this.easing = 'linear';
            this.stack = [];
            this.home = this.element.find('.sidebar-panel')[0];
            $(this.home).show();
            $(this.home).panel({hidden: false, toptabs: true});
            jQuery.data(this.home, 'index', 0);
            jQuery.data(this.home, 'href', '#');
            this.stack.push(this.home);
            this.index = 0;
            var self = this;
            this.element.find('a').live('click', function(e){
                var $a = $(this);
                var target = $a.attr('target');
                if(target == '_blank' || target == '_self'){
                    return true;
                }
                e.preventDefault();
                var href = $a.attr('href');
                
                if(href == '#js'){
                    // Link is used for a custom javascript event handler
                    return;
                }
                
                if(href == '#'){
                    // Link directly to home
                    self._popPanel(0);
                    return;
                }
                
                for(var i = 1; i < self.stack.length; i++){
                    // Check to see if link points to a panel that is 
                    // already in the stack
                    if(href == jQuery.data(self.stack[i], 'href')){
                        if(i == self.index){
                            $(this).fadeTo("slow", 0.5);
                        }else{
                            self._popPanel(i);
                        }
                        return;
                    }
                }
                
                if($a.hasClass('back_link') || $a.hasClass('backward')){
                    self._insertBefore($a);
                }else if($a.hasClass('switch')){
                
                }else{
                    self._appendPanel($a);
                }
            });
            // this.resize();
        },

        // Create an empty panel, assuming it will be loaded from an 
        // AJAX request
        createPanel: function(opts){
            opts.title = opts.title || 'Loading Panel...';
            var panel_opts = {
                width: this.element.width(),
                height: this.element.height(),
                hidden: false,
                html: 'spinner',
                title: opts.title
            };
            var panel = $('<div class="sidebar-panel" />');
            this.element.append(panel);
            panel.panel(panel_opts);
            return panel;
        },
        
        home: function(){
            return this.home;
        },
        
        // Resize the panelManager element and all it's children
        resize: function(opts){
            opts = opts || {};
            this.element.find('.sidebar-panel').panel('resize', opts);
            opts.width = opts.width || this.element.width();
            opts.height = opts.height || 
                this.element.find('.sidebar-panel').height();
            this.element.width(opts.width);
            this.element.height(opts.height);
        },
        
        // Show a panel, sliding it in from the right and adding to the stack
        _appendPanel: function(link){
            var panel = this.createPanel({title: $(link).attr('title')});
            this.stack.push(panel);
            jQuery.data(panel, 'index', this.stack.length - 1);
            // this.resize();
            this.index += 1;
            var href = $(link).attr('href');
            jQuery.data(panel, 'href', href);
            var self = this;
            $.ajax({
                url: href,
                success: function(data, s){
                    self._appendSuccess(data, s);
                },
                error: function(s){
                    self._panelLoadFail(s);
                },
                method: 'GET'
            });
            this._removeBackButton();
            var incoming = panel;
            var outgoing = $(this.stack[this.index - 1]);
            incoming.show('slide', {direction: 'right'}, this.duration);
            outgoing.hide('slide', {direction: 'left'}, this.duration);
            // this.animateFromRight();
            return panel;
        },
        
        // Called after the _appendPanel request finishes
        _appendSuccess: function(data, s){
            $data = $(data);
            var panel = $(this.stack[this.index]);
            var html = $data.find('.sidebar-panel').html();
            var back = $data.find('.back_link');
            // need to add back button to a property of the panel so it can be  
            // retrieved later
            if(!back.length){
                back = this.createBackButton();
            }
            $panel = $(panel);
            $panel.data('backButton', back);
            $panel.panel('setContent', 
            $data.find('.sidebar-panel').html());
            // $panel.panel('resize');
            $(this.element).trigger('panelChange', $panel);
            this._showBackButton(back);
        },
        
        // TODO: Make this pretty for the user
        _panelLoadFail: function(s){
            alert('loading of panel content failed. ' + s);
        },
        
        // Insert a panel from a url behind the current panel
        _insertBefore: function(link){
            var panel = this.createPanel({title: $(link).attr('title')});
            var end = this.stack.pop();
            this.stack.push(panel);
            jQuery.data(panel, 'index', this.stack.length - 1);
            this.stack.push(end);
            var href = $(link).attr('href');
            jQuery.data(panel, 'href', href);
            var self = this;
            $.ajax({
                url: href,
                success: function(data, s){
                    self._insertBeforeSuccess(data, s);
                },
                error: function(s){
                    self._panelLoadFail(s);
                },
                method: 'GET'
            });
            this._removeBackButton();
            $(end).hide('slide', {direction: 'right'}, this.duration);
            var current = self.stack.pop();
            $(panel).show('slide', {direction: 'left'}, this.duration, function(){
                $(current).panel('destroy').remove();                
            });
            return panel;            
        },
        
        // Called after _insertBefore request finishes
        _insertBeforeSuccess: function(data, s){
            $data = $(data);
            var panel = $(this.stack[this.index]);
            var html = $data.find('.sidebar-panel').html();
            var back = $data.find('.back_link');
            // need to add back button to a property of the panel so it can be  
            // retrieved later
            if(!back.length){
                back = this.createBackButton();
            }
            $panel = $(panel);
            $panel.data('backButton', back);
            $panel.panel('setContent', 
                $data.find('.sidebar-panel').html());
            // $panel.panel('resize');
            $(this.element).trigger('panelChange', [$panel]);
            // this._showBackButton(back);
            this._showBackButton(back);
        },
        
        // Removes panel from the stack, including all the panels above it, 
        // and slides in the panel below.
        // index defaults to the last panel in the stack
        // specify an index to pop a specified panel in the stack
        _popPanel: function(index){
            if(!index && index != 0){
                index = this.stack.length - 2;
            }
            var incoming = this.stack[index];
            index += 1;
            var outgoing = this.stack[this.index];
            this.index = index - 1;
            var self = this;
            this._removeBackButton();            
            $(incoming).show("slide", {direction: 'left'}, this.duration);
            $(outgoing).hide("slide", {direction: 'right'}, this.duration, function(){
                while(index < self.stack.length){
                    var current = self.stack.pop();
                    $(current).panel('destroy').remove();
                }                
                if(self.stack.length > 1){
                    !self._showBackButton($(incoming).data('backButton'));
                }
                $(self.element).trigger('panelChange', [$(incoming)]);
            });
        },

        _removeBackButton: function(){
            $(this.element).find('.back_link').remove();
        },
        
        _showBackButton: function(button){
            if(button){
                button.hide();
                $(this.element).append(button);
                $(button).fadeIn(500);
                return true;
            }else{
                return false;
            }
        },
        
        getStack: function(){
            return this.stack;
        }
        
        
        // Leaving these functions in place, since I may have to use them
        // again to fix some layout issues
        
        // Presumes the appropriate value is set on this.index
        // animateFromRight: function(callback){
        //     // Place in the waiting area on the right
        //     var incoming = $(this.stack[this.index]);
        //     var outgoing = $(this.stack[this.index - 1]);
        //     // get the incoming panel into position before animating
        //     incoming.css('top', 0);
        //     incoming.css('left', this.stagingRightX);
        //     $(incoming).panel('resize');
        //     $(incoming).addClass('active');
        //     $(outgoing).removeClass('active');
        //     incoming.animate({
        //         top: 0,
        //         left: 0
        //     }, this.duration, this.easing);
        //     
        //     var self = this;
        //     outgoing.animate({
        //         top: 0,
        //         left: this.element.width() * -1 - 10
        //     }, this.duration, this.easing, function(){
        //         // Callbacks are fired here since the outgoing animation 
        //         // finishes last
        //         $(this).hide();
        //         // if(self.index){
        //         //    
        //         // }
        //         if(callback){
        //             callback(incoming, outgoing);
        //         }
        //     });
        // },
        
        // Presumes the appropriate value is set on this.index
        // animateFromLeft: function(incoming, outgoing, callback){
        //     // var incoming = $(this.stack[this.index]);
        //     // var outgoing = $(this.stack[this.index + 1]);
        //     incoming = $(incoming);
        //     outgoing = $(outgoing);
        //     incoming.addClass('active');
        //     outgoing.removeClass('active');
        //     incoming.css({
        //         top: 0,
        //         left: this.stagingLeftX - 10
        //     });
        //     incoming.show();
        //     $(incoming).panel('resize');
        //     incoming.animate({
        //         top: 0,
        //         left: 0
        //     }, this.duration, this.easing, function(){
        //     });
        //     var self = this;
        //     outgoing.animate({
        //         top: 0,
        //         left: this.element.width() + 10
        //     }, this.duration, this.easing, function(){
        //         $(this).hide();
        //         if(callback){
        //             callback(incoming, outgoing);
        //         }
        //     });
        // }, 
        
    });

    $.extend($.ui.panelManager, {
        getter: "home createPanel getStack",
        defaults: {
            width: 360,
            height: 400
        }
    });
})(jQuery);
