module('panel_manager');

test("panels navigatable", function(){
    stop();
    $.get('../media/panel_manager.html', function(data){
        var panelManager = $(data).find('#panelManager');
        start();
        ok(panelManager.length == 1, 'ajax request for setup successful');
        $(document.body).append(panelManager);
        var mngr = $('#panelManager').panelManager({top: '3em', left: '0px'});
        ok(mngr.length == 1, 'panelManager created.');
        ok($('li.ui-state-active a[href="#tab1"]').length == 1, 'Starts with tab1 active');
        $('a[href="#tab4"]').click();
        ok($("li.ui-state-active a[href='#tab4']").length == 1, 'Tab changed to tab4');
        equals(mngr.panelManager('getStack').length, 1, "only home panel in stack");
    });
});

test("home -> panel 1 navigatable", function(){
    var mngr = $('#panelManager');
    stop();
    mngr.unbind('panelChange');
    mngr.bind('panelChange', function(event, data){
        equals($(data).find('h1').html(), 'Panel 1', 'The appropriate panel loaded.');
        $('#link1').click();
        equals($(data).find('h1').html(), 'Panel 1', 'Clicking link to current panel causes no change.');
        equals(mngr.panelManager('getStack').length, 2, "only home panel and panel 1 in stack");
        start();
    });
    $('#panelTests').click();
});

test("panel 1 -> home works", function(){
    var mngr = $('#panelManager');
    mngr.unbind('panelChange');
    stop();
    mngr.bind('panelChange', function(event, data){
        equals($(data).find('a[href="#tab4"]').html(), 'Tab 4', 'Home panel shown.');
        equals(mngr.panelManager('getStack').length, 1, "only home panel in stack");
        start();
    });
    $('.back_link').click();
});

test("home -> panel 1", function(){
    var mngr = $('#panelManager');
    stop();
    mngr.unbind('panelChange');
    mngr.bind('panelChange', function(event, data){
        equals($(data).find('h1').html(), 'Panel 1', 'The appropriate panel loaded.');
        equals(mngr.panelManager('getStack').length, 2, "only home panel and panel 1 in stack");
        start();
    });
    $('#panelTests').click();
});

test("panel 1 -> panel 2", function(){
    var mngr = $('#panelManager');
    stop();
    mngr.unbind('panelChange');
    mngr.bind('panelChange', function(event, data){
        equals($(data).find('h1').html(), 'Panel 2', 'The appropriate panel loaded.');
        equals(mngr.panelManager('getStack').length, 3, "home, panel 1 & 2 in stack");
        start();
    });
    $('#link2').click();
});

test("panel 2 -> panel 3", function(){
    var mngr = $('#panelManager');
    stop();
    mngr.unbind('panelChange');
    mngr.bind('panelChange', function(event, data){
        equals($(data).find('h1').html(), 'Panel 3', 'The appropriate panel loaded.');
        equals(mngr.panelManager('getStack').length, 4, "home, panel 1, 2 & 3 in stack");
        start();
    });
    $('#link3').click();
});

test("panel 3 -> panel 2 via back button", function(){
    var mngr = $('#panelManager');
    stop();
    mngr.unbind('panelChange');
    mngr.bind('panelChange', function(event, data){
        equals($(data).find('h1').html(), 'Panel 2', 'The appropriate panel loaded.');
        equals(mngr.panelManager('getStack').length, 3, "home, panel 1 & 2 in stack");
        start();
    });
    $('.back_link').click();
});

test("panel 2 -> panel 1 via link", function(){
    var mngr = $('#panelManager');
    stop();
    mngr.unbind('panelChange');
    mngr.bind('panelChange', function(event, data){
        equals($(data).find('h1').html(), 'Panel 1', 'The appropriate panel loaded.');
        equals(mngr.panelManager('getStack').length, 2, "only home panel and panel 1 in stack");
        start();
    });
    $('#link1').click();
});

test("panel 1 -> panel 3 (hopping over 2)", function(){
    var mngr = $('#panelManager');
    stop();
    mngr.unbind('panelChange');
    mngr.bind('panelChange', function(event, data){
        equals($(data).find('h1').html(), 'Panel 3', 'The appropriate panel loaded.');
        equals(mngr.panelManager('getStack').length, 3, "home, panel 1 & 3 in stack");
        start();
    });
    $('#link3').click();
});

test("panel 3 -> panel 2", function(){
    var mngr = $('#panelManager');
    stop();
    mngr.unbind('panelChange');
    mngr.bind('panelChange', function(event, data){
        equals($(data).find('h1').html(), 'Panel 2', 'The appropriate panel loaded.');
        equals(mngr.panelManager('getStack').length, 3, "home, panel 1 & 2 in stack");
        start();
    });
    $('.back_link').click();
});

test("panel 2 -> panel 3", function(){
    var mngr = $('#panelManager');
    stop();
    mngr.unbind('panelChange');
    mngr.bind('panelChange', function(event, data){
        equals($(data).find('h1').html(), 'Panel 3', 'The appropriate panel loaded.');
        start();
    });
    $('#link3').click();
});