var form_buttons = '<input id="submit" type="submit" value="Submit" />' + '<button id="cancel">Cancel</button>';

/**
 * Creates a new MpaSaver instance.
 * @constructor
 * @param {Panel} displayPanel, used for displaying templates related to mpa saving
 * @param {Function} renderCallBack, function called after save attempt is complete
 */
lingcod.MpaSaver = function(displayPanel, renderCallBack) {
    this.displayPanel = displayPanel;
    this.renderCallBack = renderCallBack;
};

/**
 * Initializes original and clipped geometry variables (used in final form submission)
 * Executes ajax GET call to server to retrieve the save form
 * @param {Geometry} original_geom, geometry drawn by user
 * @param {Geometry} clipped_geom, geometry after clipping by manipulators
 */
//lingcod.MpaSaver.prototype.getFormAndPostData = function(id, original_geom, clipped_geom) {
    //this.id = id;
lingcod.MpaSaver.prototype.getFormAndPostData = function(original_geom, clipped_geom) {
    this.original_geom = original_geom;
    this.clipped_geom = clipped_geom;
    $.get('/mpa/save/form/', $.delegate(this.displayForm, this));
};

/**
 * Called upon Form retrieval
 * Displays the form on the panel along with a submit and a cancel button
 * Hides the geometry related fields and labels
 * Initializes the form buttons for click action
 * @param {Form} mpa_form, html form for mpa saving
 */
lingcod.MpaSaver.prototype.displayForm = function(mpa_form) {
    //I'm adding the submit button here because I couldn't figure out how to get the submitted form to return 
    //the next template to the display panel (it would display the resulting template to the whole window)
    //This solution however leaves intact the problem of the user hitting <enter> from a text box
    //in which case the application reloads (problem)
    mpa_form += form_buttons;
    this.displayPanel.html(mpa_form);
    this.initializeFormFieldsAndButtons();
};

/**
 * Hides the geometry related fields and labels
 * Initializes the form buttons for click action
 */
lingcod.MpaSaver.prototype.initializeFormFieldsAndButtons = function() {
    //$('[id=id_id]').hide();
    //$('[for=id_id]').hide();
    $('[id=id_geometry_orig]').hide();
    $('[for=id_geometry_orig]').hide();
    $('[id=id_geometry_final]').hide();
    $('[for=id_geometry_final]').hide();
    $('#submit').click($.delegate(this.submitForm, this));
    $('#cancel').click($.delegate(this.cancelForm, this));
};

/**
 * Called upon Form submission/return
 * If form was valid, displays the template, returns control to callback
 * Otherwise, redisplays the form 
 * @param {Form/Template} save_results, html form for mpa saving
 */
lingcod.MpaSaver.prototype.handleFormCompletion = function(save_results) {
    this.displayPanel.html(save_results); //this line allows the id_geometry_orig check to work
    if ($('#id_geometry_orig').val() == undefined) {
        var success = true;
        this.renderCallBack.call(this.renderCallBack, success);
    }
    else {
        this.displayForm(save_results);
    }
};

/**
 * Called upon form submit button click action
 * Executes ajax POST call to server to save the given mpa to the db
 */
lingcod.MpaSaver.prototype.submitForm = function() {
    $.post(
        '/mpa/', 
        { //id: this.id,
          user: $('#id_user').val(),
          name: $('#id_name').val(), 
          geometry_orig: this.original_geom,
          geometry_final: this.clipped_geom },
        $.delegate(this.handleFormCompletion, this)
    );
};

/**
 * Called upon form cancel button click action
 * Clears the panel of any display
 * Returns control to callback
 */
lingcod.MpaSaver.prototype.cancelForm = function() {
    var success = false;
    this.displayPanel.html("");
    this.renderCallBack.call(this.renderCallBack, success);
};
