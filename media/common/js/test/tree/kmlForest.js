module('kmlForest');

/**
 * Simply verify that the widget loads without throwing any errors (unless of course the proper options were not defined).
 */
test('initialize', function(){
    $(document.body).append('<div id="treetest"></div>');
    $('#treetest').kmlForest({ge: ge, gex: gex, animate: false});
    ok($('#treetest').kmlForest('length') == 0, 'No kml files loaded yet');
});

test('add', function(){
    stop();
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
        ok($('#treetest :contains(kmlForestTest.kmz)').length > 0, 'Proper nodes added to tree');
    }});
});

test('clear', function(){
    $('#treetest').kmlForest('clear');
    ok($('#treetest').kmlForest('length') == 0, 'All kml files removed');
    equals($('#treetest li').length, 0, 'All nodes from kmlForest removed along with them');
});

// this is here just to make sure the following tests can deal with more than
// one kml file being displayed
test('add extra kml file before continuing tests', function(){
    stop();
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/example_camera_view.kml', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
    }});
});

test('getByUrl', function(){
    stop();
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        var kmlObject = $('#treetest').kmlForest('getByUrl', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz');
        ok(kmlObject, 'returns value');
        equals(kmlObject.getName(), 'kmlForestTest.kmz', 'Is the correct kml file');
        $('#treetest').kmlForest('clear');
    }});
});

// this is here just to make sure the following tests can deal with more than
// one kml file being displayed
test('add extra kml file before continuing tests', function(){
    stop();
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/example_camera_view.kml', {cachebust: true, callback: function(){
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
        start();
    }});
});

test('remove', function(){
    stop();
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 2, 'KML file successfully loaded');
        $('#treetest').kmlForest('remove', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz');
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully removed');
        equals($('#treetest :contains("kmlForestTest.kmz")').length, 0, 'kmlForestTest.kmz removed');
    }});
});

test('add with relative path', function(){
    $('#treetest').kmlForest('clear');    
    // Not sure how to test this considering the location of the kml files in relation to where the tests are run
});

test('refresh', function(){
    // Not going to address this yet, since it requires remembering the on/off/open state of each element.
});


test('appropriate category header', function(){
    $('#treetest').kmlForest('clear');
    stop();
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
        ok($('#treetest .marinemap-tree-category').length == 1, 'Category created');
    }});
});

test('supports kml <a href="http://code.google.com/apis/kml/documentation/kmlreference.html#open">open tag</a>', function(){
    $('#treetest').kmlForest('clear');
    stop();
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
        equals($('#treetest a:contains("kmlForest Test File")').parent().find('> ul:visible').length, 1, "List should be visible, folder open");
        equals($('#treetest a:contains("closed folder")').parent().find('> ul:visible').length, 0, "'closed folder' should be closed");
    }});    
});

test('supports <a href="http://code.google.com/apis/kml/documentation/kmlreference.html#visibility">visibility tag</a>', function(){
    stop();
    $('#treetest').kmlForest('clear');
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
        equals($('#treetest a:contains("Visibility set to false")').length, 1, 'unchecked node exists.');
        equals($('#treetest a:contains("Visibility set to false")').parent().data('kml').getVisibility(), false, 'Node is not visible on the map.');
        equals($('#treetest a:contains("Visibility set to false")').parent().find('input:checked').length, 0, 'Checkbox is not checked.');
        
        equals($('#treetest a:contains("Placemark with description")').length, 1, 'checked node exists.');
        equals($('#treetest a:contains("Placemark with description")').parent().data('kml').getVisibility(), true, 'Node is visible on the map.');
        equals($('#treetest a:contains("Placemark with description")').parent().find('input:checked').length, 1, 'Checkbox is checked.');
    }});    
});

test('supports <a href="http://code.google.com/apis/kml/documentation/kmlreference.html#snippet">snippet tag</a>', function(){
    stop();
    $('#treetest').kmlForest('clear');
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
        equals($('#treetest a:contains("PhotoOverlay of South Coast Study Region")').length, 1, 'node with snippet exists.');
        equals($('#treetest a:contains("PhotoOverlay of South Coast Study Region")').parent().find('p.snippet').length, 1, 'Snippet is displayed.');
    }});    
    
});

