if(!window.lingcod){
    lingcod = {};
}

lingcod.geographicReport = (function(){
    
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
        while(value <= opts.maxValue){
            this.tics.push(
                new Tic(value, position, opts.paper, opts.ticHeight, baseline, opts.color, true)
            );
            var value = value + opts.majorInterval;
            var position = Math.round(((value / opts.maxValue) * opts.width) + opts.origin[0]);
        }
        
        // Setup minor ticks
        var position = opts.origin[0];
        var end = position + opts.width;
        var value = 0;
        var height = opts.ticHeight / 2;
        while(value <= opts.maxValue){
            if(value % opts.majorInterval !== 0){
                this.tics.push(
                    new Tic(value, position, opts.paper, height, baseline - (height / 2), opts.color, false)
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
        }else if(animationTarget){
            this.path.animateWith(animationTarget, {path: new_path}, animationDuration, animationEasing);
        }else{
            this.path.animate({path: new_path}, animationDuration, animationEasing);
        }
        if(this.t){
            if(!animate){
                this.t.attr('x', x);
            }else if(animationTarget){
                this.t.animateWith(animationTarget, {x: x}, animationDuration, animationEasing);
            }else{
                this.t.animate({x: x}, animationDuration, animationEasing);
            }
        }
    };
    
    return function(options){
        if(!options.element || !options.maxScale){
            throw('need an element to render to.');
        }
        
        var that = {};
        var el = $(options.element);
        var paper = new Raphael(el[0], el.width(), 160);
        
        options.maxScale = Math.round(options.maxScale);
        options.animationEasing = options.animationEasing || '<>';
        options.animationDuration = options.animationDuration || 500;
        
        var leftMargin = 5;
        var rightMargin = 10;
        var dataWidth = el.width() - (leftMargin + rightMargin);
        var majorTicInterval = options.majorTicInterval || 10;
        var minorTicInterval = options.minorTicInterval || 5;
        
        var scalebarY = 80;
        var ticHeight = 10;
        that.currentScale = options.maxScale;
        
        var rectHeight = 40;
        var x1 = leftMargin;
        var y1 = scalebarY - ticHeight - 20 - rectHeight;
        var width = 1;
        var height = rectHeight;
        var valueRect = paper.rect(x1, y1, width, height);
        valueRect.attr({fill: "90-#5394AD-#62ABCD", 'stroke-width': 1, 'stroke': '#3D75AA'});
        
        var annotations = [];
        var max_annotation_value = false;
        var start_max_annotation = 0;
        
        
        var outOfRange = paper.set();
        var tw = el.width();
        var bg = paper.rect(tw * .25, y1 + 5, tw * .5, height - 10, 5);
        bg.attr({'fill': '270-#356375-#16272F', 'stroke-width': 0});
        var t = paper.text(el.width() / 2, y1 + 20, 'Out of Range');
        t.attr({'fill': '#BBD6D8', 'font-size': 18});
        outOfRange.push(bg);
        outOfRange.push(t);
        outOfRange.hide();
                
        var widthFromValue = function(value){
            return Math.round((value / that.currentScale) * dataWidth);
        };
                
        var addAnnotation = function(opts){
            var w = widthFromValue(opts.max - opts.min);
            var x = (opts.min / that.currentScale) * dataWidth + leftMargin;
            var a = paper.rect(x, 0, w, 120);
            var opacity;
            a.attr({'fill': opts.color, 'stroke-width': 1, 'stroke': opts.color});
            a.toBack();
            var text_x = Math.round(x + w / 2);
            var text = paper.text(text_x, 100, opts.label);
            var subtext = paper.text(text_x, 110, opts.min + ' to '+opts.max + ' sq miles');
            if(w < 100){
                text.attr({opacity: 0});
                subtext.attr({opacity: 0});
            }
            annotations.push({rect: a, text: text, subtext: subtext, opts: opts});
            if(!max_annotation_value || opts.max > max_annotation_value){
                max_annotation_value = opts.max;
            }
        };


        if(options.annotations.length){
            for(var i=0; i<options.annotations.length;i++){
                if(options.annotations[i].max > start_max_annotation){
                    start_max_annotation = options.annotations[i].max;
                }
            }
            that.currentScale = start_max_annotation;
            for(var i=0; i<options.annotations.length;i++){
                addAnnotation(options.annotations[i]);
            }
        }
                
        var scaleBar = new ScaleBar({
            paper: paper,
            origin: [leftMargin, scalebarY],
            width: dataWidth,
            ticHeight: ticHeight,
            color: 'black',
            maxValue: options.maxScale,
            minorInterval: 5,
            majorInterval: 10,
            animationEasing: options.animationEasing,
            animationDuration: options.animationDuration,
            initialMaxValue: that.currentScale
        });
                
        that.scaleBar = scaleBar;
        
                
        // for debugging purposes only
        that.paper = paper;
        
        var updateValue = function(value, animate, animationTarget){
            console.log('updateValue', value, animate, max_annotation_value, options.maxScale, that.currentScale);
            if(max_annotation_value && value > max_annotation_value){
                var scale;
                if(value + (value * 0.1) > options.maxScale){
                    scale = options.maxScale;
                }else{
                    scale = value + (value * 0.1);
                }
                updateScale(scale, animate, function(){
                    updateValueCallback(value, animate);
                });
            }else{
                if(max_annotation_value && that.currentScale > max_annotation_value){
                    updateScale(max_annotation_value, animate, function(){
                        updateValueCallback(value, animate);
                    });                    
                }else{
                    updateValueCallback(value, animate, animationTarget);
                }
            }
        };
        
        that.updateValue = updateValue;
        
        var updateValueCallback = function(value, animate, animationTarget, callback){
            var prevValue = that.value || 1;
            that.value = value;
            var w = widthFromValue(value);
            if(animate){
                if(animationTarget){
                    valueRect.animateWith(animationTarget, {'width': w}, options.animationDuration, options.animationEasing, callback);
                }else{
                    valueRect.animate({'width': w}, options.animationDuration, options.animationEasing, callback);
                }
            }else{
                valueRect.attr('width', w);
            }
            if(annotations.length){
                for(var i=0;i<annotations.length;i++){
                    var a = annotations[i];
                    if(value <= a.opts.max && value >= a.opts.min){
                        a.text.attr({'font-weight': 'bold'});
                    }else{
                        a.text.attr({'font-weight': 'normal'});                        
                    }
                }
            }
            if(value > options.maxScale){
                outOfRange.show();
            }else{
                outOfRange.hide();
            }
        }
        
        var render = function(){
            // createScale();
        };
        
        that.render = render;
        
        var updateScale = function(value, animate, callback){
            var target = scaleBar.update(value, animate);
            that.currentScale = value;
            scaleAnnotations(target);
            updateValueCallback(that.value, animate, target, callback);
        };
        
        that.updateScale = updateScale;
        
        
        var scaleAnnotations = function(animationTarget){
            for(var i=0;i<annotations.length;i++){
                var a = annotations[i];
                var w = widthFromValue(a.opts.max - a.opts.min);
                var x = (a.opts.min / that.currentScale) * dataWidth + leftMargin;
                var text_x = Math.round(x + w / 2);
                if(animationTarget){
                    a.rect.animateWith(animationTarget, {x: x, width: w}, options.animationDuration, options.animationEasing);
                    if(w < 100){
                        a.text.animateWith(animationTarget, {x: text_x, opacity:0}, options.animationDuration, options.animationEasing);
                        a.subtext.animateWith(animationTarget, {x: text_x, opacity:0}, options.animationDuration, options.animationEasing);
                    }else{
                        a.text.animateWith(animationTarget, {x: text_x, opacity:1}, options.animationDuration, options.animationEasing);
                        a.subtext.animateWith(animationTarget, {x: text_x, opacity:1}, options.animationDuration, options.animationEasing);                        
                    }
                }else{
                    a.animate({x: x, width: w}, options.animationDuration, options.animationEasing);
                    a.text.animate({x: text_x}, options.animationDuration, options.animationEasing);
                    a.subtext.animate({x: text_x}, options.animationDuration, options.animationEasing);
                }
            }
        }
        
        return that;
    }    
}
)();