/**
 * Creates a new MpaCreator instance.
 * @constructor
 */
lingcod.MpaCreator = function(renderCallBack, manip_list, buttons) {
    this.drawTool = new lingcod.DrawTool();
    this.manipulators = new lingcod.Manipulators(renderCallBack, manip_list);
    this.create_button = buttons['create'];
    this.edit_button = buttons['edit'];
    this.finish_button = buttons['finish'];
    $('#'+this.create_button).removeAttr('disabled');
    $('#'+this.edit_button).attr('disabled', 'disabled');
    $('#'+this.finish_button).attr('disabled', 'disabled');
    $("#create_button").click($.delegate(this.drawAndProcess, this)); 
}

/**
 * Calls drawShape in DrawTool. Sets callback to processManipulators.
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
 * Calls hide in DrawTool.
 */
lingcod.MpaCreator.prototype.hide = function() {
    this.drawTool.hide();
}

/**
 * Calls clear in DrawTool.
 */
lingcod.MpaCreator.prototype.clear = function() {
    this.drawTool.clear();
}

/**
 * Calls editShape in DrawTool.
 */
lingcod.MpaCreator.prototype.editShape = function() {
    this.drawTool.editShape();
}

/**
 * Calls endEdit in DrawTool.  Sets callback to processManipulators.
 */
lingcod.MpaCreator.prototype.endEdit = function() {
    this.drawTool.endEdit($.delegate(this.processManipulators, this));
}

lingcod.MpaCreator.prototype.disableButton = function(button) {
    $('#'+button).attr('disabled', 'disabled');
}

lingcod.MpaCreator.prototype.enableButton = function(button) {
    $('#'+button).removeAttr('disabled');
}