test('toggle on/off features', function(){
    // check that toggling a feature works
    stop();
    $('#treetest').kmlForest('clear');
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
        // Make sure all other visibilities match up
        $('#treetest li').each(function(){
            var kml = $(this).data('kml');
            if(!$(this).hasClass('toggle')){
                ok(kml.getVisibility(), "init check: "+kml.getName() + ' node: KML is not toggle-able, so should have visibility set at true');
            }else{
                var text = "init check: "+'"' + kml.getName() + '" node ';
                var checked = $(this).find('> input:checked').length == 1;
                if(checked){
                    text += 'is checked so should be visible.'
                }else{
                    text += "is not checked so shouldn't be visible."
                }
                ok(checked == kml.getVisibility(), text)
            }
        });
        
        equals($('#treetest a:contains("Visibility set to false")').length, 1, 'invisible node exists');
        equals($('#treetest a:contains("One at a time")').length, 1, 'other invisible node exists');
        equals($('#treetest a:contains("Visibility set to false")').parent().data('kml').getVisibility(), false, 'invisible node does not show on map');
        var input = $('#treetest a:contains("Visibility set to false")').parent().find('input');
        // turn on visibility of feature
        input.click();
        equals($('#treetest a:contains("Visibility set to false")').parent().data('kml').getVisibility(), true, 'node turned on after click on map');
        equals($('#treetest a:contains("Visibility set to false")').parent().find('input:checked').length, 1, 'node turned on after click in list');
        
        // Make sure all other visibilities match up
        $('#treetest li').each(function(){
            var kml = $(this).data('kml');
            if(!$(this).hasClass('toggle')){
                ok(kml.getVisibility(), "toggle-on check: "+kml.getName() + ' node: KML is not toggle-able, so should have visibility set at true');
            }else{
                var text = "toggle-on check: "+'"' + kml.getName() + '" node ';
                var checked = $(this).find('> input:checked').length == 1;
                if(checked){
                    text += 'is checked so should be visible.'
                }else{
                    text += "is not checked so shouldn't be visible."
                }
                ok(checked == kml.getVisibility(), text)
            }
        });

        // turn off visibility of feature
        input.click();
        equals($('#treetest a:contains("Visibility set to false")').parent().data('kml').getVisibility(), false, 'node turned off on map');
        equals($('#treetest a:contains("Visibility set to false")').parent().find('input:checked').length, 0, 'node turned off in list');
        
        // Make sure all other visibilities match up
        $('#treetest li').each(function(){
            var kml = $(this).data('kml');
            if(!$(this).hasClass('toggle')){
                ok(kml.getVisibility(), "toggle-off check: "+kml.getName() + ' node: KML is not toggle-able, so should have visibility set at true');
            }else{
                var text = "toggle-off check: "+'"' + kml.getName() + '" node ';
                var checked = $(this).find('> input:checked').length == 1;
                if(checked){
                    text += 'is checked so should be visible.'
                }else{
                    text += "is not checked so shouldn't be visible."
                }
                ok(checked == kml.getVisibility(), text)
            }
        });
    }});    
    
    // then check that it hasn't messed with any of the others
});

test('toggle on/off folders toggles children', function(){
    // same as is tested in the tree tests, just check getVisibility()
    stop();
    $('#treetest').kmlForest('clear');
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
        var folder = $('#treetest a:contains("Both visible")').parent();
        var input = folder.find('>input');
        // toggle off
        input.click();
        var kml = folder.data('kml');
        ok(!kml.getVisibility(), 'Folder is now visible');
        ok(!kml.getFeatures().getLastChild().getVisibility(), 'Children are now visible');
        // toggle on now
        input.click();
        equals(kml.getVisibility(), true, 'Folder is now invisible');
        equals(kml.getFeatures().getLastChild().getVisibility(), true, 'Children are now visible');
    }});
});

test('semi-toggled state for parents with some children visible', function(){
    // this will require custom icons
});

test('features with descriptions have balloon link', function(){
    
});

var firstLat;

test('double click feature flys to feature', function(){
    stop();
    $('#treetest').kmlForest('clear');
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
        equals($('#treetest a:contains("Placemark without description")').length, 1, 'Placemark exists');
        firstLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
        $('#treetest a:contains("Placemark without description")').dblclick();
    }});
});

test('finish double click feature flys to feature', function(){
    stop();
    setTimeout(function(){
        var secondLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
        ok(firstLat != secondLat, "Viewport has changed after double-clicking the placemark");
        start();
    }, 500);
});

test('proper default icons given to folders, network links, features, etc', function(){
    // Just check the class for KmlFolder, KmlGroundOverlay, KmlPlacemark, KmlNetworkLink, etc
});

test('<a href="http://code.google.com/apis/kml/documentation/kmlreference.html#liststyle">ListStyle</a> support: radioFolder. All ListStyle support depends on <a href="http://code.google.com/p/earth-api-samples/issues/detail?id=303">this ticket</a>', function(){
    
});

test('<a href="http://code.google.com/apis/kml/documentation/kmlreference.html#liststyle">ListStyle</a> support: checkOffOnly', function(){
    
});

test('<a href="http://code.google.com/apis/kml/documentation/kmlreference.html#liststyle">ListStyle</a> support: checkHideChildren', function(){
    
});

test('<a href="http://code.google.com/apis/kml/documentation/kmlreference.html#liststyle">ListStyle</a> support: ItemIcon', function(){
    
});

test('Contents of NetworkLinks can be displayed. Depends on <a href="http://code.google.com/p/earth-api-samples/issues/detail?id=260&q=NetworkLink&colspec=ID%20Type%20Summary%20Component%20OpSys%20Browser%20Status%20Stars#c3">this ticket</a>, or a hack', function(){
    
});

// Not a very good test. If the double click event was instead causing the 
// viewport to zoom to the camera like any other feature, the bug likely
// wouldn't be detected. Should really be a ge.getTourPlayer().getTour() api.
// A feature request has been submitted for that function
// http://code.google.com/p/earth-api-samples/issues/detail?id=309
test('tours are activated when double-clicked.', function(){
    stop();
    $('#treetest').kmlForest('clear');
    $('#treetest').kmlForest('add', 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz', {cachebust: true, callback: function(){
        start();
        ok($('#treetest').kmlForest('length') == 1, 'KML file successfully loaded');
        equals($('#treetest a:contains("Tour Example")').length, 1, 'Tour exists');
        var firstLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
        $('#treetest a:contains("Tour Example")').dblclick();
        ge.getTourPlayer().play();
        var secondLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
        ok(firstLat != secondLat, "Assuming the latitude changes after double-clicking the tour, it must be active.");
        ge.getTourPlayer().pause();
    }});    
});

