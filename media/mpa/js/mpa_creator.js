
var create_edit_finish_html = '<button id="create_button">Create an Mpa</button><button id="edit_button">Edit Mpa</button><button id="finish_edit">Finish Edit</button>';    
var accept_reject_html = '<p><button id="accept_button">Accept</button><button id="reject_button">Reject</button></p>';
var try_again_html = '<p><button id="try_again_button">Try Again</button></p>';

/**
 * Creates a new MpaCreator instance.
 * Creates a new DrawTool instance and a new Manipulators instance
 * Initializes panels and buttons
 * @constructor
 * @param {List} manip_list, list of manipulators to be executed
 * @param {Dictionary} panels, the ids of the button panel and the results panel
 */
lingcod.MpaCreator = function(manip_list, panels) {
    this.drawTool = new lingcod.DrawTool();
    this.manipulators = new lingcod.Manipulators($.delegate(this.renderManipulatorResults, this), manip_list);
    
    this.button_panel = $('#'+panels.button_panel);
    this.results_panel = $('#'+panels.results_panel);
    
    this.button_panel.html(create_edit_finish_html);
    
    this.create_button = $('#create_button');
    this.edit_button   = $('#edit_button');
    this.finish_button = $('#finish_edit');
    
    this.disableButton(this.create_button);
    this.disableButton(this.edit_button);
    this.disableButton(this.finish_button);
}

/**
 * Starts the mpa creation process by enabling the 'Create an Mpa' button.
 */
lingcod.MpaCreator.prototype.startMpaCreation = function() {
    this.enableButton(this.create_button);
    this.create_button.click($.delegate(this.drawAndProcess, this)); 
}

/**
 * Calls drawShape in DrawTool. Callback returns control to processManipulators.
 */
lingcod.MpaCreator.prototype.drawAndProcess = function() {
    this.drawTool.drawShape($.delegate(this.processManipulators, this));
    this.disableButton(this.create_button);
}

/**
 * Calls process in Manipulators with WKT version of targetShape.
 */
lingcod.MpaCreator.prototype.processManipulators = function() {
    target_wkt = this.drawTool.polyToWkt();
    this.manipulators.process(target_wkt);
}

/**
 * Called upon completion of manipulators.process.
 * Evalautes manip_data parameter, and calls displayResults.
 * @param {JSON wrapped dictionary} manip_data is assigned the return value from manipulators.process
 */
lingcod.MpaCreator.prototype.renderManipulatorResults = function(manip_data) {
    ret_obj = eval( '(' + manip_data + ')' );
    this.displayResults(ret_obj.html, ret_obj.clipped_shape, ret_obj.success);
}

/**
 * Displays the html return results from the manipulators.
 * If the manipulation was a success, displays the clipped shape.
 * @param {String} ret_html, will be displayed on the results panel
 * @param {kml geometry} clipped_shape, in the case of a successful manipulation, clipped_shape will be displayed on the map
 * @param {String} success, equal to '1' if manipulations were a success, equal to '0' otherwise
 */
lingcod.MpaCreator.prototype.displayResults = function(ret_html, clipped_shape, success) {
    if(success=='1') {
        this.drawTool.hideShape();
        this.lastMpa = gex.util.displayKmlString(clipped_shape);
        
        this.enableButton(this.edit_button);
        this.edit_button.click($.delegate(this.editShape, this));
        
        ret_html += accept_reject_html;
        this.results_panel.html(ret_html);
        
        this.accept_button = $('#accept_button');
        //this.accept_button.click($.delegate(this.acceptMpa, this));
        
        this.reject_button = $('#reject_button');
        this.reject_button.click($.delegate(this.rejectMpa, this));
    }
    else {
        ret_html += try_again_html;
        this.results_panel.html(ret_html);
        
        this.try_again_button = $('#try_again_button');
        this.try_again_button.click($.delegate(this.tryAgain, this));
    }
}

/**
 * Removes clipped shape, enables editing of original shape.
 */
lingcod.MpaCreator.prototype.editShape = function() {
    gex.dom.removeObject(this.lastMpa);
    
    this.disableButton(this.accept_button);
    this.disableButton(this.reject_button);
    this.disableButton(this.edit_button);
    
    this.drawTool.editShape();
    
    this.enableButton(this.finish_button);
    this.finish_button.click($.delegate(this.finishEdit, this));
}

/**
 * Clears the results_panel, ends the editing process, effects execution of processManipulators.
 */
lingcod.MpaCreator.prototype.finishEdit = function() {
    this.results_panel.html("");
    this.disableButton(this.finish_button);
    this.drawTool.endEdit($.delegate(this.processManipulators, this));
}

/**
 * Removes the clipped shape from the map, clears the results panel, enables the Create an Mpa button.
 */
lingcod.MpaCreator.prototype.rejectMpa = function() {
    gex.dom.removeObject(this.lastMpa);
    this.results_panel.html("");
    this.enableButton(this.create_button);
    this.disableButton(this.edit_button);
}

/**
 * Removes the user-drawn shape from the map, clears the results panel, enables the Create an Mpa button.
 */
lingcod.MpaCreator.prototype.tryAgain = function() {
    this.drawTool.clearShape();
    this.results_panel.html("");
    this.enableButton(this.create_button);
    this.disableButton(this.edit_button);
}

/**
 * Disables the given button.
 * @param {button object} button is the object to be disabled
 */
lingcod.MpaCreator.prototype.disableButton = function(button) {
    button.attr('disabled', 'disabled');
}

/**
 * Enables the given button
 * @param {button object} button is the object to be enabled
 */
lingcod.MpaCreator.prototype.enableButton = function(button) {
    button.removeAttr('disabled');
}
