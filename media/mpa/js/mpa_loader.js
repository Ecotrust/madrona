var loadFormURL = '/mpa/load/form/';
var form_buttons = '<input id="submit" type="submit" value="Submit" />' + '<button id="cancel">Cancel</button>';

/**
 * Creates a new MpaLoader instance.
 * @constructor
 * @param {DrawTool} drawTool, object used to draw and edit shapes on the map
 * @param {Panel} displayPanel, used for displaying templates related to mpa loading
 * @param {Function} renderCallBack, function called after load attempt is complete
 */
lingcod.MpaLoader = function(drawTool, displayPanel, renderCallBack) {
    this.drawTool = drawTool;
    this.displayPanel = displayPanel;
    this.renderCallBack = renderCallBack;
};
   
/**
 * Executes ajax GET call to server to retrieve the load form
 */
lingcod.MpaLoader.prototype.getFormAndLoadMpa = function() {
    $.get(loadFormURL, $.delegate(this.displayForm, this));
};

/**
 * Called upon completion of load form retrieval
 * Displays the returned load form on the given panel
 * Adds a Submit and a Cancel button
 * @param {String} mpa_form, form for loading a specific mpa
 */
lingcod.MpaLoader.prototype.displayForm = function(mpa_form) {
    //I'm adding the submit button here because I couldn't figure out how to get the submitted form to return 
    //the next template to the display panel (it would display the resulting template to the whole window)
    mpa_form += form_buttons;
    this.displayPanel.html(mpa_form);
    this.initializeButtons();
};

/**
 * Called from displayForm()
 * Initializes template buttons for click action
 */
lingcod.MpaLoader.prototype.initializeButtons = function() {
    $('#submit').click($.delegate(this.submitForm, this));
    $('#cancel').click($.delegate(this.cancelForm, this));
}

/**
 * Executes ajax GET call to server to retrieve the mpa
 */
lingcod.MpaLoader.prototype.submitForm = function() {
    $.get(
        '/mpa/load/', 
        { user: $('#id_user').val(),
          name: $('#id_name').val() },
        $.delegate(this.handleFormCompletion, this) 
    );
};

/**
 * Called upon Cancel button click event
 * Clears the display panel and returns control to the callback
 */
lingcod.MpaLoader.prototype.cancelForm = function() {
    var success = false;
    this.displayPanel.html("");
    this.renderCallBack.call(this.renderCallBack, success);
};

/**
 * Called upon form submittal/return
 * If the return value is the form (required fields not completed), displays the form again
 * Otherwise, renders the mpa and template
 * @param {String/json} load_results, either the form for loading or the json dictionary containing the loaded mpa
 */
lingcod.MpaLoader.prototype.handleFormCompletion = function(load_results) {
    if($('#id_user').val() == "" || $('#id_name').val() == "") {
        this.displayForm(load_results);
    } else {
        this.renderResults(load_results);
    }
};

/**
 * Called upon successful mpa loading 
 * If the load was a success, add geometries to drawTool and display clipped geometry on the map
 * Regardless, display returned template and return control to the callback
 * @param {JSON} load_data, the json dictionary containing the loaded mpa
 */
lingcod.MpaLoader.prototype.renderResults = function(load_data) {
    var ret_obj = eval( '(' + load_data + ')' );
    var success = ret_obj.success == '1';
    if(success) {
        //this.drawTool.setMpaID(ret_obj.id);
        var geojson_clipped = eval( '(' + ret_obj.geojson_clipped + ')' );
        this.drawTool.setClippedShape(geojson_clipped);
        
        var geojson_orig = eval( '(' + ret_obj.geojson_orig + ')' );
        this.drawTool.setTargetShape(geojson_orig);
        this.drawTool.displayClipped(); 
    }
    this.displayPanel.html(ret_obj.html);
    this.renderCallBack.call(this.renderCallBack, success);
};


