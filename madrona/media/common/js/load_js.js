(function(){
    var queue = [];
    var callback = function(){};
    this.mm_load_js = function(path, callbackF, test){
        if(callbackF){
            callback = callbackF;
        }
        $.get(path+'js_includes.xml', function(data, textStatus){
            var xml = $(data);
            $(xml).find('file').each(function(){
                queue.push($(this).attr('path'));
            });
            if(test){
                $(xml).find('test').each(function(){
                    queue.push($(this).attr('path'));
                });
            }
            loaded();
        });
    }
    
    function loaded(){
        if(queue.length){
            var path = queue.shift();
            $.getScript(path, loaded);
        }else{
            callback();
        }
    }
})()