module('DrawTool');

/**
 * Simply verify that the widget loads without throwing any errors (unless of course the proper options were not defined).
 */
test('initialize', function(){
    tool = new lingcod.DrawTool(ge, gex);
    equals(tool.gex, gex);
    equals(tool.targetShape, null);
    equals(tool.clippedShapeWKT, null);
    equals(tool.clippedShapeKML, null);
});