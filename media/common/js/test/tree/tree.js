module("Tree");

test("initialize", 2, function() {
    $(document.body).append('<ul id="treetest" />');
    equals($("#treetest").length, 1);
    var tree = new lingcod.Tree({
        element: ("#treetest")
    });
    
    ok($('#treetest').hasClass('marinemap-tree'), 'Should have class');
    tree.destroy();
    $('#treetest').remove();
});

test("add", function(){
    $(document.body).append('<ul id="treetest" />');
    var tree = new lingcod.Tree({
        element: ("#treetest")
    });
    var node = tree.add({
        id: 'noIcon',
        name: 'Default Icon Category'
    });
    equals($('li.noIcon').length, 1);
    equals($('li.noIcon img.icon').length, 0);

    // test that category was created
    var myCategory = tree.add({
        id: 'myCategory',
        icon: 'http://null.net/icon.png',
        name: 'My Category',
        collapsible: true
    });
    equals($('li.myCategory').length, 1);
    equals($('li.myCategory ul').length, 1);
    equals($('li.myCategory img.icon').length, 1);
    
    equals($('li.myCategory > ul > li').length, 0);
    var node = tree.add({
        name: 'subelement',
        collapsible: false,
        parent: myCategory,
        data: {mydata: true}
    });
    equals($('li.myCategory > ul > li').length, 1);
    equals($(node).data('mydata'), true)
    tree.destroy();
    $('#treetest').remove();
});

function setupTree(){
    return setupTreeById('#treetest');
}

function setupTreeById(id){
    $(id).remove();
    var id_id = id.substring(1, id.length);
    $(document.body).append('<ul id="'+id_id+'" />');
    var tree = new lingcod.Tree({
        element: $(id)
    });
    var node = tree.add({
        name: 'category',
        classname: 'marinemap-tree-category',
        toggle: false
    });
    
    var folder = tree.add({
        name: 'folder',
        toggle: true,
        collapsible: true,
        parent: node,
        open: true,
        checked: true
    });
    
    tree.add({
        name: 'child zero',
        toggle: true,
        collapsible: false,
        parent: folder
    });
    
    tree.add({
        name: 'child2',
        toggle: true,
        collapsible: false,
        parent: folder,
        checked: true
    });
    
    var subfolder = tree.add({
        name: 'sub folder',
        toggle: true,
        collapsible: true,
        parent: folder,
        checked: false,
        open: true
    });
    
    tree.add({
        name: 'child 1',
        toggle: true,
        collapsible: false,
        parent: subfolder,
        checked: false
    });
    
    tree.add({
        name: 'child 2',
        toggle: true,
        collapsible: false,
        parent: subfolder,
        checked: true
    });
    ok($(id+' li a:contains(child 2)').length == 1, 'tree setup properly.');
    return tree;
}

test("clicking fires toggle event", function(){
    var tree = setupTree();
    $(tree).bind('itemToggle', function(e, clickedData, checked){
        ok(clickedData.length > 0, 'Event fired with proper clickedData');
        $(tree).unbind('itemToggle');
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

test("two trees shouldn't confuse event handlers", 4, function(){
    var tree2 = setupTreeById('#tree2');
    var tree1 = setupTreeById('#tree1');
    $(tree2).bind('itemClick', function(){
        equals(this, tree2);
    });
    $(tree1).bind('itemClick', function(){
        equals(this, tree1);
    });
    $(tree2.element.find('li.marinemap-tree-item a')[0]).click();
    $(tree1.element.find('li.marinemap-tree-item a')[0]).click();
});

test("two trees shouldn't confuse event handlers", 4, function(){
    var tree1 = setupTreeById('#tree1');
    var tree2 = setupTreeById('#tree2');
    $(tree2).bind('itemClick', function(){
        equals(this, tree2);
    });
    $(tree1).bind('itemClick', function(){
        equals(this, tree1);
    });
    $(tree2.element.find('li.marinemap-tree-item a')[0]).click();
    $(tree1.element.find('li.marinemap-tree-item a')[0]).click();
});