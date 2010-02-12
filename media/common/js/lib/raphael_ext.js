Raphael.el.anim = function(opts){
    if(opts['with']){
        if(opts['easing']){
            this.animateWith(opts['with'], opts['attrs'], opts['ms'], opts['callback']);
        }else{
            this.animateWith(opts['with'], opts['attrs'], opts['ms'], opts['easing'], opts['callback']);
        }
    }else{
        if(opts['easing']){
            this.animate(opts['attrs'], opts['ms'], opts['callback']);
        }else{
            this.animate(opts['attrs'], opts['ms'], opts['easing'], opts['callback']);
        }        
    }
};