lingcod.graphics = (function(){
    
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
        return ticZero;
    };
    
    ScaleBar.prototype.changeY = function(y, target, easing, duration){
        for(var i=0; i<this.tics.length;i++){
            var el = this.tics[i].changeY(y, easing, duration, target);
            if(!target){
                target = el;
            }
        }
    }
    
    var Tic = function(value, initial_position, paper, ticHeight, origin, color, showValue){
        this.path = paper.path(
            "M"+initial_position+' '+origin+'L'+initial_position+' '+(origin-ticHeight)
        );
        this.path.attr({'stroke': color});
        if(showValue){
            this.t = paper.text(initial_position, origin + 10, String(value));
            this.t.attr({'fill': color});
        }
        this.initial_position = initial_position;
        this.value = value;
        this.paper = paper;
    };
    
    Tic.prototype.changePosition = function(x, animate, animationEasing, animationDuration, animationTarget){
        var path = this.path.attr('path');
        var new_path = 'M'+ x + ' ' + path[0][2] + 'L' + x + ' ' + path[1][2];
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
            if(!animate){
                this.t.attr('x', x);
            }else{
                this.t.anim({
                    attrs: {x: x},
                    ms: animationDuration,
                    easing: animationEasing,
                    target: animationTarget
                });
            }
        }
    };
    
    Tic.prototype.changeY = function(y, easing, duration, target){
        var path = this.path.attr('path');
        var new_path = 'M'+ path[0][1] + ' ' + (path[0][2] + y)  + 'L' + path[1][1] + ' ' + (path[1][2] + y);
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
            this.t.anim({
                attrs: {y: this.t.attr('y') + y},
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