mlpa.representationReport = (function(){
    
    var row_text_y = 23;
    var row_rect_y = 10;
    var data_rect_max_width = 300;
    var minScale = 8;
    var maxValue = 30;
    
    var Row = function(label, json, paper){
        this.paper = paper;
        this.label = label;
        this.json = json;
        this.set = paper.set();
        this.text = this.paper.text(125, row_text_y, this.label);
        this.text.attr({'text-anchor': 'end', 'font-size': 12, 'opacity': 1});
        this.rect = paper.rect(135, row_rect_y, 1, 25);
        // var self = this;
        // this.rect.attr({fill: "90-#5394AD-#62ABCD", 'stroke-width': 1, 'stroke': '#3D75AA'});
        this.rect.attr({'fill': '#ccc', 'stroke': '#aaa'});
        this.set.push(this.text, this.rect);
        var self = this;
        this.set.mouseover(function(e){
            var tt = $('<div id="repTooltip" style="position:absolute;top:'+(e.clientY + 15)+'px;left:'+(e.clientX + 15)+'px;"><strong>'+self.label+'</strong><br />'+Math.round(self.json.result * 1000) / 1000+' '+self.json.units+'<br />'+Math.round(self.json.percent_of_total * 1000) / 1000+' % of study region</div>');
            $(document.body).append(tt);
        });
        this.set.mouseout(function(e){
            $('#repTooltip').remove();
        });
    };
    
    Row.prototype.update = function(json){
        this.json = json;
    };
    
    Row.prototype.setOffset = function(offset, animate, callback){
        this.offset = offset;
        if(animate){
            var target = false;
            if(animate !== true){
                target = animate;
            }
            this.text.anim({
                attrs: {y: row_text_y + offset},
                ms: animationDuration,
                easing: animationEasing,
                target: target,
                callback: callback
            });
            this.rect.anim({
                attrs: {y: row_rect_y + offset},
                ms: animationDuration,
                easing: animationEasing,
                target: target                
            });
        }else{
            this.text.attr({y: row_text_y + offset});
            this.rect.attr({y: row_rect_y + offset});
            callback();
        }
    };
    
    Row.prototype.getOffset = function(){
        return this.offset;
    };
    
    Row.prototype.showValue = function(animate, scale, target){
        var w = this.json.percent_of_total * (data_rect_max_width / scale);
        if(animate){
            this.rect.anim({
                attrs: {'width': w},
                ms: animationDuration,
                easing: animationEasing,
                target: target
            });
        }else{
            this.rect.attr({'width': w});
        }
    };
    
    var animationEasing = '>';
    var animationDuration = 300;
    
    return function(el, json, animate){
        var that = {};
        
        var paper = new Raphael(el[0], 450, 850);
        that.paper = paper;
        that.element = el;
        var currentScale = false;

        var rows = {};
                
        var update = function(json, animate){
            var newScale = 0;
            for(var key in json){
                var record = json[key];
                if(rows[key]){
                    rows[key].update(record);
                }else{
                    rows[key] = new Row(key, record, paper);
                    rows[key].text.attr({'opacity': 0});
                    rows[key].rect.attr({'opacity': 0});
                }
                if(record.percent_of_total > newScale){
                    newScale = record.percent_of_total;
                }
            }
            hideInvalidRows(json, function(){
                sortAndPositionRows(animate, function(){
                    updateScale(newScale, true, function(){
                        setTimeout(showValues, 100);
                    });
                });
            });
        };
        
        that.update = update;
        
        var showValues = function(target){
            for(var key in rows){
                var row = rows[key];
                if(row.rect.attr('opacity') !== 0){
                    row.showValue(true, currentScale, target);
                    if(!target){
                        target = row.rect;
                    }
                }
            }
        };
        
        var hideInvalidRows = function(json, callback){
            var hideTarget = false;
            var showTarget = false;
            for(var key in rows){
                var row = rows[key];
                var missing = true;
                for(var ekey in json){
                    if(ekey === key){
                        missing = false;
                        break;
                    }
                }
                if(missing){
                    row.hidden = true;
                    if(row.text.attr('opacity') > 0.05){
                        row.text.anim({
                            attrs: {'opacity': 0},
                            ms: animationDuration,
                            easing: animationEasing,
                            target: hideTarget,
                            callback: callback
                        });
                        if(!hideTarget){
                            hideTarget = row.set;
                            callback = false;
                        }
                        row.rect.anim({
                            attrs: {'opacity': 0},
                            ms: animationDuration,
                            easing: animationEasing,
                            target: hideTarget,
                            callback: callback
                        });                        
                    }
                }else{
                    row.hidden = false;
                    if(row.text.attr('opacity') < 0.95){
                        row.text.anim({
                            attrs: {'opacity': 1},
                            ms: animationDuration,
                            easing: animationEasing,
                            target: showTarget,
                            callback: callback 
                        });
                        if(!showTarget){
                            showTarget = row.set;
                            callback = false;
                        }
                        row.rect.anim({
                           attrs: {'opacity': 1},
                           ms: animationDuration,
                           easing: animationEasing,
                           target: showTarget,
                           callback: callback 
                        });
                    }
                }
            }
            if(callback){
                callback();
            }else{
            }
        };
        
        var offset = 35;
        var scaleOffset = 0;
        
        var sortAndPositionRows = function(animate, callback){
            var row_array = [];
            for(var key in rows){
                if(rows[key].hidden === false){
                    row_array.push(rows[key]);
                }
            }
            row_array.sort(function(a, b){
                return a.json.sort - b.json.sort;
            });
            if(animate){
                animate = row_array[0];
            }
            var totalOffset = 0;
            var animate = false;
            for(var i=0; i<row_array.length;i++){
                totalOffset = i * offset;
                if(totalOffset !== row_array[i].getOffset()){
                    if(animate){
                        row_array[i].setOffset(totalOffset, animate);
                    }else{
                        var animate = row_array[i];
                        row_array[i].setOffset(totalOffset, animate, callback);
                    }                    
                }
            }
            var old = totalOffset;
            
            if(old === scaleOffset){
                if(!animate){
                    callback();
                }else{
                }
            }else{
                setTimeout(callback, animationDuration);
                totalOffset = totalOffset - scaleOffset;
                scaleBar.changeY(totalOffset, animate, animationEasing, animationDuration);                
            }
            scaleOffset = old;
            that.height = (row_array.length * offset) + 70;
            $(that.paper.canvas).parent().height(that.height);
        }
        
        var currentScale = minScale;

        var updateScale = function(max, animate, callback){
            if(max < minScale){
                max = minScale;
            }else if(max > maxValue){
                max = maxValue;
            }
            if(currentScale === max){
                // do nothing
                callback();
            }else{
                currentScale = max;
                var target = scaleBar.update(max, true, callback);
                showValues(target);
                // callback();
            }
        }
        
        // create the scale
        var scaleBar = new lingcod.graphics.ScaleBar({
            paper: paper,
            origin: [135, 70],
            width: data_rect_max_width,
            ticHeight: 5,
            color: 'black',
            maxValue: maxValue,
            minorInterval: 1,
            majorInterval: 2,
            animationEasing: animationEasing,
            animationDuration: animationDuration,
            initialMaxValue: minScale,
            label: 'Percent of Habitat Captured  % '
        });
        
        
        update(json, true);
        
        return that;
    };
})();