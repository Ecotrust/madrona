module('ge-utility-lib-patches');

test("load kml and flyToView", function(){
    gex.dom.clearFeatures();
    gex.util.displayKml('http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/example_camera_view.kml', {'flyToView': true});
    stop();
    var found = false;
    setTimeout(function(){
        ok(ge.getFeatures().getChildNodes().getLength() == 1, 'KML added');
        ok(ge.getView().getViewportGlobeBounds().getNorth() > 34.84);
        start();
    }, 2000);
    // Leaving this test unfinished as kml can't be loaded from local disk.
});