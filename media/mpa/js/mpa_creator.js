
var create_edit_finish_html = '<button id="create_button">Create an Mpa</button><button id="edit_button">Edit Mpa</button><button id="finish_edit">Finish Edit</button>';    
var accept_html = '<p><button id="accept_button">Accept</button></p>';
var load_clear_html = '<p><button id="load_button">Load Mpa</button><button id="clear_mpa_button">Clear Mpa</button><button id="clear_all_button">Clear All</button></p>';

/**
 * Creates a new MpaCreator instance
 * Initializes panels and buttons
 * Creates a new Manipulators instance, MpaLoader instance, and MpaSaver instance
 * @constructor
 * @param {drawTool} drawTool, initialized drawTool object
 * @param {List} manip_list, list of manipulators to be executed
 * @param {Dictionary} panels, the ids of the button panel and the results panel
 */
lingcod.MpaCreator = function( drawTool, manip_url, panels) {
    //we've put the gex back into draw_tool via the constructor (was needed to run lingcod.js)
    //will need to re-examine this public gex at some point...
    this.drawTool = drawTool;
        
    this.results_panel = $('#'+panels.results_panel);
    this.button_panel = $('#'+panels.button_panel);
    button_html = create_edit_finish_html + load_clear_html;
    this.button_panel.html(button_html);
    this.template_buttons = []
    
    this.manipulators = new lingcod.Manipulators(this.results_panel, $.delegate(this.finishManipulatorDisplay, this), manip_url, this.drawTool);
    this.mpaLoader = new lingcod.MpaLoader(this.drawTool, this.results_panel, $.delegate(this.finishLoadDisplay, this), "1");
    this.mpaSaver = new lingcod.MpaSaver(this.results_panel, $.delegate(this.finishSave, this));
    
    this.initializeButtons();
}

/**
 * Initializes the primary buttons used in drawing, loading, saving, and editing mpas.
 */
lingcod.MpaCreator.prototype.initializeButtons = function() {
    this.create_button = $('#create_button');
    this.create_button.click($.delegate(this.createMpa, this)); 
    this.edit_button   = $('#edit_button');
    this.edit_button.click($.delegate(this.editMpa, this));
    this.finish_button = $('#finish_edit');
    this.finish_button.click($.delegate(this.finishEdit, this));
    this.load_button = $('#load_button');
    //this.load_button.click($.delegate(this.loadMpa, this));
    this.clear_mpa_button = $('#clear_mpa_button');
    this.clear_mpa_button.click($.delegate(this.clearMpa, this));
    this.clear_all_button = $('#clear_all_button');
    this.clear_all_button.click($.delegate(this.clearAll, this));
    
    //this.disableButton(this.create_button);
    this.disableButton(this.edit_button);
    this.disableButton(this.finish_button);
    //this.disableButton(this.load_button);
    this.disableButton(this.clear_mpa_button);
    this.disableButton(this.clear_all_button);
}

/**
 * Removes the current mpa from the map (and drawTool)
 * Clears any template contents from the results panel
 * Resets the buttons for drawing/loading
 */
lingcod.MpaCreator.prototype.clearMpa = function() {
    this.clearShapeFromDrawTool();
    this.clearResultsPanel();
    this.disableButton(this.edit_button);
    this.disableButton(this.finish_button);
    this.disableButton(this.clear_mpa_button);
    this.enableCreateAndLoad();
    this.enableButton(this.clear_all_button);
}

/**
 * Removes all mpas from the map (and the drawTool)
 * Clears any template contents from the results panel
 * Resets the buttons for drawing/loading
 */
lingcod.MpaCreator.prototype.clearAll = function() {
    this.drawTool.clearAll();
    this.clearResultsPanel();
    this.disableButton(this.edit_button);
    this.disableButton(this.finish_button);
    this.disableButton(this.clear_mpa_button);
    this.enableCreateAndLoad();
}

// LOADING MPA

/**
 * Starts the Loading process 
 */
lingcod.MpaCreator.prototype.loadMpa = function() {
    this.disableButton(this.create_button);
    this.disableButton(this.load_button);
    this.disableButton(this.clear_mpa_button);
    this.disableButton(this.clear_all_button);
    this.mpaLoader.getFormAndLoadMpa();
}

/**
 * Called upon Load completion
 * Resets buttons for Load Acceptance/Editing/Rejecting
 * @param {boolean} success, boolean value representing load success or failure
 */
lingcod.MpaCreator.prototype.finishLoadDisplay = function(success) {
    if (success) {
        load_html = this.results_panel.html() + accept_html;
        this.results_panel.html(load_html);
                        
        this.accept_button = $('#accept_button');
        this.accept_button.click($.delegate(this.acceptLoad, this));
                
        this.template_buttons = [this.accept_button];
        this.enableButton(this.edit_button);
        this.enableButton(this.clear_mpa_button);
    } else {    
        this.enableCreateAndLoad();
        this.enableButton(this.clear_all_button);
    }
}

/**
 * Called upon loading 'Accept' button click event
 * Clears contents from results panel 
 * Resets buttons for drawing/loading
 */
lingcod.MpaCreator.prototype.acceptLoad = function() {
    this.clearResultsPanel();
    this.enableCreateAndLoad();
    this.disableButton(this.clear_mpa_button);
    this.enableButton(this.clear_all_button);
};

