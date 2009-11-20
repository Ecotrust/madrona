lingcod.rest.Client = function(opts){
    this.options = $.extend(this.defaults, opts);
}

lingcod.rest.Client.prototype.defaults = {
    service: false,
    shape_editor: false
}

lingcod.rest.Client.prototype.edit_context_link = function(){
    // if the kml feature is editable, return a context menu link as a string
}

lingcod.rest.Client.prototype.