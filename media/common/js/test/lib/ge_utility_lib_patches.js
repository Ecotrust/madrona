module('ge-utility-lib-patches');

earthAsyncTest("load kml and flyToView", 2, function(ge, gex){
    gex.dom.clearFeatures();
    var oldNorth = ge.getView().getViewportGlobeBounds().getNorth();    
    gex.util.displayKml('http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/example_camera_view.kml', {'flyToView': true});
    var found = false;
    setTimeout(function(){
        start();
        ok(ge.getFeatures().getChildNodes().getLength() == 1, 'KML added');
        ok(ge.getView().getViewportGlobeBounds().getNorth() !== oldNorth, 'Viewport did not fly to layer extent.');
    }, 2000);
    // Leaving this test unfinished as kml can't be loaded from local disk.
});