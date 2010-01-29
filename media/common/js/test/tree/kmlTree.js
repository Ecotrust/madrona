module('kmlTree');

(function(){
    
    var kmlTreeUrl = 'http://marinemap.googlecode.com/svn-history/r869/trunk/media/projects/nc_mlpa/layers/uploaded-kml/ecotrustDataLayers.kml';
    var kmlTreeUrl2 = 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/kmlForestTest.kmz';
    var trans = 'http://chart.apis.google.com/chart?cht=p3&chs=1x1&chf=bg,s,EFEF0000';
    var traversal = 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/TreeTraversal.kmz';
    var NLHistory = 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/NLHistory.kmz';
    var NLHistory2 = 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/NLHistory2.kmz';
    var openNL = 'http://marinemap.googlecode.com/svn/trunk/media/common/fixtures/openNL.kmz';

    earthTest('create instance', 2, function(ge, gex){    
        $(document.body).append('<div id="kmltreetest"></div>');
        var errors = false;
        try{
            var tree = lingcod.kmlTree({
                gex: gex, 
                map_div: $('#map3d'), 
                element: $('#kmltreetest'),
                trans: trans,
                bustCache: false
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
            trans: trans,
            bustCache: false
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
            trans: trans,
            bustCache: false
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
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span.name:contains(Placemark without description)')
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
            fireEvents: function(){return true;},
            bustCache: false
        });
        var tree2 = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest2'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            equals(e.target, tree);
            $('#kmltreetest').find('span.name:contains(Placemark without description)')
                .click();
        });
        $(tree).bind('click', function(e, node, kmlObject){
            equals(kmlObject.getName(), 'Placemark without description');
            equals(e.target, tree);
        });
        $(tree2).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            equals(e.target, tree2);
            $('#kmltreetest2').find('span.name:contains(Placemark without description)')
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
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span.name:contains(Placemark without description)')
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
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span.name:contains(Placemark without description)')
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
            trans: trans,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(Placemark with ID)').parent();
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
            title: true,
            bustCache: false
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var closed = $('#kmltreetest').find('span.name:contains(closed folder)');
            equals(closed.length, 1);
            ok(!closed.parent().hasClass('open'));
            var open = $('#kmltreetest').find('span.name:contains(Radio Folder)');
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var nodes = tree.getNodesById('myId');
            var kmlObject = tree.lookup(nodes);
            equals(kmlObject.getName(), 'Placemark with ID');
            ok(nodes.hasClass('visible'));
            equals(kmlObject.getVisibility(), 1);
            var node = $('#kmltreetest').find('span.name:contains(Visibility set to false)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(PhotoOverlay of South Coast Study Region)').parent();
            equals(node.length, 1);
            equals(node.find('> .snippet').length, 1);
            var node = $('#kmltreetest').find('span.name:contains(Visibility set to false)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(Placemark without description)').parent();
            ok(!node.hasClass('hasDescription'));
            var node = $('#kmltreetest').find('span.name:contains(Placemark with description)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(closed folder)').parent();
            equals(node.find('> ul:visible').length, 0);
            var node = $('#kmltreetest').find('span.name:contains(Radio Folder)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(closed folder)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(PhotoOverlay of South Coast Study Region)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(Both visible)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(level 4)').parent();
            equals(node.length, 1);
            // All items off to start
            ok(!node.hasClass('visible'));
            // turn on
            node.find('> span.toggler').click();
            var kmlObject = tree.lookup(node);
            ok(kmlObject);
            ok(kmlObject.getVisibility());
            var level1 = $('#kmltreetest').find('span.name:contains(level 1)').parent();
            ok(level1.hasClass('visible'));
            ok(tree.lookup(level1).getVisibility());
            var level2sib = $('#kmltreetest').find('span.name:contains(level 2 sibling)').parent();
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
            title: true,
            bustCache: false
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

    earthAsyncTest('radioFolder support', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: kmlTreeUrl2,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(One at a time)').parent();
            var a = node.find('span.name:contains(Radio A)').parent();
            var b = node.find('span.name:contains(Radio B)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(One at a time)').parent();
            var a = node.find('span.name:contains(Radio A)').parent();
            var b = node.find('span.name:contains(Radio B)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var parent = $('#kmltreetest').find('span.name:contains(check off only)').parent();
            var a = parent.find('span.name:contains(a)').parent();
            var b = parent.find('span.name:contains(b)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var folder = $('#kmltreetest').find('span.name:contains(folder with contents hidden)').parent();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            ok(!ge.getBalloon(), 'start out with no balloon open.');
            var node = $('#kmltreetest').find('span.name:contains(Placemark with description)').parent();
            $('#kmltreetest').find('span.name:contains(Placemark with description)').click();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            ge.setBalloon(null);
            ok(!ge.getBalloon(), 'start out with no balloon open.');
            var node = $('#kmltreetest').find('span.name:contains(Placemark with description)').parent();
            $('#kmltreetest').find('span.name:contains(Placemark with description)').click();
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(Visibility set to false)').parent();
            node.find('span.name').dblclick();
            ok(tree.lookup(node).getVisibility(), 'Feature should be visible.');
            setTimeout(function(){
                var secondLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
                ok(secondLat !== firstLat);
                tree.destroy();
                $('#kmltreetest').remove();
                start();
            }, 400);
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span.name:contains(Placemark without description)').parent().find('span.icon').dblclick();
            setTimeout(function(){
                var secondLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
                ok(secondLat !== firstLat);
                tree.destroy();
                $('#kmltreetest').remove();
                start();
            }, 400);
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
            title: true,
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            var node = $('#kmltreetest').find('span.name:contains(Tour Example)').parent();
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
            fireEvents: function(){return true;},
            bustCache: false
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
            fireEvents: function(){return true;},
            bustCache: false
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
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $(tree).unbind('kmlLoaded');
            var nlink = $('#kmltreetest').find('span.name:contains(networklink a)').parent();
            var nlinkobject = tree.lookup(nlink);
            $(tree).bind('networklinkload', function(e, node, kmlObject){
                equals(kmlObject.getName(), 'linka.kmz');
                equals($('#kmltreetest').find('span.name:contains(NetworkLink Content)').length, 1, 'NetworkLink contents displayed.');
                equals(nlinkobject.getVisibility(), kmlObject.getVisibility());
                var pmark = $('#kmltreetest').find('li:contains(NetworkLink Content) span.name:contains(Untitled Placemark)');
                equals(pmark.length, 1);
                // toggling-off networklink toggles off linked document
                nlink.find('.toggler').click();
                equals(nlinkobject.getVisibility(), false, 'NetworkLink visibility off');
                equals(nlinkobject.getVisibility(), kmlObject.getVisibility(), 'Parent document visibility tracks NetworkLink visibility.');
                // Events still work (testing double-click on tree node)
                pmark.dblclick();
                setTimeout(function(){
                    var secondLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
                    ok(secondLat !== firstLat, 'Events on tree nodes should still function.');
                    tree.destroy();
                    $('#kmltreetest').remove();
                    start();                    
                }, 400);
            });
            nlink.find('.expander').click();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest('Networklinks that start out with visibility=0 should not be visible just because they have been loaded.', function(ge, gex){
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
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $(tree).unbind('kmlLoaded');
            var nlink = $('#kmltreetest').find('span.name:contains(networklink off)').parent();
            equals(nlink.length, 1);
            var nlinkobject = tree.lookup(nlink);
            $(tree).bind('networklinkload', function(e, node, kmlObject){
                equals(kmlObject.getName(), 'linka.kmz');
                equals($('#kmltreetest').find('span.name:contains(NetworkLink Content)').length, 1, 'NetworkLink contents displayed.');
                equals(nlinkobject.getVisibility(), kmlObject.getVisibility());
                tree.destroy();
                $('#kmltreetest').remove();
                start();                    
            });
            nlink.find('.expander').click();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest("NetworkLinks with listItemType=checkHideChildren don't expand", function(ge, gex){
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
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlDocument', 'KmlDocument loaded correctly');
            $(tree).unbind('kmlLoaded');
            var nlink = $('#kmltreetest').find('span.name:contains(networklink checkHideChildren)').parent();
            equals(nlink.find('.expander:visible').length, 0);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest("NetworkLinks with open=1 should automatically be loaded and expanded", function(ge, gex){
        var firstLat = ge.getView().copyAsCamera(ge.ALTITUDE_ABSOLUTE).getLatitude();
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: openNL,
            ge: ge,
            gex: gex,
            animate: false,
            map_div: $('#map3d'),
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false,
            restoreState: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'Kmz loaded correctly');
            $(tree).unbind('kmlLoaded');
            var nlink = $('#kmltreetest').find('span.name:contains(open networklink)').parent();
            ok(nlink.hasClass('loaded'));
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });


    earthAsyncTest("tree.walk visits in correct order", function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'Document loaded correctly');
            $(tree).unbind('kmlLoaded');
            var order = '';
            tree.walk(function(node){
                order += node.find('>span.name').text();
            });
            equals('FJBADCEGIH', order);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest("children ignored if callback returns false", function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'Document loaded correctly');
            $(tree).unbind('kmlLoaded');
            var order = '';
            tree.walk(function(node){
                var name = node.find('>span.name').text();
                order += name;
                if(name === 'B'){
                    return false;
                }
            });
            equals(order, 'FJBGIH');
            var order = '';
            tree.walk(function(node){
                var name = node.find('>span.name').text();
                order += name;
                if(name === 'D'){
                    return false;
                }
            });
            equals('FJBADGIH', order);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest("getState: one element turned off, then back on", function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'Document loaded correctly');
            $(tree).unbind('kmlLoaded');
            var E = $('#kmltreetest').find('span.name:contains(E)').parent();
            E.find('>span.toggler').click();
            var state = tree.getState();
            equals(state.name, 'root');
            equals(state.children.length, 1);
            equals(state.children[0].children[0].name, 'B');
            equals(state.children[0].children[0].children[0].name, 'D');
            equals(state.children[0].children[0].children[0].children.length, 1);
            equals(state.children[0].children[0].children[0].children[0].name, 'E');
            equals(state.children[0].children[0].children[0].children[0].modified.visibility.current, false);
            // turn back on
            E.find('>span.toggler').click();
            var state = tree.getState();
            // should just come back as not modified
            equals(state.children.length, 0);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest("getState: two elements turned off, affecting parents", function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'Document loaded correctly');
            $(tree).unbind('kmlLoaded');
            var E = $('#kmltreetest').find('span.name:contains(E)').parent();
            var C = $('#kmltreetest').find('span.name:contains(C)').parent();
            var A = $('#kmltreetest').find('span.name:contains(A)').parent();
            E.find('>span.toggler').click();
            C.find('>span.toggler').click();
            var state = tree.getState();
            equals(state.name, 'root');
            equals(state.children.length, 1);
            equals(state.children[0].children[0].name, 'B');
            equals(state.children[0].children[0].children[0].name, 'D');
            ok(state.children[0].children[0].children[0].modified && state.children[0].children[0].children[0].modified.visibility.current === false);
            equals(state.children[0].children[0].children[0].children.length, 2);
            equals(state.children[0].children[0].children[0].children[0].name, 'C');
            equals(state.children[0].children[0].children[0].children[1].name, 'E');
            ok(state.children[0].children[0].children[0].children[0].modified && state.children[0].children[0].children[0].children[0].modified.visibility.current === false);
            ok(state.children[0].children[0].children[0].children[1].modified && state.children[0].children[0].children[0].children[1].modified.visibility.current === false);
            A.find('>span.toggler').click();
            var state = tree.getState();
            equals(state.name, 'root');
            equals(state.children.length, 1);
            equals(state.children[0].children[0].name, 'B');
            ok(state.children[0].children[0].modified && state.children[0].children[0].modified.visibility.current === false);
            equals(state.children[0].children[0].children[0].name, 'A');
            ok(state.children[0].children[0].children[0].modified && state.children[0].children[0].children[0].modified.visibility.current === false);
            equals(state.children[0].children[0].children[1].children.length, 2);
            equals(state.children[0].children[0].children[1].children[0].name, 'C');
            equals(state.children[0].children[0].children[1].children[1].name, 'E');
            ok(state.children[0].children[0].children[1].children[0].modified && state.children[0].children[0].children[1].children[0].modified.visibility.current === false);
            ok(state.children[0].children[0].children[1].children[1].modified && state.children[0].children[0].children[1].children[1].modified.visibility.current === false);
            A.find('>span.toggler').click();
            // turn back on
            C.find('>span.toggler').click();
            var state = tree.getState();
            equals(state.name, 'root');
            equals(state.children.length, 1);
            equals(state.children[0].children[0].name, 'B');
            equals(state.children[0].children[0].children[0].name, 'D');
            equals(state.children[0].children[0].children[0].children.length, 1);
            equals(state.children[0].children[0].children[0].children[0].name, 'E');
            ok(state.children[0].children[0].children[0].children[0].modified && state.children[0].children[0].children[0].children[0].modified.visibility.current === false);
            // should just come back as not modified
            E.find('>span.toggler').click();
            var state = tree.getState();
            equals(state.children.length, 0);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest("getState: parent turned off, affecting children", function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'Document loaded correctly');
            $(tree).unbind('kmlLoaded');
            var B = $('#kmltreetest').find('span.name:contains(B)').parent();
            var A = $('#kmltreetest').find('span.name:contains(A)').parent();
            var D = $('#kmltreetest').find('span.name:contains(D)').parent();
            var C = $('#kmltreetest').find('span.name:contains(C)').parent();
            var E = $('#kmltreetest').find('span.name:contains(E)').parent();
            B.find('>span.toggler').click();
            var state = tree.getState();
            equals(state.name, 'root');
            equals(state.children.length, 1);
            equals(state.children[0].children[0].name, 'B');
            ok(state.children[0].children[0].modified && state.children[0].children[0].modified.visibility.current === false);
            equals(state.children[0].children[0].children[0].name, 'A');
            equals(state.children[0].children[0].children[0].modified.visibility.current, false);
            equals(state.children[0].children[0].children[1].name, 'D');
            equals(state.children[0].children[0].children[1].modified.visibility.current, false);
            equals(state.children[0].children[0].children[1].children[0].name, 'C');
            equals(state.children[0].children[0].children[1].children[0].modified.visibility.current, false);
            equals(state.children[0].children[0].children[1].children[1].name, 'E');
            equals(state.children[0].children[0].children[1].children[1].modified.visibility.current, false);
            E.find('>span.toggler').click();
            var state = tree.getState();
            // E will actually no longer be in the state results, because it starts out visible
            // equals(state.children[0].children[0].children[1].children[1].name, 'E');
            // equals(state.children[0].children[0].children[1].children[1].modified.visibility, true);            
            equals(state.children[0].children[0].children[1].children[0].name, 'C');
            equals(state.children[0].children[0].children[1].children[0].modified.visibility.current, false);
            // D will be in the tree, but not modified
            equals(state.children[0].children[0].children[1].name, 'D');
            equals(state.children[0].children[0].children[1]['modified'], undefined);
            // So is B
            equals(state.children[0].children[0].name, 'B');
            equals(state.children[0].children[0]['modified'], undefined);
            // Turn back on all B's children
            B.find('>span.toggler').click();
            B.find('>span.toggler').click();
            var state = tree.getState();
            equals(state.children.length, 0);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest("getState: getState tracks open state of Folders and NetworkLinks", function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'Document loaded correctly');
            $(tree).unbind('kmlLoaded');
            var B = $('#kmltreetest').find('span.name:contains(B)').parent();
            var A = $('#kmltreetest').find('span.name:contains(A)').parent();
            var D = $('#kmltreetest').find('span.name:contains(D)').parent();
            var C = $('#kmltreetest').find('span.name:contains(C)').parent();
            var E = $('#kmltreetest').find('span.name:contains(E)').parent();
            B.find('>span.expander').click();
            var state = tree.getState();
            equals(state.name, 'root');
            equals(state.children.length, 1);
            equals(state.children[0].children[0].name, 'B');
            ok(state.children[0].children[0].modified && state.children[0].children[0].modified.open.current === false);
            // Test can be simple, because it doesnt need to track up/down the tree like toggling
            B.find('>span.expander').click();
            var state = tree.getState();
            equals(state.children.length, 0);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest("getState: getState tracks open state", function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'Document loaded correctly');
            $(tree).unbind('kmlLoaded');
            var B = $('#kmltreetest').find('span.name:contains(B)').parent();
            var A = $('#kmltreetest').find('span.name:contains(A)').parent();
            var D = $('#kmltreetest').find('span.name:contains(D)').parent();
            var C = $('#kmltreetest').find('span.name:contains(C)').parent();
            var E = $('#kmltreetest').find('span.name:contains(E)').parent();
            B.find('>span.expander').click();
            var state = tree.getState();
            equals(state.name, 'root');
            equals(state.children.length, 1);
            equals(state.children[0].children[0].name, 'B');
            ok(state.children[0].children[0].modified && state.children[0].children[0].modified.open.current === false);
            // Test can be simple, because it doesnt need to track up/down the tree like toggling
            B.find('>span.expander').click();
            var state = tree.getState();
            equals(state.children.length, 0);
            tree.destroy();
            $('#kmltreetest').remove();
            start();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    

    earthAsyncTest('refresh tracks previous state', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span.name:contains(E)').parent().find('>span.toggler').click();
            $(tree).unbind('kmlLoaded');
            $(tree).bind('kmlLoaded', function(e, kmlObject){
                ok(true, 'kml refreshed');
                var E = $('#kmltreetest').find('span.name:contains(E)').parent();
                ok(!E.hasClass('visible'), 'History remembered in tree widget');
                ok(!tree.lookup(E).getVisibility(), 'Visibility set on kmlObject');
                tree.destroy();
                $('#kmltreetest').remove();
                start();
            });
            tree.refresh();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest('more complex example', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span.name:contains(H)').parent().find('>span.toggler').click();
            $('#kmltreetest').find('span.name:contains(G)').parent().find('>span.expander').click();
            $('#kmltreetest').find('span.name:contains(A)').parent().find('>span.toggler').click();
            $(tree).unbind('kmlLoaded');
            $(tree).bind('kmlLoaded', function(e, kmlObject){
                ok(true, 'kml refreshed');
                var A = $('#kmltreetest').find('span.name:contains(A)').parent();
                var H = $('#kmltreetest').find('span.name:contains(H)').parent();
                var G = $('#kmltreetest').find('span.name:contains(G)').parent();
                ok(!A.hasClass('visible'), 'History remembered in tree widget');
                ok(!tree.lookup(A).getVisibility(), 'Visibility set on kmlObject');
                ok(!H.hasClass('visible'), 'History remembered in tree widget');
                ok(!tree.lookup(H).getVisibility(), 'Visibility set on kmlObject');
                ok(!G.hasClass('visible'), 'History remembered in tree widget');
                ok(!G.hasClass('open'), 'History remembered in tree widget');
                ok(!tree.lookup(G).getVisibility(), 'Visibility set on kmlObject');
                tree.destroy();
                $('#kmltreetest').remove();
                start();
            });
            tree.refresh();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest('refreshing twice has the same affect', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            $(tree).unbind('kmlLoaded');
            ok(kmlObject.getType() === 'KmlFolder', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span.name:contains(H)').parent().find('>span.toggler').click();
            $('#kmltreetest').find('span.name:contains(G)').parent().find('>span.expander').click();
            $('#kmltreetest').find('span.name:contains(A)').parent().find('>span.toggler').click();
            $(tree).bind('kmlLoaded', function(e, kmlObject){
                $(tree).unbind('kmlLoaded');
                $(tree).bind('kmlLoaded', function(e, kmlObject){
                    $(tree).unbind('kmlLoaded');
                    ok(true, 'kml refreshed');
                    var A = $('#kmltreetest').find('span.name:contains(A)').parent();
                    var H = $('#kmltreetest').find('span.name:contains(H)').parent();
                    var G = $('#kmltreetest').find('span.name:contains(G)').parent();
                    ok(!A.hasClass('visible'), 'History remembered in tree widget');
                    ok(!tree.lookup(A).getVisibility(), 'Visibility set on kmlObject');
                    ok(!H.hasClass('visible'), 'History remembered in tree widget');
                    ok(!tree.lookup(H).getVisibility(), 'Visibility set on kmlObject');
                    ok(!G.hasClass('visible'), 'History remembered in tree widget');
                    ok(!G.hasClass('open'), 'History remembered in tree widget');
                    ok(!tree.lookup(G).getVisibility(), 'Visibility set on kmlObject');
                    tree.destroy();
                    $('#kmltreetest').remove();
                    start();
                });
                tree.refresh();                
            });
            tree.refresh();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest('history with networklinks', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: NLHistory,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'KmlDocument loaded correctly');
            $(tree).unbind('kmlLoaded');
            var L = $('#kmltreetest').find('span.name:contains(L)').parent();
            L.find('>span.expander').click();
            $(tree).bind('networklinkload', function(){
                $(tree).unbind('networklinkload');
                var X = $('#kmltreetest').find('span.name:contains(X)').parent();
                X.find('>span.toggler').click();
                ok(!X.hasClass('visible'));
                $(tree).bind('kmlLoaded', function(e, kmlObject){
                    $(tree).unbind('kmlLoaded');
                    ok(true, 'kml refreshed');
                    var X = $('#kmltreetest').find('span.name:contains(X)').parent();
                    var L = $('#kmltreetest').find('span.name:contains(L)').parent();
                    ok(L.hasClass('open'), 'Networklink open state remembered');
                    ok(!X.hasClass('visible'), 'History remembered in tree widget');
                    ok(!tree.lookup(X).getVisibility(), 'Visibility set on kmlObject');
                    tree.destroy();
                    $('#kmltreetest').remove();
                    start();
                });
                tree.refresh();
            });
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('more complex history with networklinks', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: NLHistory,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'KmlDocument loaded correctly');
            $(tree).unbind('kmlLoaded');
            var L = $('#kmltreetest').find('span.name:contains(L)').parent();
            L.find('>span.expander').click();
            $(tree).bind('networklinkload', function(){
                $(tree).unbind('networklinkload');
                var X = $('#kmltreetest').find('span.name:contains(X)').parent();
                var Z = $('#kmltreetest').find('span.name:contains(Z)').parent();
                var Y = $('#kmltreetest').find('span.name:contains(Y)').parent();
                X.find('>span.toggler').click();
                Y.find('>span.toggler').click();
                Z.find('>span.toggler').click();
                ok(!X.hasClass('visible'));
                ok(!Y.hasClass('visible'));
                ok(!Z.hasClass('visible'));
                $(tree).bind('kmlLoaded', function(e, kmlObject){
                    $(tree).unbind('kmlLoaded');
                    ok(true, 'kml refreshed');
                    var X = $('#kmltreetest').find('span.name:contains(X)').parent();
                    var Y = $('#kmltreetest').find('span.name:contains(Y)').parent();
                    var Z = $('#kmltreetest').find('span.name:contains(Z)').parent();
                    var L = $('#kmltreetest').find('span.name:contains(L)').parent();
                    ok(L.hasClass('open'), 'Networklink open state remembered');
                    ok(!L.hasClass('visible'), 'L should not be visible since children are not');
                    ok(!X.hasClass('visible'), 'History remembered in tree widget');
                    ok(!tree.lookup(X).getVisibility(), 'Visibility set on kmlObject');
                    ok(!Y.hasClass('visible'), 'History remembered in tree widget');
                    ok(!tree.lookup(Y).getVisibility(), 'Visibility set on kmlObject');
                    ok(!Z.hasClass('visible'), 'History remembered in tree widget');
                    ok(!tree.lookup(Z).getVisibility(), 'Visibility set on kmlObject');
                    tree.destroy();
                    $('#kmltreetest').remove();
                    start();
                });
                tree.refresh();
            });
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });

    earthAsyncTest('history with nested networklinks', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: NLHistory,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'KmlDocument loaded correctly');
            $(tree).unbind('kmlLoaded');
            var L = $('#kmltreetest').find('span.name:contains(L)').parent();
            $(tree).bind('networklinkload', function(){
                $(tree).unbind('networklinkload');
                $(tree).bind('networklinkload', function(){
                    $(tree).unbind('networklinkload');
                    var X = $('#kmltreetest').find('span.name:contains(X)').parent();
                    var Z = $('#kmltreetest').find('span.name:contains(Z)').parent();
                    var B = $('#kmltreetest').find('span.name:contains(B)').parent();
                    X.find('>span.toggler').click();
                    B.find('>span.toggler').click();
                    Z.find('>span.toggler').click();
                    ok(!X.hasClass('visible'));
                    ok(!B.hasClass('visible'));
                    ok(!Z.hasClass('visible'));
                    $(tree).bind('kmlLoaded', function(e, kmlObject){
                        $(tree).unbind('kmlLoaded');
                        ok(true, 'kml refreshed');
                        var X = $('#kmltreetest').find('span.name:contains(X)').parent();
                        var Y = $('#kmltreetest').find('span.name:contains(Y)').parent();
                        var B = $('#kmltreetest').find('span.name:contains(B)').parent();
                        var Z = $('#kmltreetest').find('span.name:contains(Z)').parent();
                        var L = $('#kmltreetest').find('span.name:contains(L)').parent();
                        var A = $('#kmltreetest').find('span.name:contains(A)').parent();
                        ok(L.hasClass('open'), 'Networklink open state remembered');
                        ok(L.hasClass('visible'));
                        ok(!X.hasClass('visible'), 'History remembered in tree widget');
                        ok(!tree.lookup(X).getVisibility(), 'Visibility set on kmlObject');
                        ok(Y.hasClass('open'), 'History remembered in tree widget');
                        ok(!B.hasClass('visible'), 'History remembered in tree widget');
                        ok(!tree.lookup(B).getVisibility(), 'Visibility set on kmlObject');
                        ok(!Z.hasClass('visible'), 'History remembered in tree widget');
                        ok(!tree.lookup(Z).getVisibility(), 'Visibility set on kmlObject');
                        tree.destroy();
                        $('#kmltreetest').remove();
                        start();
                    });
                    tree.refresh();
                });
                var Y = $('#kmltreetest').find('span.name:contains(Y)').parent();
                Y.find('>span.expander').click();
            });
            L.find('>span.expander').click();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest('state tracking can be turned off', function(ge, gex){
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            restoreStateOnRefresh: false,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            ok(kmlObject.getType() === 'KmlFolder', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span.name:contains(E)').parent().find('>span.toggler').click();
            $(tree).unbind('kmlLoaded');
            $(tree).bind('kmlLoaded', function(e, kmlObject){
                ok(true, 'kml refreshed');
                var E = $('#kmltreetest').find('span.name:contains(E)').parent();
                ok(E.hasClass('visible'));
                ok(tree.lookup(E).getVisibility());
                tree.destroy();
                $('#kmltreetest').remove();
                start();
            });
            tree.refresh();
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });
    
    earthAsyncTest('restore state using localStorage', function(ge, gex){
        if(!!window.localStorage){
            window.localStorage.clear();
        }
        $(document.body).append('<div id="kmltreetest"></div>');
        var tree = lingcod.kmlTree({
            url: traversal,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map3d'), 
            element: $('#kmltreetest'),
            trans: trans,
            restoreStateOnRefresh: false,
            restoreState: true,
            fireEvents: function(){return true;},
            bustCache: false
        });
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            $(tree).unbind('kmlLoaded');
            ok(kmlObject.getType() === 'KmlFolder', 'KmlDocument loaded correctly');
            $('#kmltreetest').find('span.name:contains(E)').parent().find('>span.toggler').click();
            var E = $('#kmltreetest').find('span.name:contains(E)').parent();
            ok(!E.hasClass('visible'));
            tree.destroy();
            $(document.body).append('<div id="kmltreetest"></div>');
            var tree2 = lingcod.kmlTree({
                url: traversal,
                ge: ge, 
                gex: gex, 
                animate: false, 
                map_div: $('#map3d'), 
                element: $('#kmltreetest'),
                trans: trans,
                restoreStateOnRefresh: false,
                restoreState: true,
                fireEvents: function(){return true;},
                bustCache: false
            });
            $(tree2).bind('kmlLoaded', function(e, kmlObject){
                ok(true, 'kml refreshed');
                var E = $('#kmltreetest').find('span.name:contains(E)').parent();
                ok(!E.hasClass('visible'));
                ok(!tree2.lookup(E).getVisibility());
                tree2.destroy();
                $('#kmltreetest').remove();
                start();
            });
            tree2.load(true);
        });
        ok(tree !== false, 'Tree initialized');
        tree.load(true);
    });    
    
})();