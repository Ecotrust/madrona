/**
 * Constructor for googleLayers widget which controls the display options of the plugin.
 * @constructor
 * @param {GEPlugin} reference to the google earth plugin instance.
 * @param {form element} the form that controls options. See http://code.google.com/apis/earth/documentation/reference/interface_g_e_options.html
 * @param {form element} the form that controls which layers are displayed. See http://code.google.com/apis/earth/documentation/layers.html#layers
 */
lingcod.map.googleLayers = function(ge, options_form, layers_form){
    this.layers = layers_form;
    this.options = options_form;
    this.get = ge;
    var self = this;
    $(this.layers).find('input').click(function(){
        self.updateLayers()
    });
    
    $(this.options).find('input').click(function(){
        self.updateOptions()
    });
    
    this.updateLayers();
    this.updateOptions();
}

/**
 * Looks at the layers form and updates the map to match form values
 */
lingcod.map.googleLayers.prototype.updateLayers = function(){
    console.log('updating layers');
    $(this.layers).find('input').each(function(){
        ge.getLayerRoot().enableLayerById(ge[$(this).attr('name')], $(this).attr('checked'));
    });
};

/**
 * Looks at the options form and updates the map to match form values. The 
 * name of the input element should match the setXVisibility function on 
 * ge.getOptions();.
 * for example:
 *      <input name="setGridVisibility" />
 */
lingcod.map.googleLayers.prototype.updateOptions = function(){
    var form = this.options;
    var options = ge.getOptions();
    $(form).find('input').each(function(){
        console.log(this);
        var $input = $(this);
        var name = $input.attr('name');
        if(name != 'nav' && name != 'sun'){
            options[name](this.checked);
        }
    });
    
    if (form.nav && form.nav.checked) {
        ge.getNavigationControl().setVisibility(ge.VISIBILITY_SHOW);
    } else if(form.nav) {
        ge.getNavigationControl().setVisibility(ge.VISIBILITY_HIDE);
    }
    
    if(form.sun){
        ge.getSun().setVisibility(form.sun.checked);
    }
};

/**
 * Unbinds all event listeners.
 */ 
lingcod.map.googleLayers.prototype.destroy = function(){
    $(this.layers).find('input').unbind('click');
    $(this.options).find('input').unbind('click');
}