// CREATING MPA 

/**
 * Starts shape drawing process
 * Callback (when user finishes drawing) returns control to this.manipulators.process
 */
lingcod.MpaCreator.prototype.createMpa = function() {
    this.results_panel.html("");
    this.drawTool.drawShape($.delegate(this.manipulators.process, this.manipulators));
    this.disableButton(this.create_button);
    this.disableButton(this.load_button);
    this.disableButton(this.clear_mpa_button);
    this.disableButton(this.clear_all_button);
}

// PROCESS MANIPULATORS

/**
 * Called after an mpa has been manipulated
 * Resets buttons for Load Acceptance/Editing/Rejecting
 * @param {boolean} success, boolean value representing manipulators success or failure
 */
lingcod.MpaCreator.prototype.finishManipulatorDisplay = function(success) {
    if(success) {
        display = this.results_panel.html() + accept_html;
        this.results_panel.html(display);
        
        this.accept_button = $('#accept_button');
        this.accept_button.click($.delegate(this.acceptManipulatorResults, this));
                
        this.template_buttons = [this.accept_button];
        this.enableButton(this.edit_button);
        this.enableButton(this.clear_mpa_button);
    } else {
        this.clearResultsPanel();
        //this.clearShapeFromDrawTool();
        this.drawTool.clear();
        this.enableCreateAndLoad();
        this.enableButton(this.clear_all_button);
    }
}

/**
 * Called upon mpa creation/clipping 'Accept' button click event
 * disables primary buttons and begins the Save process
 */
lingcod.MpaCreator.prototype.acceptManipulatorResults = function() {
    this.disableButton(this.edit_button);
    this.disableButton(this.clear_mpa_button);
    this.disableButton(this.clear_all_button);
    this.saveMpa();
}

// EDITING MPA -- move to manipulators and mpa_loader?

/**
 * Adjusts button enable/disable
 * Starts the edit process
 */
lingcod.MpaCreator.prototype.editMpa = function() {
    this.drawTool.removeClipped();

    this.disableButtons(this.template_buttons);
    this.disableButton(this.edit_button);
    this.disableButton(this.clear_mpa_button);
    this.disableButton(this.clear_all_button);
    
    this.drawTool.editShape();
    
    this.enableButton(this.finish_button);
    this.enableButton(this.clear_mpa_button);
}

/**
 * Called on Finsish Edit button click event
 * Disables primary buttons 
 * Ends editing, which in turn restarts manipulator processing
 */
lingcod.MpaCreator.prototype.finishEdit = function() {
    this.disableButton(this.finish_button);
    this.disableButton(this.clear_mpa_button);
    this.disableButton(this.clear_all_button);
    this.drawTool.endEdit($.delegate(this.manipulators.process, this.manipulators));
}

// SAVE MPA

/**
 * Saves the clipped shape (and original geometry) to the database.
 */
lingcod.MpaCreator.prototype.saveMpa = function() {
    //this.mpaSaver.getFormAndPostData(this.drawTool.getMpaID(), this.drawTool.targetToWkt(), this.drawTool.getClippedShape());
    this.mpaSaver.getFormAndPostData(this.drawTool.targetToWkt(), this.drawTool.getClippedShape());
}

/**
 * Called after an mpa has been saved
 * If save was successful, 
 *      Resets buttons for Load Acceptance/Editing/Rejecting
 * otherwise,
 *      return state to that before attempted save (clipped shape is shown with edit option)
 * @param {boolean} success, boolean value representing Save success or failure
 */
lingcod.MpaCreator.prototype.finishSave = function(success) {
    if(success) {
        this.enableCreateAndLoad();
        this.enableButton(this.clear_all_button);
    } else {
        this.enableButton(this.edit_button);
        this.enableButton(this.clear_mpa_button);
    }
}

// OTHER OPERATIONS

/**
 * Removes any template display from results panel
 */
lingcod.MpaCreator.prototype.clearResultsPanel = function() {
    this.results_panel.html("");
    this.template_buttons = [];
}

/**
 * Removes shape references from drawTool
 */
lingcod.MpaCreator.prototype.clearShapeFromDrawTool = function() {
    this.drawTool.removeClipped();
    this.drawTool.clear();
}

/**
 * Removes shape references from drawTool
 */
lingcod.MpaCreator.prototype.enableCreateAndLoad = function() {
    this.enableButton(this.create_button);
    this.enableButton(this.load_button); 
    this.disableButtons([this.edit_button, this.finish_button]);
}

/**
 * Disables the given button.
 * @param {button object} button to be disabled
 */
lingcod.MpaCreator.prototype.disableButton = function(button) {
    button.attr('disabled', 'disabled');
}

/**
 * Disables the given buttons.
 * @param {list of button objects} buttons to be disabled
 */
lingcod.MpaCreator.prototype.disableButtons = function(buttons) {
    for ( var i in buttons ) {
        buttons[i].attr('disabled', 'disabled');
    }
}

/**
 * Enables the given button
 * @param {button object} button to be enabled
 */
lingcod.MpaCreator.prototype.enableButton = function(button) {
    button.removeAttr('disabled');
}
