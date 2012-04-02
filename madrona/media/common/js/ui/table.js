madrona.ui = {};

madrona.ui.table = (function(){
    
    
    return function(element){
        var element = $(element);
        
        if(element.hasClass('madrona-table')){
            if(element.hasClass('processed')){
                return;
            }
            
            element.addClass('processed');
            
            if(element.hasClass('madrona-table-zebra')){
                var odd = false;
                element.find('tbody tr').each(function(){
                    if(odd){
                        $(this).addClass('zebra');
                    }
                    odd = !odd;
                });
            }
            if(element.find('span.hover').length > 0){
                element.addClass('madrona-table-hover');
            }
            if(element.find('span.popup').length > 0){
                element.addClass('madrona-table-popup');
            }
            
        }else{
            throw('element does not have class madrona-table');
        }
    }
})();