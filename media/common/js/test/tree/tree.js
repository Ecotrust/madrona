module("Tree");

test("initialize", function() {
    $(document.body).append('<ul id="treetest" />');
    equals($("#treetest").length, 1);
    $("#treetest").tree();
    ok($('#treetest').hasClass('marinemap-tree'), 'Should have class');
    $('#treetest').tree('destroy');
    $('#treetest').remove();
});

test("add", function(){
    $(document.body).append('<ul id="treetest" />');
    $("#treetest").tree();
    
    var node = $('#treetest').tree('add', {
        id: 'noIcon',
        name: 'Default Icon Category'
    });
    equals($('li.noIcon').length, 1);
    equals($('li.noIcon img.icon').length, 0);

    // test that category was created
    var myCategory = $('#treetest').tree('add', {
        id: 'myCategory',
        icon: 'http://null.net/icon.png',
        name: 'My Category',
        collapsible: true
    });
    equals($('li.myCategory').length, 1);
    equals($('li.myCategory ul').length, 1);
    equals($('li.myCategory img.icon').length, 1);
    
    equals($('li.myCategory > ul > li').length, 0);
    var node = $('#treetest').tree('add', {
        name: 'subelement',
        collapsible: false,
        parent: myCategory,
        data: {mydata: true}
    });
    equals($('li.myCategory > ul > li').length, 1);
    equals($(node).data('mydata'), true)
    $('#treetest').tree('destroy');
    $('#treetest').remove();
});

function setupTree(){
    $('#treetest').remove();
    $(document.body).append('<ul id="treetest" />');
    $("#treetest").tree();
    
    var node = $('#treetest').tree('add', {
        name: 'category',
        classname: 'marinemap-tree-category',
        toggle: false
    });
    
    var folder = $('#treetest').tree('add', {
        name: 'folder',
        toggle: true,
        collapsible: true,
        parent: node,
        open: true,
        checked: true
    });
    
    $('#treetest').tree('add', {
        name: 'child zero',
        toggle: true,
        collapsible: false,
        parent: folder
    });
    
    $('#treetest').tree('add', {
        name: 'child2',
        toggle: true,
        collapsible: false,
        parent: folder,
        checked: true
    });
    
    var subfolder = $('#treetest').tree('add', {
        name: 'sub folder',
        toggle: true,
        collapsible: true,
        parent: folder,
        checked: false,
        open: true
    });
    
    $('#treetest').tree('add', {
        name: 'child 1',
        toggle: true,
        collapsible: false,
        parent: subfolder,
        checked: false
    });
    
    $('#treetest').tree('add', {
        name: 'child 2',
        toggle: true,
        collapsible: false,
        parent: subfolder,
        checked: true
    });
    ok($('#treetest li a:contains(child 2)').length == 1, 'tree setup properly.');
}

test("clicking fires toggle event", function(){
    setupTree();
    $('#treetest').bind('itemToggle', function(e, clickedData, checked){
        ok(clickedData.length > 0, 'Event fired with proper clickedData');
        $('#treetest').unbind('itemToggle');
    });
    $('a:contains(child)').parent().find('> input').click();
});

test("when all children are toggled off so does the parent", function(){
    setupTree();
    $('a:contains(child2)').parent().find('>input').click();
    $('#treetest').bind('itemToggle', function(e, clickedData, checked){
        equals(clickedData.length, 3, 'Event fired with proper clickedData');
        $('#treetest').unbind('itemToggle');
    });
    $('a:contains(child 2)').parent().find('>input').click();
});

test("clicking off parent clears children", function(){
    setupTree();
    $('#treetest').bind('itemToggle', function(e, clickedData, checked){
        equals(clickedData.length, 3, 'Event fired with proper clickedData');
        $('#treetest').unbind('itemToggle');
    });
    $('a:contains(folder):first').parent().find('>input').click();
    $('#treetest').remove();
    
});