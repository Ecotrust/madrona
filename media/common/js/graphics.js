madrona.graphics = (function(){
    
    var ScaleBar = function(opts){
        // var s = "M"+opts.origin[0]+' '+opts.origin[1]+'L'+opts.origin[0] + opts.width+' '+opts.origin[1];
        // opts.paper.path(s);
        this.opts = opts;
        // Setup major ticks
        this.tics = [];
        var baseline = opts.origin[1] - 16;
        var position = opts.origin[0];
        var end = position + opts.width;
        var value = 0;
        // major tics
        while(value <= opts.maxValue){
            this.tics.push(
                new Tic(value, position, opts.paper, opts.ticHeight, baseline, opts.color, true)
            );
            var value = value + opts.majorInterval;
            var position = this.calculateXPosition(value, opts.width, opts.maxValue, opts.origin[0]);
        }
        
        // Setup minor ticks
        var position = opts.origin[0];
        var end = position + opts.width;
        var value = 0;
        var height = opts.ticHeight / 2;
        var b = baseline - (height / 2);
        while(value <= opts.maxValue){
            if(value % opts.majorInterval !== 0){
                this.tics.push(
                    new Tic(value, position, opts.paper, height, b, opts.color, false)
                );
            }
            var value = value + opts.minorInterval;
            var position = this.calculateXPosition(value, opts.width, opts.maxValue, opts.origin[0])
        }
        this.maxValue = opts.maxValue;
        if(opts.initialMaxValue){
            this.update(opts.initialMaxValue, false);
        }
        if(opts.label){
            this.label = opts.paper.text(opts.origin[0] + (opts.width / 2), opts.origin[1] + 15, opts.label);
        }
    };
    
    ScaleBar.prototype.calculateXPosition = function(value, width, maxValue, originX){
        return Math.round(((value / maxValue) * width) + originX);
    };
    
    ScaleBar.prototype.update = function(maxValue, animate){
        var ticZero = this.tics[0];
        var x = this.calculateXPosition(ticZero.value, this.opts.width, maxValue, this.opts.origin[0]);
        if(animate){
            ticZero.changePosition(x, true, this.opts.animationEasing, this.opts.animationDuration);
        }else{
            ticZero.changePosition(x, false);
        }
        for(var i=1;i<this.tics.length;i++){
            var tic = this.tics[i];
            var x = this.calculateXPosition(tic.value, this.opts.width, maxValue, this.opts.origin[0]);
            if(animate){
                tic.changePosition(x, true, this.opts.animationEasing, this.opts.animationDuration, ticZero);
            }else{
                tic.changePosition(x, false);
            }
        }
        this.maxValue = maxValue;
        // returns an animation target for additional animateWith calls
        return ticZero.path;
    };
    
    ScaleBar.prototype.changeY = function(y, target, easing, duration){
        for(var i=0; i<this.tics.length;i++){
            var el = this.tics[i].changeY(y, easing, duration, target);
            if(!target){
                target = el;
            }
        }
        if(this.label){
            this.label.anim({
                attrs: {y: this.label.attr('y') + y},
                easing: easing,
                ms: duration,
                target: target
            });
        }
    }
    
    var Tic = function(value, initial_position, paper, ticHeight, origin, color, showValue){
        this.y1 = (origin);
        this.y2 = ((origin-ticHeight));
        this.x = initial_position;
        this.path = paper.path(
            "M"+this.x+' '+this.y1+'L'+this.x+' '+this.y2
        );
        this.path.attr({'stroke': color});
        if(showValue){
            this.tx = initial_position;
            this.ty = origin + 10;
            this.t = paper.text(this.tx, this.ty, String(value));
            this.t.attr({'fill': color});
        }
        this.initial_position = initial_position;
        this.value = value;
        this.paper = paper;
    };
    
    Tic.prototype.changePosition = function(x, animate, animationEasing, animationDuration, animationTarget){
        this.x = x;
        var new_path = 'M'+ this.x + ' ' + this.y1 + 'L' + this.x + ' ' + this.y2;
        if(!animate){
            this.path.attr('path', new_path);
        }else{
            this.path.anim({
                attrs: {path: new_path},
                ms: animationDuration,
                easing: animationEasing,
                target: animationTarget
            });
        }
        if(this.t){
            this.tx = x;
            if(!animate){
                this.t.attr('x', this.tx);
            }else{
                this.t.anim({
                    attrs: {x: this.tx, y: this.ty},
                    ms: animationDuration,
                    easing: animationEasing,
                    target: animationTarget
                });
            }
        }
    };
    
    Tic.prototype.changeY = function(y, easing, duration, target){
        this.y1 = this.y1 + y;
        this.y2 = this.y2 + y;
        var new_path = 'M'+ this.x + ' ' + this.y1  + 'L' + this.x + ' ' + this.y2;
        this.path.anim({
            attrs: {path: new_path},
            ms: duration,
            easing: easing,
            target: target
        });
        if(!target){
            target = this.path;
        }
        if(this.t){
            this.ty = this.ty + y;
            this.t.anim({
                attrs: {y: this.ty},
                ms: duration,
                easing: easing,
                target: target           
            });
        }
        return target;
    }
    
    var that = {};
    
    that.ScaleBar = ScaleBar;

    return that;
})();