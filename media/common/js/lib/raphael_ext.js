Raphael.el.anim = function(opts){
    if(opts['target']){
        if(opts['easing']){
            this.animateWith(opts['target'], opts['attrs'], opts['ms'], opts['callback']);
        }else{
            this.animateWith(opts['target'], opts['attrs'], opts['ms'], opts['easing'], opts['callback']);
        }
    }else{
        if(opts['easing']){
            this.animate(opts['attrs'], opts['ms'], opts['callback']);
        }else{
            this.animate(opts['attrs'], opts['ms'], opts['easing'], opts['callback']);
        }        
    }
};

Raphael.fn.anim = Raphael.el.anim;