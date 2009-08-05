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
    
});

test('toggle on/off folders and NetworkLinks', function(){
    
});

test('semi-toggled state for parents with some children visible', function(){
    
});

test('features with descriptions have balloon link', function(){
    
});

test('double click feature flys to feature', function(){
    
});

test('proper default icons given to folders, network links, features, etc', function(){
    
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