(function($){

    $.widget("ui.panel", {
        _init: function() {
            if(this.element.find('ul.tabs')){
                this.element.tabs({selected: 0});
            }
            if(this.options.toptabs){
                this.element.find('.sidebar-header h1').hide();
            }
            if (this.options.hidden){
                this.hide();
            }
            if(this.options.html){
                this.element.html(this.options.html);
            }
            // set size
            this.element.width(this.options.width);
            this.element.height(this.options.height)
            if(this.options.title){
                this.title(this.options.title);
            }
            this.resize({width: this.options.width, height: this.options.height});
        },

        title: function(title){
            if(!this.element.find('h1').length){
                this.element.prepend('<h1>'+title+'</h1>');
            }
            this.resize();
        },

        setContent: function(html){
            this.element.html(html);
        },

        resize: function(opts){
            opts = opts || {};
            opts.width = opts.width || this.element.width();
            opts.height = opts.height || this.element.height();
            this.element.width(opts.width);
            var h1 = this.element.find('.sidebar-header');
            var hh = 0;
            if(h1.length){
                hh = h1.outerHeight();
            }
            this.element.height(opts.height);
            var el = this.element;
            this.element.find('.sidebar-body').each(function(){
                var body = $(this);
                var footer = body.find('.sidebar-footer');
                footer.css('margin-top', 0);
                body.height(opts.height - hh);
                if(footer.length){
                    var wh = body.find('.sidebar-wrapper').height();
                    var bh = body.height();
                    if(wh < bh){
                        var diff = bh - wh;
                        footer.css('margin-top', diff);                        
                    }
                }
            });
        },
        
        width: function(){
            return this.element.outerWidth();
        },
        
        height: function(){
            return this.element.height();
        },
        
        hide: function(){
            this.element.css({
                position: 'absolute',
                left: '-1000px',
                top: '0px'
            });
        },
        
        // TODO: Beautify
        showSpinner: function(text){
            var text = text || "Loading...";
            
        },
        
        hideSpinner: function(){
            
        }
    });

    $.extend($.ui.panel, {
        getter: "width height",
        defaults: {
            hidden: true,
            width: 360,
            height: 400,
            html: false,
            tabs: false,
            title: null,
            toptabs: false
        }
    });
})(jQuery);
