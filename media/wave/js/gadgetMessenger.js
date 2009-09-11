if(lingcod == undefined){
    var lingcod = {};
}

lingcod.gadgetMessenger = {};

lingcod.gadgetMessenger.gadgetSide = function(url){
    this.target_url = url;
    this.target = top;
    
    var self = this;
    $(window).bind('message', function(je){
        // console.log('gadgetMessenger, message!');
        var e = je.originalEvent;
        // console.log(e.source, self.target)
        if(e.source == self.target){
            // console.log('source matches target');
            var data = gadgets.json.parse(e.data);
            // console.log(data);
            $(self).trigger(e, data);
        }
    });
}

lingcod.gadgetMessenger.gadgetSide.prototype.send = function(data){
    // console.log('send called with argument', data);
    var json = gadgets.json.stringify(data);
    // console.log('send, json:', json);
    if(json.length && json.length > 0){
        // console.log('postingMessage', json, this.target_url);
        this.target.postMessage(json, this.target_url);
        // console.log('posted');
    }else{
        throw('cannot send empty message!!');
        if(console && console.log){
            console.log('tried to send message with data = ', data);
        }
    }
}