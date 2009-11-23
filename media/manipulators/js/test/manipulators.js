module('Manipulators');

/**
 * Simply verify that the widget loads without throwing any errors (unless of course the proper options were not defined).
 */
test('initialize', function(){
    tool = new lingcod.DrawTool(ge, gex);
    manip = new lingcod.Manipulators('#main', null, tool);
    equals(manip.results_panel, '#main');
    equals(manip.renderCallBack, null);
    equals(manip.drawTool, tool);
    equals(manip.manipulator_list, null);
    equals(manip.success, false);
});

