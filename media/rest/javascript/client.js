if(typeof lingcod.rest != 'object'){
    MarineMap.rest = {};
}

lingcod.rest.Client = function(opts){
    this.options = $.extend(this.defaults, opts);
}

lingcod.rest.Client.prototype.defaults = {
    name: false,
    service: false,
    // Editing will be enabled by default if a form is found within the service
    // body.
    editing: true,
    // (this, client object that was created, response body)
    on_create: function(client, object, response){},
    // (this, client object that was updated, response body)
    on_update: function(client, object, response){},
    // client = this, object = client object that was deleted
    on_delete: function(client, object){},
    // client = this, object = object being edited (false if create action)
    on_form_display: function(client, object){},
    // called after the client fetches the service root
    on_ready: function(){}
}