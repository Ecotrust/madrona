module('kmlTree');

(function(){
    
    var kmlTreeUrl = 'http://marinemap.googlecode.com/svn-history/r869/trunk/media/projects/nc_mlpa/layers/uploaded-kml/ecotrustDataLayers.kml';
    var kmlTreeUrl2 = 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz';
    var trans = 'http://chart.apis.google.com/chart?cht=p3&chs=1x1&chf=bg,s,EFEF0000';

    earthTest('create instance', 2, function(ge, gex){    
        $(document.body).append('<div id="kmltreetest"></div>');
        var errors = false;
        try{
            var tree = lingcod.kmlTree({
                gex: gex, 
                map_div: $('#map3d'), 
                element: $('#kmltreetest'),
                trans: trans
            });
        }catch(e){
            errors = true;
        }
        ok(errors);

        var tree = lingcod.kmlTree({
            url: kmlTreeUrl,
            gex: gex, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans
        });
        ok(tree !== false, 'Tree initialized');
        tree.destroy();
        $('#kmltreetest').remove();
    });

    earthAsyncTest('load kml, fire kmlLoaded event', 2, function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('click events', 4, function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;}
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span:contains(Placemark without description)')
                .click();
        });
        $(tree).bind('click', function(e, node, kmlObject){
            equals(kmlObject.getName(), 'Placemark without description');
            equals(e.target, tree);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('events arent confused across multiple instances', 9, function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        $(document.body).append('<div id="kmltreetest2"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;}
        });
        var tree2 = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest2'),
            trans: trans,
            fireEvents: function(){return true;}
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            equals(e.target, tree);
            $('#kmltreetest').find('span:contains(Placemark without description)')
                .click();
        });
        $(tree).bind('click', function(e, node, kmlObject){
            equals(kmlObject.getName(), 'Placemark without description');
            equals(e.target, tree);
        });
        $(tree2).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            equals(e.target, tree2);
            $('#kmltreetest2').find('span:contains(Placemark without description)')
                .click();
        });
        $(tree2).bind('click', function(e, node, kmlObject){
            equals(kmlObject.getName(), 'Placemark without description');
            equals(e.target, tree2);
            tree.destroy();
            tree2.destroy();
            $('#kmltreetest').remove();
            $('#kmltreetest2').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
        tree2.load(true);
    });

    earthAsyncTest('dblclick events', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;}
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span:contains(Placemark without description)')
                .dblclick();
        });
        $(tree).bind('dblclick', function(e, node, kmlObject){
            equals(kmlObject.getName(), 'Placemark without description');
            equals(e.target, tree);
            $('#kmltreetest').remove();
            tree.destroy();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('contextmenu events', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;}
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span:contains(Placemark without description)')
                .trigger('contextmenu');
        });
        $(tree).bind('contextmenu', function(e, node, kmlObject){
            equals(kmlObject.getName(), 'Placemark without description');
            equals(e.target, tree);
            $('#kmltreetest').remove();
            tree.destroy();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('getNodesById', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(Placemark with ID)').parent();
            equals(node.length, 1);
            var nodes = tree.getNodesById('myId');
            equals(nodes.length, 1);
            equals(nodes[0], node[0]);
            equals(tree.getNodesById('non-existent').length, 0);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('optional title support', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var title = $('#kmltreetest').find('h4:contains(kmlForestTest.kmz)');
            equals(title.length, 1);
            ok(title.hasClass('marinemap-kmltree-title'))
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('supports kml <a href="http://code.google.com/apis/kml/documentation/kmlreference.html#open">open tag</a>', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var closed = $('#kmltreetest').find('span:contains(closed folder)');
            equals(closed.length, 1);
            ok(!closed.parent().hasClass('open'));
            var open = $('#kmltreetest').find('span:contains(Radio Folder)');
            equals(open.length, 1);
            ok(open.parent().hasClass('open'));
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('supports <a href="http://code.google.com/apis/kml/documentation/kmlreference.html#visibility">visibility tag</a>', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var nodes = tree.getNodesById('myId');
            var kmlObject = tree.lookup(nodes);
            equals(kmlObject.getName(), 'Placemark with ID');
            ok(nodes.hasClass('visible'));
            equals(kmlObject.getVisibility(), 1);
            var node = $('#kmltreetest').find('span:contains(Visibility set to false)').parent();
            equals(node.length, 1);
            ok(!node.hasClass('visible'));
            var kmlObject = tree.lookup(node);
            equals(kmlObject.getName(), 'Visibility set to false');
            equals(kmlObject.getVisibility(), 0);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('supports <a href="http://code.google.com/apis/kml/documentation/kmlreference.html#snippet">snippet tag</a>', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(PhotoOverlay of South Coast Study Region)').parent();
            equals(node.length, 1);
            equals(node.find('> .snippet').length, 1);
            var node = $('#kmltreetest').find('span:contains(Visibility set to false)').parent();
            equals(node.length, 1);
            equals(node.find('> .snippet').length, 0);        
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('features with descriptions appear as a link', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(Placemark without description)').parent();
            ok(!node.hasClass('hasDescription'));
            var node = $('#kmltreetest').find('span:contains(Placemark with description)').parent();
            ok(node.hasClass('hasDescription'));
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest("open folder contents visible, closed folders' content not", function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(closed folder)').parent();
            equals(node.find('> ul:visible').length, 0);
            var node = $('#kmltreetest').find('span:contains(Radio Folder)').parent();
            equals(node.find('> ul:visible').length, 1);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('folders expand/collapse', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(closed folder)').parent();
            equals(node.length, 1);
            node.find('> span.expander').click();
            equals(node.find('>ul:visible').length, 1);
            node.find('> span.expander').click();
            equals(node.find('>ul:visible').length, 0);
            $('#kmltreetest').remove();
            tree.destroy();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('can toggle features', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(PhotoOverlay of South Coast Study Region)').parent();
            var kmlObject = tree.lookup(node);
            equals(node.length, 1);
            ok(!kmlObject.getVisibility());
            node.find('> span.toggler').click();
            ok(kmlObject.getVisibility());
            ok(kmlObject.getVisibility());
            node.find('> span.toggler').click();
            ok(!kmlObject.getVisibility());
            $('#kmltreetest').remove();
            tree.destroy();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('toggling folders toggles children', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(Both visible)').parent();
            var kmlObject = tree.lookup(node);
            equals(node.length, 1);
            // All items on to start
            ok(node.find('> ul > li.visible').length > 0);
            ok(kmlObject.getVisibility());
            // turn them off
            node.find('> span.toggler').click();
            equals(node.find('> ul > li.visible').length, 0);
            ok(!kmlObject.getVisibility());
            var child = node.find('> ul > li')[0];
            var childKml = tree.lookup(child);
            ok(childKml);
            ok(!childKml.getVisibility());
            // turn back on
            node.find('> span.toggler').click();
            ok(kmlObject.getVisibility());
            ok(childKml.getVisibility());
            $('#kmltreetest').remove();
            tree.destroy();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('toggling child toggles all parents', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(level 4)').parent();
            equals(node.length, 1);
            // All items off to start
            ok(!node.hasClass('visible'));
            // turn on
            node.find('> span.toggler').click();
            var kmlObject = tree.lookup(node);
            ok(kmlObject);
            ok(kmlObject.getVisibility());
            var level1 = $('#kmltreetest').find('span:contains(level 1)').parent();
            ok(level1.hasClass('visible'));
            ok(tree.lookup(level1).getVisibility());
            var level2sib = $('#kmltreetest').find('span:contains(level 2 sibling)').parent();
            ok(!level2sib.hasClass('visible'));
            ok(!tree.lookup(level2sib).getVisibility());
            $('#kmltreetest').remove();
            tree.destroy();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('toggling all children off toggles parents off', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        $('#kmltreetest').remove();
        start();
    });

    // // Tests for when a semi-toggled state for folders is implemented
    // 
    // earthAsyncTest('toggling child with no siblings toggles folder', function(ge, gex){
    //     $(document.body).append('<div id="kmltreetest"></div>');
    //     $('#kmltreetest').remove();
    //     start();
    // });
    // 
    // earthAsyncTest('toggling one of many children semi-toggles folder', function(ge, gex){
    //     $(document.body).append('<div id="kmltreetest"></div>');
    //     $('#kmltreetest').remove();
    //     start();
    // });
    // 
    // earthAsyncTest('semi-toggling travels up deeply nested trees', function(ge, gex){
    //     $(document.body).append('<div id="kmltreetest"></div>');
    //     $('#kmltreetest').remove();
    //     start();
    // });

    earthAsyncTest('list items given class names matching kmlObject.getType()', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            ok($('#kmltreetest').find('li.KmlPlacemark').length > 0);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('<a href="http://code.google.com/apis/kml/documentation/kmlreference.html#liststyle">ListStyle</a> support: radioFolder. All ListStyle support depends on <a href="http://code.google.com/p/earth-api-samples/issues/detail?id=303">this ticket</a>', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(One at a time)').parent();
            var a = node.find('span:contains(Radio A)').parent();
            var b = node.find('span:contains(Radio B)').parent();
            ok(node.length === 1);
            ok(a.length === 1);
            ok(b.length === 1);
            ok(node.hasClass('radioFolder'));
            var kmlObject = tree.lookup(node);
            // start out not visible
            ok(!kmlObject.getVisibility());
            node.find('> span:toggler').click();
            ok(kmlObject.getVisibility());
            ok(tree.lookup(a).getVisibility());
            ok(a.hasClass('visible'));
            ok(!tree.lookup(b).getVisibility());
            ok(!b.hasClass('visible'));
            b.find('> span:toggler').click();
            ok(!tree.lookup(a).getVisibility());
            ok(tree.lookup(b).getVisibility());
            b.find('> span:toggler').click();
            ok(!tree.lookup(a).getVisibility());
            ok(!tree.lookup(b).getVisibility())
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest("toggling parent of radio folder doesn't toggle all radioFolder children.", function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(One at a time)').parent();
            var a = node.find('span:contains(Radio A)').parent();
            var b = node.find('span:contains(Radio B)').parent();
            ok(node.length === 1);
            ok(a.length === 1);
            ok(b.length === 1);
            ok(node.hasClass('radioFolder'));
            var parent = node.parent().parent();
            parent.find('> span.toggler').click();
            parent.find('> span.toggler').click();
            parent.find('> span.toggler').click();        
            ok(!tree.lookup(parent).getVisibility(), 
                'Startout with parent and children cleared');
            ok(!tree.lookup(a).getVisibility(), 
                'Startout with parent and children cleared');
            ok(!tree.lookup(b).getVisibility(), 
                'Startout with parent and children cleared');
            parent.find('> span.toggler').click();        
            ok(tree.lookup(a).getVisibility(), 'Should turn on the first child.');
            ok(!tree.lookup(b).getVisibility(), 
                'Only one child of a radioFolder should be turned on at a time.');
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('<a href="http://code.google.com/apis/kml/documentation/kmlreference.html#liststyle">ListStyle</a> support: checkOffOnly', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var parent = $('#kmltreetest').find('span:contains(check off only)').parent();
            var a = parent.find('span:contains(a)').parent();
            var b = parent.find('span:contains(b)').parent();
            ok(tree.lookup(parent).getVisibility());
            ok(tree.lookup(a).getVisibility());
            ok(tree.lookup(b).getVisibility());
            parent.find('> span.toggler').click();
            ok(!tree.lookup(parent).getVisibility(), 
                'Parent visibility off after click.');
            ok(!tree.lookup(a).getVisibility(), 
                'Both children should be turned off by click on parent.');
            ok(!tree.lookup(b).getVisibility(),
                'Both children should be turned off by click on parent.');

            parent.find('> span.toggler').click();
            ok(!tree.lookup(parent).getVisibility() &&
                !tree.lookup(a).getVisibility() && 
                !tree.lookup(b).getVisibility(),
                'Should not be able to toggle visibility with listItemType = checkOffOnly.');
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('<a href="http://code.google.com/apis/kml/documentation/kmlreference.html#liststyle">ListStyle</a> support: checkHideChildren', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var folder = $('#kmltreetest').find('span:contains(folder with contents hidden)').parent();
            ok(folder.find('> span.toggler:visible').length === 0, 'Toggle icon should not be visible');
            ok(folder.find('> ul > li').length === 0, 'Shouldnt add children');
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('<a href="http://code.google.com/apis/kml/documentation/kmlreference.html#liststyle">ListStyle</a> support: ItemIcon', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        $('#kmltreetest').remove();
        start();
    });

    earthAsyncTest('click on elements with descriptions opens balloon.', function(ge, gex){
        var firstLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            ok(!ge.getBalloon(), 'start out with no balloon open.');
            var node = $('#kmltreetest').find('span:contains(Placemark with description)').parent();
            $('#kmltreetest').find('span:contains(Placemark with description)').click();
            ok(ge.getBalloon(), 'Balloon should now be open.');
            ok(tree.lookup(node).getVisibility(), 'Should be visible if viewing balloon.');
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('Untoggling feature with balloon closes it.', function(ge, gex){
        var firstLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            ge.setBalloon(null);
            ok(!ge.getBalloon(), 'start out with no balloon open.');
            var node = $('#kmltreetest').find('span:contains(Placemark with description)').parent();
            $('#kmltreetest').find('span:contains(Placemark with description)').click();
            ok(ge.getBalloon(), 'Balloon should now be open.');
            ok(tree.lookup(node).getVisibility(), 'Should be visible if viewing balloon.');
            node.find('> span.toggler').click();
            ok(!tree.lookup(node).getVisibility(), 'Feature should be invisible');
            ok(!ge.getBalloon(), 'Balloon should be closed.');
            ge.setBalloon(null);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('double click feature flys to feature', function(ge, gex){
        var firstLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(Visibility set to false)').parent();
            $('#kmltreetest').find('span:contains(Visibility set to false)').dblclick();
            ok(tree.lookup(node).getVisibility(), 'Feature should be visible.');
            setTimeout(function(){
                var secondLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
                ok(secondLat !== firstLat);
                tree.destroy();
                $('#kmltreetest').remove();
                start();
            }, 100);
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('double click works on icons too', function(ge, gex){
        var firstLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span:contains(Placemark without description)').parent().find('span.icon').dblclick();
            setTimeout(function(){
                var secondLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
                ok(secondLat !== firstLat);
                tree.destroy();
                $('#kmltreetest').remove();
                start();
            }, 100);
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    // Not a very good test. If the double click event was instead causing the 
    // viewport to zoom to the camera like any other feature, the bug likely
    // wouldn't be detected. Should really be a ge.getTourPlayer().getTour() api.
    // A feature request has been submitted for that function
    // http://code.google.com/p/earth-api-samples/issues/detail?id=309
    earthAsyncTest('tours are activated when double-clicked.', function(ge, gex){
        var firstLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span:contains(Tour Example)').parent();
            ok(node.length, "Tour exists");
            var firstLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
            node.dblclick();
            ge.getTourPlayer().play();
            var secondLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
            ok(firstLat != secondLat, "Assuming the latitude changes after double-clicking the tour, it must be active.");
            ge.getTourPlayer().pause();
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('refresh reloads kml tree', 3, function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;}
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $(tree).unbind('kmlLoaded');
            $(tree).bind('kmlLoaded', function(e, kmlObject){
                ok(true, 'kml refreshed');
                tree.destroy();
                $('#kmltreetest').remove();
                start();
            });
            tree.refresh();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('selectNode', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;}
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $(tree).unbind('kmlLoaded');
            $(tree).bind('kmlLoaded', function(e, kmlObject){
                ok(true, 'kml refreshed');
                tree.destroy();
                $('#kmltreetest').remove();
                start();
            });
            tree.refresh();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('selectById', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        $('#kmltreetest').remove();
        start();
    });

    earthAsyncTest('Contents of NetworkLinks can be displayed. Depends on <a href="http://code.google.com/p/earth-api-samples/issues/detail?id=260&q=NetworkLink&colspec=ID%20Type%20Summary%20Component%20OpSys%20Browser%20Status%20Stars#c3">this ticket</a>, or a hack', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;}
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $(tree).unbind('kmlLoaded');
            // tree.destroy();
            // $('#kmltreetest').remove();
            // start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest("NetworkLinks with listItemType=checkHideChildren don't expand", function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;}
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $(tree).unbind('kmlLoaded');
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('networklink content fetched when expanded', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        $('#kmltreetest').remove();
        start();
    });

    earthAsyncTest('refresh reloads kml tree', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        $('#kmltreetest').remove();
        start();
    });

    earthAsyncTest('refresh tracks previous state', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        $('#kmltreetest').remove();
        start();
    });
    
})();