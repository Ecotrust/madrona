mlpa.representationReport = (function(){
    
    var Row = function(){
        // attr({'text-anchor': 'end'});
    };
    
    Row.prototype.update = function(){
        
    };
    
    return function(el, json, animate){
        var that = {};
        
        var paper = new Raphael(el[0], el.width(), 500);
        
        that.paper = paper;
        that.element = el;
        
        var update = function(json, animate){
            
        };
        
        that.update = update;
        
        update(json, animate);
        
        return that;
    };
})();