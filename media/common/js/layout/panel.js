lingcod.panel = function(options){
        
    var that = {};
    
    var el = $('<div style="display:none;" class="marinemap-panel"><a class="close" href="#">close</a><div class="content"></div></div>');
    el.find('a.close').click(function(){
        that.close();
    });
    var content = el.find('.content');
    
    $(document.body).append(el);

    that.showContent = function(elements){
        that.addContent(elements);
        that.show();        
    }
    
    that.addContent = function(elements){
        content.html('');
        content.append(elements);        
    }
    
    that.show = function(){
        el.show();
        $(that).trigger('show', that);        
    }
    
    that.close = function(){
        el.hide();
        el.find('div.content').html('');
    }
    
    that.spin = function(message){
        el.show();
    }
    
    that.showError = function(title, message){
        
    }
    
    that.showUrl = function(url, options){
        // throw('what the fucking fuck!');
        var new_url = url;
        that.spin(options.load_msg || "Loading");
        $.ajax({
            url: url,
            method: 'GET',
            complete: function(response, status){
                switch(response.status){
                    case 200:
                        that.showContent(response.responseText)
                        if(options && options.success){
                            options.success(response, status);
                            $(that).trigger('show', response, status);
                        }
                        // get content
                        // that.showContent
                        break;
                        
                    default:
                        that.showError('A Server Error Occured.', 
                            'Please try again.');
                            
                        if(options && options.error){
                            options.error(response, status);
                        }
                        $(that).trigger('error', response, status);
                }
            }
        });
    }
    
    // Methods needed for test management        
    that.destroy = function(){
        that.getEl().remove();
    }
    
    that.getEl = function(){
        return el;
    }
            
    return that;
};