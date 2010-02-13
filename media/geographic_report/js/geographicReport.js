if(!window.lingcod){
    lingcod = {};
}

lingcod.geographicReport = (function(){
    
    var ScaleBar = lingcod.graphics.ScaleBar;
        
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
        
        var annotationHover = paper.set();
        var background = paper.rect(0, 0, 110, 20);
        background.attr({'fill': '#F6EDC8', 'stroke': '#8F8F8F', 'stroke-width': '1'});
        var annotationText = paper.text(55, 11, "");
        annotationHover.push(background);
        annotationHover.push(annotationText);
        annotationHover.hide();
        annotationHover.toFront();
        
        var addAnnotation = function(opts){
            var w = widthFromValue(opts.max - opts.min);
            var x = (opts.min / that.currentScale) * dataWidth + leftMargin;
            var anno = paper.set();
            var a = paper.rect(x, 0, w, 120);
            var opacity;
            a.attr({'fill': opts.color, 'stroke-width': 1, 'stroke': opts.color});
            a.toBack();
            var text_x = Math.round(x + w / 2);
            var text = paper.text(text_x, 100, opts.label);
            var subtext = paper.text(text_x, 110, opts.min + ' to '+opts.max + ' sq miles');
            if(w < 100){
                a.textHidden = true;
                text.hide();
                subtext.hide();
            }else{
                a.textHidden = false;
                text.show();
                subtext.show();
            }
            var obj = {rect: a, text: text, subtext: subtext, opts: opts};
            annotations.push(obj);
            if(!max_annotation_value || opts.max > max_annotation_value){
                max_annotation_value = opts.max;
            }
            anno.push(a);
            anno.push(text);
            anno.push(subtext);
            anno.hover(function(e){
                a.attr({opacity: 0.85});
            });
            anno.attr({title: opts.label});
            anno.mouseout(function(){
                a.attr({opacity: 1});
                a.attr({fill: opts.color})
                // annotationHover.hide();
            });
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
            var value = value || 0;
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
                if(callback){
                    callback(value, animate);
                }
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
            scaleAnnotations(target, false);
            updateValueCallback(that.value, animate, target, callback);
        };
        
        that.updateScale = updateScale;
        
        
        var scaleAnnotations = function(animationTarget, animate){
            for(var i=0;i<annotations.length;i++){
                var a = annotations[i];
                var w = widthFromValue(a.opts.max - a.opts.min);
                var x = (a.opts.min / that.currentScale) * dataWidth + leftMargin;
                var text_x = Math.round(x + w / 2);
                if(!animate){
                    a.rect.attr({x: x, width: w});
                    if(w < 100){
                        a.text.attr({x: text_x});
                        a.text.hide();
                        a.textHidden = true;
                        a.subtext.attr({x: text_x});
                        a.subtext.hide();
                    }else{
                        a.textHidden = false;
                        a.text.attr({x: text_x});
                        a.subtext.attr({x: text_x});    
                        a.text.show();
                        a.subtext.show();
                        a.subtext.show();                    
                    }
                }else if(animationTarget){
                    a.rect.animateWith(animationTarget, {x: x, width: w}, options.animationDuration, options.animationEasing);
                    if(w < 100){
                        a.textHidden = true;
                        a.text.hide();
                        a.subtext.hide();
                    }else{
                        a.textHidden = false;
                        a.text.show();
                        a.subtext.show();
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