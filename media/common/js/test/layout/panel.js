(function(){
    
    // This is helpful during development of tests, but may hide errors in
    // handling caching in the actual panel component. Be careful!
    $.ajaxSetup({
        cache: false
    });
    
    var html = [
        '<div>',
            '<style id="ssheet1" type="text/css" media="screen">',
                'div#foo {padding:100px;};',
            '</style>',
            '<script type="text/javascript" charset="utf-8">',
                'lingcod.onShow(function(){',
                	"$(document.body).append('<div id=\"sctSuccess\" />');",
                '});',
                'lingcod.onShow(function(){',
                	"$(document.body).append('<div id=\"sctSuccess2\" />');",
                '});',
            '</script>',
            // should be ignored
            '<script src="blah.js" type="text/javascript" charset="utf-8">',
            '</script>',
            // html should make it out and be available via 
            // SanitizedContent#html
            '<p id="foo">bar</p></div>',
        '</div>'
    ].join('');
    
    var html2 = [
        '<div>',
            '<style id="ssheet1" type="text/css" media="screen">',
                'div#foo {padding:100px;};',
            '</style>',
            '<script type="text/javascript" charset="utf-8">',
                'lingcod.onShow(function(){',
                	"$(document.body).append('<div id=\"sctSuccess\" />');",
                '});',
                'lingcod.onShow("#tab1", function(){',
                	"$(document.body).append('<div id=\"tabSuccess1\" />');",
                '});',
                'lingcod.onShow("#tab2", function(){',
                	"$(document.body).append('<div id=\"tabSuccess2\" />');",
                '});',
                'lingcod.onShow("#tab2", function(){',
                	"$(document.body).append('<div id=\"tabSuccess22\" />');",
                '});',
            '</script>',
            '<div class="tabs">',
                '<ul>',
                    '<li><a href="tab1"><span>tab1</span></a></li>',
                    '<li><a href="tab2"><span>tab2</span></a></li>',
                '</ul>',
                '<div id="tab1"></div>',
                '<div id="tab2"></div>',
            '</div>',
        '</div>'
    ].join('');
        
    module('SanitizedContent');
    
    test('strips out style and script tags', function(){
        var content = new lingcod.layout.SanitizedContent(html);
        ok(!content.html.match('script'), 'script tags removed');
        ok(!content.html.match('style'), 'style tags removed');
        ok(content.html.match('foo'), 'html left intact');
    });

    test('addStylesToDocument', function(){
        var content = new lingcod.layout.SanitizedContent(html);
        content.addStylesToDocument();
        ok($('#ssheet1').length === 1, 'stylesheet added to doc');
        var content = new lingcod.layout.SanitizedContent(html);
        content.addStylesToDocument();
        ok($('#ssheet1').length === 1, 'stylesheet added to doc only once');
    });
    
    test('finds onShow callbacks', function(){
        var content = new lingcod.layout.SanitizedContent(html);
        var callbacks = content.extractCallbacks();
        ok(callbacks['panel'] && callbacks['panel'].show && 
            callbacks['panel'].show.length === 2, 'found two callbacks');
        callbacks['panel'].show[0](); callbacks['panel'].show[1]();
        ok($('#sctSuccess').length === 1, 'appropriate callbacks stored.');
        ok($('#sctSuccess2').length === 1, 'appropriate callbacks stored.');
        $('#sctSuccess, #sctSuccess2').remove();
    });

    test('finds onShow callbacks bound to tabs', function(){
        var content = new lingcod.layout.SanitizedContent(html2);
        var callbacks = content.extractCallbacks();
        ok(callbacks['panel']);
        ok(callbacks['panel'] && callbacks['panel'].show && 
            callbacks['panel'].show.length === 1, 'found one panel callback');
        ok(callbacks['tabs'] && callbacks['tabs']['#tab1'].show.length === 1, 
            'found one callback for tab1');
        ok(callbacks['tabs'] && callbacks['tabs']['#tab2'].show.length === 2, 
            'found two callbacks for tab2');
        callbacks['panel'].show[0]();
        ok($('#sctSuccess').length === 1, 'appropriate callbacks stored.');
        callbacks['tabs']['#tab1'].show[0]();
        ok($('#tabSuccess1').length === 1, 'appropriate callbacks stored.');
        callbacks['tabs']['#tab2'].show[0]();
        ok($('#tabSuccess2').length === 1, 'appropriate callbacks stored.');
        callbacks['tabs']['#tab2'].show[1]();
        ok($('#tabSuccess22').length === 1, 'appropriate callbacks stored.');
        $('#tabSuccess22, #tabSuccess2, #tabSuccess1, #sctSuccess').remove();
    });
    
    module('contentLoader');
    
    asyncTest('error handling', function(){
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        var loader = lingcod.contentLoader({
            url: '../url/that/doesnt/exist/',
            target: target,
            success: function(){
                ok(false, 
                    'success called even though content does not exist!');
                $('#target').remove();
                start();
            },
            error: function(){
                ok(true, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    // Verify creation of tabs and subtabs from markup
    // ===============================================
    
    asyncTest('verify "a simple panel" example from docs.', function(){
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/example1.html',
            target: target,
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                $('#target').remove();
                start();
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('verify "synchronous tabs" example from docs.', function(){
        var t = $('<div id="target"></div>');
        $(document.body).append(t);
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/example2.html',
            target: t,
            success: function(){
                ok(true, 'content loaded.');
                ok(t.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                ok(t.find('#Report').hasClass('ui-tabs-hide') === true, 
                    'Report tab content should be hidden');
                ok(t.find('#Attributes').hasClass('ui-tabs-hide') === false, 
                    'Attributes tab content should be shown');
                // make sure tabs are working
                t.find('a[href=#Report]').click();
                ok(t.find('#Report').hasClass('ui-tabs-hide') === false, 
                    'Clicking tab should show it.');
                ok(t.find('#Attributes').hasClass('ui-tabs-hide') === true, 
                    'Attributes tab content should be hidden now.');
                $('#target').remove();
                start();
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });

    asyncTest('verify "asynchronous tabs" example from docs.', function(){
        var t = $('<div id="target"></div>');
        $(document.body).append(t);
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/example3.html',
            target: t,
            success: function(){
                ok(true, 'content loaded.');
                ok(t.find('.panel').length === 1, 
                    'appended to target and success handler called.');
                ok(t.find('#Report').length === 0, 
                    'No report div yet.');
                ok(t.find('#Attributes').hasClass('ui-tabs-hide') === false, 
                    'Attributes tab content should be shown');
                // make sure tabs are working
                t.find('a:contains(Report)').click();
                t.find('.tabs').bind('tabsload', function(){
                    t.find('.tabs').unbind('tabsload');
                    ok(t.find('img.chart').length === 1, 'content loaded');
                    var report = t.find('img.chart').parent().parent();
                    ok(!report.hasClass('ui-tabs-hide'), 
                        'Report tab is shown');
                    ok(t.find('#Attributes').hasClass('ui-tabs-hide'), 
                        'Attributes tab content should be hidden now');
                    $('#target').remove();
                    start();
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('synchronous tabs with subtabs.', function(){
        var t = $('<div id="target"></div>');
        $(document.body).append(t);
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/example4.html',
            target: t,
            success: function(){
                ok(true, 'content loaded.');
                ok(t.find('.panel').length === 1, 
                    'appended to target and success called afterwards.');
                ok(t.find('#Report').hasClass('ui-tabs-hide') === true, 
                    'Report tab content should be hidden');
                ok(t.find('#Attributes').hasClass('ui-tabs-hide') === false, 
                    'Attributes tab content should be shown');
                // make sure tabs are working
                t.find('a[href=#Report]').click();
                ok(t.find('#Report').hasClass('ui-tabs-hide') === false, 
                    'Clicking tab should show it.');
                ok(t.find('#Attributes').hasClass('ui-tabs-hide') === true, 
                    'Attributes tab content should be hidden now.');
                var subtabs = t.find('#Report');
                ok(subtabs.find('ul').hasClass('ui-tabs-nav'), 
                    'subtabs active');
                ok(!subtabs.find('#chart').hasClass('ui-tabs-hide'), 
                    'first subtab shown');
                ok(subtabs.find('#grid').hasClass('ui-tabs-hide'), 
                    'second subtab hidden');
                subtabs.find('a:contains(Grid)').click();
                ok(subtabs.find('#chart').hasClass('ui-tabs-hide'), 
                    'first subtab hidden');
                ok(!subtabs.find('#grid').hasClass('ui-tabs-hide'), 
                    'second subtab shown');
                $('#target').remove();
                start();
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('synchronous tabs with async subtabs.', function(){
        var t = $('<div id="target"></div>');
        $(document.body).append(t);
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/example6.html',
            target: t,
            success: function(){
                ok(true, 'content loaded.');
                ok(t.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                ok(t.find('#Report').hasClass('ui-tabs-hide') === true, 
                    'Report tab content should be hidden');
                ok(t.find('#Attributes').hasClass('ui-tabs-hide') === false, 
                    'Attributes tab content should be shown');
                // make sure tabs are working
                t.find('a[href=#Report]').click();
                ok(t.find('#Report').hasClass('ui-tabs-hide') === false, 
                    'Clicking tab should show it.');
                ok(t.find('#Attributes').hasClass('ui-tabs-hide') === true, 
                    'Attributes tab content should be hidden now.');
                ok(!t.find('#sub1').hasClass('ui-tabs-hide'), 
                    'first subtab selected');
                t.find('a:contains(subtab2)').click();
                t.find('.tabs').bind('tabsload', function(){
                    t.find('.tabs').unbind('tabsload');
                    // A timeout has to go here because tabsload actually
                    // fires before the content is shown, and tabsshow is 
                    // called evenbefore that
                    setTimeout(function(){
                        ok(t.find('img.chart').length === 1, 
                            'content loaded');
                        var subtab1 = t.find('img.chart').parent().parent();
                        var parent = subtab1.parent().parent();
                        ok(!parent.hasClass('ui-tabs-hide'), 
                            'subtab2 is shown');
                        t.find('a:contains(subtab1)').click();
                        ok(!t.find('#sub1').hasClass('ui-tabs-hide'), 
                            'first subtab now selected');
                        start();
                    }, 100);
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('async tabs with subtabs.', function(){
        $('#target').remove();
        var t = $('<div id="target"></div>');
        $(document.body).append(t);
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/example5.html',
            target: t,
            success: function(){
                ok(true, 'content loaded.');
                ok(t.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                ok(t.find('#Report').length === 0, 
                    'No report div yet.');
                ok(t.find('#Attributes').hasClass('ui-tabs-hide') === false, 
                    'Attributes tab content should be shown');
                // make sure tabs are working
                t.find('a:contains(Report)').click();
                t.find('.tabs').bind('tabsload', function(){
                    t.find('.tabs').unbind('tabsload');
                    // A timeout has to go here because tabsload actually
                    // fires before the content is shown, and tabsshow is 
                    // called evenbefore that
                    setTimeout(function(){
                        ok(t.find('img.chart').length === 1, 
                            'content loaded');
                        var reports = t.find('img.chart').parent().parent();
                        var parent = reports.parent().parent();
                        ok(!parent.hasClass('ui-tabs-hide'), 
                            'Report tab is shown');
                        ok(t.find('#Attributes').hasClass('ui-tabs-hide'), 
                            'Attributes tab content should be hidden now');
                        ok(!reports.find('#chart').hasClass('ui-tabs-hide'), 
                            'first subtab shown');
                        ok(reports.find('#grid').hasClass('ui-tabs-hide'), 
                            'second subtab hidden');
                        reports.find('a:contains(Grid)').click();
                        ok(reports.find('#chart').hasClass('ui-tabs-hide'), 
                            'first subtab hidden');
                        ok(!reports.find('#grid').hasClass('ui-tabs-hide'), 
                            'second subtab shown');
                        $('#target').remove();
                        start();                        
                    }, 200);
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('async tabs with async subtabs.', function(){
        $('#target').remove();
        var t = $('<div id="target"></div>');
        $(document.body).append(t);
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/example7.html',
            target: t,
            success: function(){
                ok(true, 'content loaded.');
                ok(t.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                ok(t.find('#Report').length === 0, 
                    'No report div yet.');
                ok(t.find('#Attributes').hasClass('ui-tabs-hide') === false, 
                    'Attributes tab content should be shown');
                // make sure tabs are working
                t.find('a:contains(Report)').click();
                t.find('.tabs').bind('tabsload', function(){
                    t.find('.tabs').unbind('tabsload');
                    // A timeout has to go here because tabsload actually
                    // fires before the content is shown, and tabsshow is 
                    // called evenbefore that
                    setTimeout(function(){
                        ok(t.find('img.chart1').length === 1, 
                            'content loaded');
                        var reports = t.find('img.chart1').parent().parent();
                        var parent = reports.parent().parent();
                        ok(!parent.hasClass('ui-tabs-hide'), 
                            'Report tab is shown');
                        ok(t.find('#Attributes').hasClass('ui-tabs-hide'), 
                            'Attributes tab content should be hidden now');
                        ok(!reports.find('#subtab1').hasClass('ui-tabs-hide'), 
                            'first subtab shown');
                        reports.find('a:contains(subtab2)').click();
                        parent.bind('tabsload', function(){
                            parent.unbind('tabsload');
                            setTimeout(function(){
                                ok(reports.find('img.chart'), 
                                    'subtab content loaded');
                                var subtab2 = reports.find('img.chart')
                                    .parent().parent();
                                ok(!subtab2.hasClass('ui-tabs-hide'), 
                                    'tab is shown');
                                $('#target').remove();
                                start();                                                        
                            }, 200);
                        });
                    }, 200);
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });

    // Verify stylesheet handling
    // ==========================
    
    asyncTest('verify simple css example from docs', function(){
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/cssExample1.html',
            target: target,
            success: function(){
                var target = $('#target');
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                equals($('#chartStyle').length, 1, 'Style added to document');
                $('#target').remove();
                var target = $('<div id="target"></div>');
                $(document.body).append(target);
                var numStyles = $('style').length;
                var loader = lingcod.contentLoader({
                    url: '../media/common/js/test/layout/cssExample1.html',
                    target: target,
                    error: function(){
                        ok(false, 'Could not load url.');
                        $('#target').remove();
                        start();
                    },
                    success: function(){
                        ok(true, 'content loaded.');
                        ok(target.find('.panel').length === 1, 
                            'content appended and success handler called.');
                        equals($('#chartStyle').length, 1, 
                            'Style added to document');
                        equals($('style').length, numStyles, 
                            'style tag only added once for the same id');
                        start();                        
                    }                
                });
                loader.load();
                
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    var numStyles;
    
    asyncTest('verify complex css example from docs \
        (2 style tags, one w/id one without)', function(){
        numStyles = 0;
        $('#target').remove();
        $('#chartStyle').remove();
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        numStyles = $('style').length;
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/cssExample2.html',
            target: target,
            success: function(){
                var target = $('#target');
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                equals($('#chartStyle').length, 1, 'Style added to document');
                equals($('style').length - numStyles, 2, 
                    'two style tags added');
                $('#target').remove();
                var target = $('<div id="target"></div>');
                $(document.body).append(target);
                numStyles = $('style').length;
                var loader = lingcod.contentLoader({
                    url: '../media/common/js/test/layout/cssExample2.html',
                    target: target,
                    error: function(){
                        ok(false, 'Could not load url.');
                        $('#target').remove();
                        start();
                    },
                    success: function(){
                        ok(true, 'content loaded.');
                        ok(target.find('.panel').length === 1, 
                            'content appended to target and success called.');
                        equals($('#chartStyle').length, 1, 
                            'only one style tag with id=chartStyle added');
                        equals(($('style').length - numStyles), 1, 
                            'only one style tag added the second time.');
                        $('#target').remove();
                        start();                        
                    }                
                });
                loader.load();
                
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('css stylesheets can be added via async tabs', function(){
        $('#exampleThreePointOneStyle').remove();
        $('#target').remove();
        numStyle = 0;
        var t = $('<div id="target"></div>');
        $(document.body).append(t);
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/example3.html',
            target: t,
            success: function(){
                ok(true, 'content loaded.');
                ok(t.find('.panel').length === 1, 
                    'appended to target and success handler called.');
                numStyle = $('style').length;
                t.find('a:contains(Report)').click();
                t.find('.tabs').bind('tabsload', function(){
                    t.find('.tabs').unbind('tabsload');
                    setTimeout(function(){
                        ok(t.find('img.chart').length === 1, 
                            'content loaded');
                        equals($('style').length - numStyle, 1, 
                            'One stylesheet added');
                        ok($('style#exampleThreePointOneStyle').length == 1, 
                            'has the right ID');
                        $('#target').remove();
                        start();
                        
                    }, 100);
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    // Verify javascript event handling
    // ================================
    
    asyncTest('verify 1st inline js example (onShow) from docs', function(){
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        window.callbackFired = 0;
        window.selectedEl = undefined;
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample1.html',
            target: target,
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                equals(window.callbackFired, 1, 'Callback was executed');
                equals(window.selectedEl.length, 1, 
                    'Callback executed after content was added to document');
                window.callbackFired = undefined;
                window.selectedEl = undefined;
                $('#target').remove();
                start();
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('verify 2nd inline js example (onShow with tabs)', function(){
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        window.callbackFired = 0;
        window.selectedEl = undefined;
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample2.html',
            target: target,
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                ok(!window.callbackFired, 'callback not fired yet.');
                ok(!window.selectedEl, 'callback not fired until tab click');
                $('a:contains(Report)').click();
                ok(window.callbackFired, 'callback fired after tab opened');
                ok(window.selectedEl.length == 1, 
                    'callback executed after content added to doc');
                window.callbackFired = undefined;
                window.selectedEl = undefined;
                $('a:contains(Information)').click();
                $('a:contains(Report)').click();
                ok(!window.callbackFired, 'onShow is called only once.');                
                $('#target').remove();
                start();
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });

    
    asyncTest('verify 3rd inline js example (onShow with tabs)', function(){
        var t = $('<div id="target"></div>');
        $(document.body).append(t);
        window.callbackFired = 0;
        window.selectedEl = undefined;
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample3.html',
            target: t,
            success: function(){
                ok(true, 'content loaded.');
                ok(t.find('.panel').length === 1, 
                    'appended to target and success handler called.');
                ok(!window.callbackFired, 'callback not fired yet.');
                ok(!window.selectedEl, 'callback not fired until tab click');
                t.find('a:contains(Report)').click();
                t.find('.tabs').bind('tabsload', function(){
                    t.find('.tabs').unbind('tabsload');
                    setTimeout(function(){
                        ok(t.find('img.chart').length === 1, 
                            'content loaded');
                        ok(window.callbackFired, 
                            'callback fired after tab opened');
                        ok(window.selectedEl.length == 1, 
                            'callback executed after content added to doc');
                        $('#target').remove();
                        start();
                        
                    }, 100);
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });

    asyncTest('same as above but w/callback on first tab as well', function(){
        var t = $('<div id="target"></div>');
        $(document.body).append(t);
        window.callbackFired = 0;
        window.selectedEl = undefined;
        window.callbackOne = 0;
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample4.html',
            target: t,
            success: function(){
                ok(true, 'content loaded.');
                ok(t.find('.panel').length === 1, 
                    'appended to target and success handler called.');
                ok(!window.callbackFired, 'callback not fired yet.');
                ok(!window.selectedEl, 'callback not fired until tab click');
                ok(window.callbackOne, "first tab's callback fired");
                t.find('a:contains(Report)').click();
                t.find('.tabs').bind('tabsload', function(){
                    t.find('.tabs').unbind('tabsload');
                    setTimeout(function(){
                        ok(t.find('img.chart').length === 1, 
                            'content loaded');
                        ok(window.callbackFired, 
                            'callback fired after tab opened');
                        ok(window.selectedEl.length == 1, 
                            'callback executed after content added to doc');
                        t.find('a:contains(Information)').click();
                        equals(window.callbackOne, 1, 
                            "first tab's callback fires only once");                        
                        t.find('a:contains(Report)').click();
                        equals(window.callbackFired, 1, 
                            "second tab's callback fires only once");                        
                        $('#target').remove();
                        start();
                        
                    }, 100);
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });

    asyncTest('onHide/onUnhide with synchronous tabs', function(){
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        // zero out variables that the callbacks will interact with
        window.attributesShown      = 0;
        window.attributesUnhidden   = 0;
        window.attributesHidden     = 0;
        window.reportShown          = 0;
        window.reportUnhidden       = 0;
        window.reportHidden         = 0;

        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample5.html',
            target: $('#target'),
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                    
                // test initial state callbacks
                equals(window.attributesShown, 1, 'attributes onshow fired');
                equals(window.attributesUnhidden, 1, 
                    'attributes onUnhide fired');
                equals(window.attributesHidden, 0, 
                    'attributes onHide not fired yet');
                equals(window.reportHidden, 0, 
                    'report onHide not fired yet');
                equals(window.reportShown, 0, 
                    'report onShow not fired yet');
                equals(window.reportUnhidden, 0, 
                    'report onUnhide not fired yet');

                // change to reports tab
                target.find('a:contains(Report)').click();
                
                equals(window.attributesShown, 1, "hasn't changed");
                equals(window.attributesUnhidden, 1, 
                    "hasn't changed");
                equals(window.attributesHidden, 1, 
                    'attributes onHide fired');
                equals(window.reportHidden, 0, 
                    'report onHide not fired yet');
                equals(window.reportShown, 1, 
                    'report onShow fired');
                equals(window.reportUnhidden, 1, 
                    'report onUnhide fired');
                
                // change back to attributes
                target.find('a:contains(Information)').click();
                equals(window.attributesShown, 1, "onShow fires only once");
                equals(window.attributesUnhidden, 2, 
                    "onUnhide called again");
                equals(window.attributesHidden, 1, 
                    'unchanged');
                equals(window.reportHidden, 1, 
                    'report onHide fired');
                equals(window.reportShown, 1, 
                    'unchanged');
                equals(window.reportUnhidden, 1, 
                    'unchanged');

                // change back to reports
                target.find('a:contains(Report)').click();
                equals(window.attributesShown, 1, "onShow fires only once");
                equals(window.attributesUnhidden, 2, 
                    "unchanged");
                equals(window.attributesHidden, 2, 
                    'attributes onHide called again');
                equals(window.reportHidden, 1, 
                    'unchanged');
                equals(window.reportShown, 1, 
                    'only called once');
                equals(window.reportUnhidden, 2, 
                    'report onUnhide called again');

                
                // cleanup
                window.attributesShown      = 0;
                window.attributesUnhidden   = 0;
                window.attributesHidden     = 0;
                window.reportShown          = 0;
                window.reportUnhidden       = 0;
                window.reportHidden         = 0;
                
                $('#target').remove();
                start();
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('onHide/onUnhide with async tabs', function(){
        $('#target').remove();
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        // zero out variables that the callbacks will interact with
        window.attributesShown      = 0;
        window.attributesUnhidden   = 0;
        window.attributesHidden     = 0;
        window.reportShown          = 0;
        window.reportUnhidden       = 0;
        window.reportHidden         = 0;
        
        window.onUnhideSelected = false;

        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample6.html',
            target: $('#target'),
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                    
                // test initial state callbacks
                equals(window.attributesShown, 1, 'attributes onshow fired');
                equals(window.attributesUnhidden, 1, 
                    'attributes onUnhide fired');
                equals(window.attributesHidden, 0, 
                    'attributes onHide not fired yet');
                equals(window.reportHidden, 0, 
                    'report onHide not fired yet');
                equals(window.reportShown, 0, 
                    'report onShow not fired yet');
                equals(window.reportUnhidden, 0, 
                    'report onUnhide not fired yet');

                // change to reports tab
                target.find('a:contains(Report)').click();
                
                target.find('.tabs').bind('tabsload', function(){
                    target.find('.tabs').unbind('tabsload');
                    setTimeout(function(){                
                        equals(window.attributesShown, 1, "hasn't changed");
                        equals(window.attributesUnhidden, 1, 
                            "hasn't changed");
                        equals(window.attributesHidden, 1, 
                            'attributes onHide fired');
                        equals(window.reportHidden, 0, 
                            'report onHide not fired yet');
                        equals(window.reportShown, 1, 
                            'report onShow fired');
                        equals(window.reportUnhidden, 1, 
                            'report onUnhide fired');
                
                        // change back to attributes
                        target.find('a:contains(Information)').click();
                        equals(window.attributesShown, 1, 
                            "onShow fires only once");
                        equals(window.attributesUnhidden, 2, 
                            "onUnhide called again");
                        equals(window.attributesHidden, 1, 
                            'unchanged');
                        equals(window.reportHidden, 1, 
                            'report onHide fired');
                        equals(window.reportShown, 1, 
                            'unchanged');
                        equals(window.reportUnhidden, 1, 
                            'unchanged');

                        // change back to reports
                        target.find('a:contains(Report)').click();
                        equals(window.attributesShown, 1, 
                            "onShow fires only once");
                        equals(window.attributesUnhidden, 2, 
                            "unchanged");
                        equals(window.attributesHidden, 2, 
                            'attributes onHide called again');
                        equals(window.reportHidden, 1, 
                            'unchanged');
                        equals(window.reportShown, 1, 
                            'only called once');
                        equals(window.reportUnhidden, 2, 
                            'report onUnhide called again');

                
                        // cleanup
                        window.attributesShown      = 0;
                        window.attributesUnhidden   = 0;
                        window.attributesHidden     = 0;
                        window.reportShown          = 0;
                        window.reportUnhidden       = 0;
                        window.reportHidden         = 0;
                
                        $('#target').remove();
                        start();
                        
                    }, 100);                    
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();        
    });
    
    asyncTest('nested tabs with onHide/onUnhide', function(){
        $('#target').remove();
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        // zero out variables that the callbacks will interact with
        window.attributesShown      = 0;
        window.attributesUnhidden   = 0;
        window.attributesHidden     = 0;
        window.reportShown          = 0;
        window.reportUnhidden       = 0;
        window.reportHidden         = 0;
                               
        window.subtab1Shown         = 0;
        window.subtab1Unhidden      = 0;
        window.subtab1Hidden        = 0;
        window.subtab2Shown         = 0;
        window.subtab2Unhidden      = 0;
        window.subtab2Hidden        = 0;    

        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample7.html',
            target: $('#target'),
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                    
                // test initial state callbacks
                equals(window.attributesShown, 1, 
                    'attributes onshow fired');
                equals(window.attributesUnhidden, 1, 
                    'attributes onUnhide fired');
                equals(window.attributesHidden, 0, 
                    'attributes onHide not fired yet');
                equals(window.reportHidden, 0, 
                    'report onHide not fired yet');
                equals(window.reportShown, 0, 
                    'report onShow not fired yet');
                equals(window.reportUnhidden, 0, 
                    'report onUnhide not fired yet');
                // subtabs
                equals(window.subtab1Shown, 0,
                    'subtab1 not shown yet');
                equals(window.subtab1Unhidden, 0,
                    'subtab1 not unhidden yet');
                equals(window.subtab1Hidden, 0,
                    'subtab1 not hidden yet');
                equals(window.subtab2Shown, 0,
                    'subtab2 not shown yet');
                equals(window.subtab2Unhidden, 0,
                    'subtab2 not unhidden yet');
                equals(window.subtab2Hidden, 0,
                    'subtab2 not hidden yet');

                // change to reports tab
                target.find('a:contains(Report)').click();
                
                target.find('.tabs').bind('tabsload', function(){
                    target.find('.tabs').unbind('tabsload');
                    setTimeout(function(){
                        
                        equals(window.attributesShown, 1, 
                            'unchanged');
                        equals(window.attributesUnhidden, 1, 
                            'unchanged');
                        equals(window.attributesHidden, 1, 
                            'attributes onHide fired');
                        equals(window.reportHidden, 0, 
                            'report onHide not fired yet');
                        equals(window.reportShown, 1, 
                            'report onShow fired');
                        equals(window.reportUnhidden, 1, 
                            'report onUnhide fired');
                        // subtabs    
                        equals(window.subtab1Shown, 1,
                            'subtab1 onShow fired');
                        equals(window.subtab1Unhidden, 1,
                            'subtab1 onUnhide fired');
                        equals(window.subtab1Hidden, 0,
                            'subtab1 not hidden yet');
                        equals(window.subtab2Shown, 0,
                            'subtab2 not shown yet');
                        equals(window.subtab2Unhidden, 0,
                            'subtab2 not unhidden yet');
                        equals(window.subtab2Hidden, 0,
                            'subtab2 not hidden yet');

                        // switch to subtab2
                        target.find('a:contains(subtab2)').click();
                        target.find('.tabs').bind('tabsload', function(){
                            target.find('.tabs').unbind('tabsload');
                            setTimeout(function(){
                                ok(true, 'tab loaded');
                                
                                equals(window.attributesShown, 1, 
                                    'unchanged');
                                equals(window.attributesUnhidden, 1, 
                                    'unchanged');
                                equals(window.attributesHidden, 1, 
                                    'unchanged');
                                equals(window.reportHidden, 0, 
                                    'unchanged');
                                equals(window.reportShown, 1, 
                                    'unchanged');
                                equals(window.reportUnhidden, 1, 
                                    'unchanged');
                                // subtabs    
                                equals(window.subtab1Shown, 1,
                                    'unchanged');
                                equals(window.subtab1Unhidden, 1,
                                    'unchanged');
                                equals(window.subtab1Hidden, 1,
                                    'now hidden');
                                equals(window.subtab2Shown, 1,
                                    'now shown');
                                equals(window.subtab2Unhidden, 1,
                                    'onUnhide fired');
                                equals(window.subtab2Hidden, 0,
                                    'subtab2 has not been hidden yet');
                                
                                // Now go back to subtab1
                                target.find('a:contains(subtab1)').click();
                                
                                equals(window.attributesShown, 1, 
                                    'unchanged');
                                equals(window.attributesUnhidden, 1, 
                                    'unchanged');
                                equals(window.attributesHidden, 1, 
                                    'unchanged');
                                equals(window.reportHidden, 0, 
                                    'unchanged');
                                equals(window.reportShown, 1, 
                                    'unchanged');
                                equals(window.reportUnhidden, 1, 
                                    'unchanged');
                                // subtabs    
                                equals(window.subtab1Shown, 1,
                                    'fires only once');
                                equals(window.subtab1Unhidden, 2,
                                    'onUnhide should fire again');
                                equals(window.subtab1Hidden, 1,
                                    'unchanged');
                                equals(window.subtab2Shown, 1,
                                    'unchanged');
                                equals(window.subtab2Unhidden, 1,
                                    'unchanged');
                                equals(window.subtab2Hidden, 1,
                                    'now hidden');
                                
                                // change back to attributes
                                target.find('a:contains(Information)')
                                    .click();
                                
                                equals(window.attributesShown, 1, 
                                    'fires only once');
                                equals(window.attributesUnhidden, 2, 
                                    'fired again');
                                equals(window.attributesHidden, 1, 
                                    'unchanged');
                                equals(window.reportHidden, 1, 
                                    'now hidden');
                                equals(window.reportShown, 1, 
                                    'unchanged');
                                equals(window.reportUnhidden, 1, 
                                    'unchanged');
                                // subtabs    
                                equals(window.subtab1Shown, 1,
                                    'unchanged');
                                equals(window.subtab1Unhidden, 2,
                                    'unchanged');
                                equals(window.subtab1Hidden, 2,
                                    'hidden again');
                                equals(window.subtab2Shown, 1,
                                    'unchanged');
                                equals(window.subtab2Unhidden, 1,
                                    'unchanged');
                                equals(window.subtab2Hidden, 1,
                                    'unchanged');


                                // cleanup
                                window.attributesShown      = 0;
                                window.attributesUnhidden   = 0;
                                window.attributesHidden     = 0;
                                window.reportShown          = 0;
                                window.reportUnhidden       = 0;
                                window.reportHidden         = 0;

                                window.subtab1Shown         = 0;
                                window.subtab1Unhidden      = 0;
                                window.subtab1Hidden        = 0;
                                window.subtab2Shown         = 0;
                                window.subtab2Unhidden      = 0;
                                window.subtab2Hidden        = 0;

                                $('#target').remove();
                                start();
                                
                            }, 100);
                        });                        
                    }, 100);                    
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();        
    });
    
    asyncTest('beforeDestroy w/simple example', function(){
        $('#target').remove();
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        window.callbackFired = 0;
        window.selectedEl = undefined;
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample8.html',
            target: target,
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                loader.destroy();
                equals(window.callbackFired, 1, 'Callback was executed');
                ok(window.selectedEl && window.selectedEl.length === 1, 
                    'Callback executed after content was added to document');
                window.callbackFired = undefined;
                window.selectedEl = undefined;
                $('#target').remove();
                start();
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('beforeDestroy specified by async tab', function(){
        $('#target').remove();
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        window.callbackFired = 0;
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample9.html',
            target: target,
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                target.find('a:contains(Report)').click();
                target.find('.tabs').bind('tabsload', function(){
                    target.find('.tabs').unbind('tabsload');
                    setTimeout(function(){
                        loader.destroy();
                        equals(window.callbackFired, 3, 
                            '3 Callbacks executed');
                        window.callbackFired = undefined;
                        $('#target').remove();
                        start();
                        
                    }, 100);
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
        
    asyncTest('beforeDestroy defined in multiple nested tabs', function(){
        $('#target').remove();
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        window.callbackFired = 0;
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample10.html',
            target: target,
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                target.find('a:contains(Report)').click();
                target.find('.tabs').bind('tabsload', function(){
                    target.find('.tabs').unbind('tabsload');
                    setTimeout(function(){
                        target.find('.tabs').bind('tabsload', function(){
                            target.find('.tabs').unbind('tabsload');
                            setTimeout(function(){
                                loader.destroy();
                                equals(window.callbackFired, 4, 
                                    '4 Callbacks executed');
                                $('#target').remove();
                                start();
                            }, 100);
                        });
                        target.find('a:contains(subtab2)').click();
                    }, 40);
                });
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('super combo callback test', function(){
        $('#target').remove();
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        
        // panel
        window.panelShow               = 0;
        window.panelUnhide             = 0;
        window.panelBeforeDestroy      = 0;
        // attributes tab
        window.attributesShow          = 0;
        window.attributesUnhide        = 0;
        window.attributesHide          = 0;
        // report tab
        window.reportShow              = 0;
        window.reportUnhide            = 0;
        window.reportHide              = 0;
        window.reportBeforeDestroy     = 0;
        // subtab1
        window.subtab1Show             = 0;
        window.subtab1Unhide           = 0;
        window.subtab1Hide             = 0;
        // subtab2
        window.subtab2Show             = 0;
        window.subtab2Unhide           = 0;
        window.subtab2Hide             = 0;
        window.subtab2BeforeDestroy    = 0;
        
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample11.html',
            target: target,
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                
                // initial state
                // panel
                equals(window.panelShow, 1,
                    "triggered");
                equals(window.panelUnhide, 1,
                    "triggered");
                equals(window.panelBeforeDestroy, 0,
                    "unchanged");
                // attributes tab
                equals(window.attributesShow, 1,
                    "triggered");
                equals(window.attributesUnhide, 1,
                    "triggered");
                equals(window.attributesHide, 0,
                    "unchanged");
                // report tab
                equals(window.reportShow, 0,
                    "unchanged");
                equals(window.reportUnhide, 0,
                    "unchanged");
                equals(window.reportHide, 0,
                    "unchanged");
                equals(window.reportBeforeDestroy, 0,
                    "unchanged");
                // subtab1
                equals(window.subtab1Show, 0,
                    "unchanged");
                equals(window.subtab1Unhide, 0,
                    "unchanged");
                equals(window.subtab1Hide, 0,
                    "unchanged");
                // subtab2
                equals(window.subtab2Show, 0,
                    "unchanged");
                equals(window.subtab2Unhide, 0,
                    "unchanged");
                equals(window.subtab2Hide, 0,
                    "unchanged");
                equals(window.subtab2BeforeDestroy, 0,
                    "unchanged");
                
                target.find('a:contains(Report)').click();
                target.find('.tabs').bind('tabsload', function(){
                    target.find('.tabs').unbind('tabsload');
                    setTimeout(function(){
                        
                        ok(true, 'changed to report tab, subtab1 displayed');
                        
                        // panel
                        equals(window.panelShow, 1,
                            "unchanged");
                        equals(window.panelUnhide, 1,
                            "unchanged");
                        equals(window.panelBeforeDestroy, 0,
                            "unchanged");
                        // attributes tab
                        equals(window.attributesShow, 1,
                            "unchanged");
                        equals(window.attributesUnhide, 1,
                            "unchanged");
                        equals(window.attributesHide, 1,
                            "triggered");
                        // report tab
                        equals(window.reportShow, 1,
                            "triggered");
                        equals(window.reportUnhide, 1,
                            "triggered");
                        equals(window.reportHide, 0,
                            "unchanged");
                        equals(window.reportBeforeDestroy, 0,
                            "unchanged");
                        // subtab1
                        equals(window.subtab1Show, 1,
                            "triggered");
                        equals(window.subtab1Unhide, 1,
                            "triggered");
                        equals(window.subtab1Hide, 0,
                            "unchanged");
                        // subtab2
                        equals(window.subtab2Show, 0,
                            "unchanged");
                        equals(window.subtab2Unhide, 0,
                            "unchanged");
                        equals(window.subtab2Hide, 0,
                            "unchanged");
                        equals(window.subtab2BeforeDestroy, 0,
                            "unchanged");

                        // switch to subtab2
                        target.find('a:contains(subtab2)').click();
                        target.find('.tabs').bind('tabsload', function(){
                            target.find('.tabs').unbind('tabsload');
                            setTimeout(function(){
                                ok(true, 'changed to report tab->subtab2');

                                // panel
                                equals(window.panelShow, 1,
                                    "unchanged");
                                equals(window.panelUnhide, 1,
                                    "unchanged");
                                equals(window.panelBeforeDestroy, 0,
                                    "unchanged");
                                // attributes tab
                                equals(window.attributesShow, 1,
                                    "unchanged");
                                equals(window.attributesUnhide, 1,
                                    "unchanged");
                                equals(window.attributesHide, 1,
                                    "unchanged");
                                // report tab
                                equals(window.reportShow, 1,
                                    "unchanged");
                                equals(window.reportUnhide, 1,
                                    "unchanged");
                                equals(window.reportHide, 0,
                                    "unchanged");
                                equals(window.reportBeforeDestroy, 0,
                                    "unchanged");
                                // subtab1
                                equals(window.subtab1Show, 1,
                                    "unchanged");
                                equals(window.subtab1Unhide, 1,
                                    "unchanged");
                                equals(window.subtab1Hide, 1,
                                    "triggered");
                                // subtab2
                                equals(window.subtab2Show, 1,
                                    "triggered");
                                equals(window.subtab2Unhide, 1,
                                    "triggered");
                                equals(window.subtab2Hide, 0,
                                    "unchanged");
                                equals(window.subtab2BeforeDestroy, 0,
                                    "unchanged");
                                    
                                target.find('a:contains(subtab1)').click();
                                // panel
                                equals(window.panelShow, 1,
                                    "unchanged");
                                equals(window.panelUnhide, 1,
                                    "unchanged");
                                equals(window.panelBeforeDestroy, 0,
                                    "unchanged");
                                // attributes tab
                                equals(window.attributesShow, 1,
                                    "unchanged");
                                equals(window.attributesUnhide, 1,
                                    "unchanged");
                                equals(window.attributesHide, 1,
                                    "unchanged");
                                // report tab
                                equals(window.reportShow, 1,
                                    "unchanged");
                                equals(window.reportUnhide, 1,
                                    "unchanged");
                                equals(window.reportHide, 0,
                                    "unchanged");
                                equals(window.reportBeforeDestroy, 0,
                                    "unchanged");
                                // subtab1
                                equals(window.subtab1Show, 1,
                                    "unchanged");
                                equals(window.subtab1Unhide, 2,
                                    "triggered");
                                equals(window.subtab1Hide, 1,
                                    "unchanged");
                                // subtab2
                                equals(window.subtab2Show, 1,
                                    "unchanged");
                                equals(window.subtab2Unhide, 1,
                                    "unchanged");
                                equals(window.subtab2Hide, 1,
                                    "triggered");
                                equals(window.subtab2BeforeDestroy, 0,
                                    "unchanged");

                                target.find('a:contains(subtab2)').click();
                                // panel
                                equals(window.panelShow, 1,
                                    "unchanged");
                                equals(window.panelUnhide, 1,
                                    "unchanged");
                                equals(window.panelBeforeDestroy, 0,
                                    "unchanged");
                                // attributes tab
                                equals(window.attributesShow, 1,
                                    "unchanged");
                                equals(window.attributesUnhide, 1,
                                    "unchanged");
                                equals(window.attributesHide, 1,
                                    "unchanged");
                                // report tab
                                equals(window.reportShow, 1,
                                    "unchanged");
                                equals(window.reportUnhide, 1,
                                    "unchanged");
                                equals(window.reportHide, 0,
                                    "unchanged");
                                equals(window.reportBeforeDestroy, 0,
                                    "unchanged");
                                // subtab1
                                equals(window.subtab1Show, 1,
                                    "unchanged");
                                equals(window.subtab1Unhide, 2,
                                    "unchanged");
                                equals(window.subtab1Hide, 2,
                                    "triggered");
                                // subtab2
                                equals(window.subtab2Show, 1,
                                    "unchanged");
                                equals(window.subtab2Unhide, 2,
                                    "triggered");
                                equals(window.subtab2Hide, 1,
                                    "unchanged");
                                equals(window.subtab2BeforeDestroy, 0,
                                    "unchanged");

                                target.find('a:contains(Information)').click();
                                // panel
                                equals(window.panelShow, 1,
                                    "unchanged");
                                equals(window.panelUnhide, 1,
                                    "unchanged");
                                equals(window.panelBeforeDestroy, 0,
                                    "unchanged");
                                // attributes tab
                                equals(window.attributesShow, 1,
                                    "unchanged");
                                equals(window.attributesUnhide, 2,
                                    "triggered");
                                equals(window.attributesHide, 1,
                                    "unchanged");
                                // report tab
                                equals(window.reportShow, 1,
                                    "unchanged");
                                equals(window.reportUnhide, 1,
                                    "unchanged");
                                equals(window.reportHide, 1,
                                    "triggered");
                                equals(window.reportBeforeDestroy, 0,
                                    "unchanged");
                                // subtab1
                                equals(window.subtab1Show, 1,
                                    "unchanged");
                                equals(window.subtab1Unhide, 2,
                                    "unchanged");
                                equals(window.subtab1Hide, 2,
                                    "unchanged");
                                // subtab2
                                equals(window.subtab2Show, 1,
                                    "unchanged");
                                equals(window.subtab2Unhide, 2,
                                    "unchanged");
                                equals(window.subtab2Hide, 2,
                                    "triggered");
                                equals(window.subtab2BeforeDestroy, 0,
                                    "unchanged");

                                target.find('a:contains(Report)').click();
                                // panel
                                equals(window.panelShow, 1,
                                    "unchanged");
                                equals(window.panelUnhide, 1,
                                    "unchanged");
                                equals(window.panelBeforeDestroy, 0,
                                    "unchanged");
                                // attributes tab
                                equals(window.attributesShow, 1,
                                    "unchanged");
                                equals(window.attributesUnhide, 2,
                                    "unchanged");
                                equals(window.attributesHide, 2,
                                    "triggered");
                                // report tab
                                equals(window.reportShow, 1,
                                    "unchanged");
                                equals(window.reportUnhide, 2,
                                    "triggered");
                                equals(window.reportHide, 1,
                                    "unchanged");
                                equals(window.reportBeforeDestroy, 0,
                                    "unchanged");
                                // subtab1
                                equals(window.subtab1Show, 1,
                                    "unchanged");
                                equals(window.subtab1Unhide, 2,
                                    "unchanged");
                                equals(window.subtab1Hide, 2,
                                    "unchanged");
                                // subtab2
                                equals(window.subtab2Show, 1,
                                    "unchanged");
                                equals(window.subtab2Unhide, 3,
                                    "triggered");
                                equals(window.subtab2Hide, 2,
                                    "unchanged");
                                equals(window.subtab2BeforeDestroy, 0,
                                    "unchanged");
                                    
                                loader.destroy();
                                
                                // panel
                                equals(window.panelShow, 1,
                                    "unchanged");
                                equals(window.panelUnhide, 1,
                                    "unchanged");
                                equals(window.panelBeforeDestroy, 1,
                                    "triggered");
                                // attributes tab
                                equals(window.attributesShow, 1,
                                    "unchanged");
                                equals(window.attributesUnhide, 2,
                                    "unchanged");
                                equals(window.attributesHide, 2,
                                    "unchanged");
                                // report tab
                                equals(window.reportShow, 1,
                                    "unchanged");
                                equals(window.reportUnhide, 2,
                                    "unchanged");
                                equals(window.reportHide, 1,
                                    "unchanged");
                                equals(window.reportBeforeDestroy, 1,
                                    "triggered");
                                // subtab1
                                equals(window.subtab1Show, 1,
                                    "unchanged");
                                equals(window.subtab1Unhide, 2,
                                    "unchanged");
                                equals(window.subtab1Hide, 2,
                                    "unchanged");
                                // subtab2
                                equals(window.subtab2Show, 1,
                                    "unchanged");
                                equals(window.subtab2Unhide, 3,
                                    "unchanged");
                                equals(window.subtab2Hide, 2,
                                    "unchanged");
                                equals(window.subtab2BeforeDestroy, 1,
                                    "triggered");
                                
                                // panel
                                window.panelShow               = undefined;
                                window.panelUnhide             = undefined;
                                window.panelBeforeDestroy      = undefined;
                                // attributes tab
                                window.attributesShow          = undefined;
                                window.attributesUnhide        = undefined;
                                window.attributesHide          = undefined;
                                // report tab
                                window.reportShow              = undefined;
                                window.reportUnhide            = undefined;
                                window.reportHide              = undefined;
                                window.reportBeforeDestroy     = undefined;
                                // subtab1
                                window.subtab1Show             = undefined;
                                window.subtab1Unhide           = undefined;
                                window.subtab1Hide             = undefined;
                                // subtab2
                                window.subtab2Show             = undefined;
                                window.subtab2Unhide           = undefined;
                                window.subtab2Hide             = undefined;
                                window.subtab2BeforeDestroy    = undefined;

                                $('#target').remove();
                                start();
                            }, 100);
                        })                    
                        
                    }, 40);
                });                
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    
    // Verfiy tab syncing
    // ==================
    
    asyncTest('super combo callback test, sync Report->subtab1', function(){
        $('#target').remove();
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        
        // panel
        window.panelShow               = 0;
        window.panelUnhide             = 0;
        window.panelBeforeDestroy      = 0;
        // attributes tab
        window.attributesShow          = 0;
        window.attributesUnhide        = 0;
        window.attributesHide          = 0;
        // report tab
        window.reportShow              = 0;
        window.reportUnhide            = 0;
        window.reportHide              = 0;
        window.reportBeforeDestroy     = 0;
        // subtab1
        window.subtab1Show             = 0;
        window.subtab1Unhide           = 0;
        window.subtab1Hide             = 0;
        // subtab2
        window.subtab2Show             = 0;
        window.subtab2Unhide           = 0;
        window.subtab2Hide             = 0;
        window.subtab2BeforeDestroy    = 0;
    
        window.subtab1Content = false;
        window.subtab2Content = false;
        
    
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample11.html',
            target: target,
            activeTabs: ['Report', 'subtab1'],
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length > 0, 
                    'content appended to target and success handler called.');
                
                // initial state with synced tabs
                // panel
                equals(window.panelShow, 1,
                    "triggered");
                equals(window.panelUnhide, 1,
                    "triggered");
                equals(window.panelBeforeDestroy, 0,
                    "unchanged");
                // attributes tab
                equals(window.attributesShow, 0,
                    "unchanged");
                equals(window.attributesUnhide, 0,
                    "unchanged");
                equals(window.attributesHide, 0,
                    "unchanged");
                // report tab
                equals(window.reportShow, 1,
                    "triggered");
                equals(window.reportUnhide, 1,
                    "triggered");
                equals(window.reportHide, 0,
                    "unchanged");
                equals(window.reportBeforeDestroy, 0,
                    "unchanged");
                // subtab1
                equals(window.subtab1Show, 1,
                    "triggered");
                equals(window.subtab1Unhide, 1,
                    "triggered");
                equals(window.subtab1Hide, 0,
                    "unchanged");
                // subtab2
                equals(window.subtab2Show, 0,
                    "unchanged");
                equals(window.subtab2Unhide, 0,
                    "unchanged");
                equals(window.subtab2Hide, 0,
                    "unchanged");
                equals(window.subtab2BeforeDestroy, 0,
                    "unchanged");
                
                ok(window.subtab1Content && window.subtab1Content.length,
                    "event triggered only after content added to document");

                // change back to information tab
                target.find('a:contains(Information)').click();
                
                // panel
                equals(window.panelShow, 1,
                    "unchanged");
                equals(window.panelUnhide, 1,
                    "unchanged");
                equals(window.panelBeforeDestroy, 0,
                    "unchanged");
                // attributes tab
                equals(window.attributesShow, 1,
                    "triggered");
                equals(window.attributesUnhide, 1,
                    "triggered");
                equals(window.attributesHide, 0,
                    "unchanged");
                // report tab
                equals(window.reportShow, 1,
                    "unchanged");
                equals(window.reportUnhide, 1,
                    "unchanged");
                equals(window.reportHide, 1,
                    "triggered");
                equals(window.reportBeforeDestroy, 0,
                    "unchanged");
                // subtab1
                equals(window.subtab1Show, 1,
                    "unchanged");
                equals(window.subtab1Unhide, 1,
                    "unchanged");
                equals(window.subtab1Hide, 1,
                    "triggered");
                // subtab2
                equals(window.subtab2Show, 0,
                    "unchanged");
                equals(window.subtab2Unhide, 0,
                    "unchanged");
                equals(window.subtab2Hide, 0,
                    "unchanged");
                equals(window.subtab2BeforeDestroy, 0,
                    "unchanged");
                    
                // change back to report->subtab1
                target.find('a:contains(Report)').click();

                // panel
                equals(window.panelShow, 1,
                    "unchanged");
                equals(window.panelUnhide, 1,
                    "unchanged");
                equals(window.panelBeforeDestroy, 0,
                    "unchanged");
                // attributes tab
                equals(window.attributesShow, 1,
                    "unchanged");
                equals(window.attributesUnhide, 1,
                    "unchanged");
                equals(window.attributesHide, 1,
                    "triggered");
                // report tab
                equals(window.reportShow, 1,
                    "unchanged");
                equals(window.reportUnhide, 2,
                    "triggered");
                equals(window.reportHide, 1,
                    "unchanged");
                equals(window.reportBeforeDestroy, 0,
                    "unchanged");
                // subtab1
                equals(window.subtab1Show, 1,
                    "unchanged");
                equals(window.subtab1Unhide, 2,
                    "triggered");
                equals(window.subtab1Hide, 1,
                    "unchanged");
                // subtab2
                equals(window.subtab2Show, 0,
                    "unchanged");
                equals(window.subtab2Unhide, 0,
                    "unchanged");
                equals(window.subtab2Hide, 0,
                    "unchanged");
                equals(window.subtab2BeforeDestroy, 0,
                    "unchanged");

                // switch to subtab2
                target.find('a:contains(subtab2)').click();
                target.find('.tabs').bind('tabsload', function(){
                    target.find('.tabs').unbind('tabsload');
                    setTimeout(function(){
                        ok(true, 'changed to report tab->subtab2');

                        // panel
                        equals(window.panelShow, 1,
                            "unchanged");
                        equals(window.panelUnhide, 1,
                            "unchanged");
                        equals(window.panelBeforeDestroy, 0,
                            "unchanged");
                        // attributes tab
                        equals(window.attributesShow, 1,
                            "unchanged");
                        equals(window.attributesUnhide, 1,
                            "unchanged");
                        equals(window.attributesHide, 1,
                            "unchanged");
                        // report tab
                        equals(window.reportShow, 1,
                            "unchanged");
                        equals(window.reportUnhide, 2,
                            "unchanged");
                        equals(window.reportHide, 1,
                            "unchanged");
                        equals(window.reportBeforeDestroy, 0,
                            "unchanged");
                        // subtab1
                        equals(window.subtab1Show, 1,
                            "unchanged");
                        equals(window.subtab1Unhide, 2,
                            "unchanged");
                        equals(window.subtab1Hide, 2,
                            "triggered");
                        // subtab2
                        equals(window.subtab2Show, 1,
                            "triggered");
                        equals(window.subtab2Unhide, 1,
                            "triggered");
                        equals(window.subtab2Hide, 0,
                            "unchanged");
                        equals(window.subtab2BeforeDestroy, 0,
                            "unchanged");
                            
                        ok(window.subtab2Content && window.subtab2Content.length,
                            "event triggered only after content added to document");
                    
                        
                        loader.destroy();
                        // panel
                        equals(window.panelShow, 1,
                            "unchanged");
                        equals(window.panelUnhide, 1,
                            "unchanged");
                        equals(window.panelBeforeDestroy, 1,
                            "triggered");
                        // attributes tab
                        equals(window.attributesShow, 1,
                            "unchanged");
                        equals(window.attributesUnhide, 1,
                            "unchanged");
                        equals(window.attributesHide, 1,
                            "unchanged");
                        // report tab
                        equals(window.reportShow, 1,
                            "unchanged");
                        equals(window.reportUnhide, 2,
                            "unchanged");
                        equals(window.reportHide, 1,
                            "unchanged");
                        equals(window.reportBeforeDestroy, 1,
                            "triggered");
                        // subtab1
                        equals(window.subtab1Show, 1,
                            "unchanged");
                        equals(window.subtab1Unhide, 2,
                            "unchanged");
                        equals(window.subtab1Hide, 2,
                            "unchanged");
                        // subtab2
                        equals(window.subtab2Show, 1,
                            "unchanged");
                        equals(window.subtab2Unhide, 1,
                            "unchanged");
                        equals(window.subtab2Hide, 0,
                            "unchanged");
                        equals(window.subtab2BeforeDestroy, 1,
                            "triggered");

                        // cleanup
                        // panel
                        window.panelShow               = undefined;
                        window.panelUnhide             = undefined;
                        window.panelBeforeDestroy      = undefined;
                        // attributes tab
                        window.attributesShow          = undefined;
                        window.attributesUnhide        = undefined;
                        window.attributesHide          = undefined;
                        // report tab
                        window.reportShow              = undefined;
                        window.reportUnhide            = undefined;
                        window.reportHide              = undefined;
                        window.reportBeforeDestroy     = undefined;
                        // subtab1
                        window.subtab1Show             = undefined;
                        window.subtab1Unhide           = undefined;
                        window.subtab1Hide             = undefined;
                        // subtab2
                        window.subtab2Show             = undefined;
                        window.subtab2Unhide           = undefined;
                        window.subtab2Hide             = undefined;
                        window.subtab2BeforeDestroy    = undefined;

                        $('#target').remove();
                        start();
                        
                    }, 100);
                });    
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    asyncTest('super combo callback test, sync Report->subtab2', function(){
        $('#target').remove();
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        
        // panel
        window.panelShow               = 0;
        window.panelUnhide             = 0;
        window.panelBeforeDestroy      = 0;
        // attributes tab
        window.attributesShow          = 0;
        window.attributesUnhide        = 0;
        window.attributesHide          = 0;
        // report tab
        window.reportShow              = 0;
        window.reportUnhide            = 0;
        window.reportHide              = 0;
        window.reportBeforeDestroy     = 0;
        // subtab1
        window.subtab1Show             = 0;
        window.subtab1Unhide           = 0;
        window.subtab1Hide             = 0;
        // subtab2
        window.subtab2Show             = 0;
        window.subtab2Unhide           = 0;
        window.subtab2Hide             = 0;
        window.subtab2BeforeDestroy    = 0;
    
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/jsExample11.html',
            target: target,
            activeTabs: ['Report', 'subtab2'],
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length > 0, 
                    'content appended to target and success handler called.');
                
                // initial state with synced tabs
                // panel
                equals(window.panelShow, 1,
                    "triggered");
                equals(window.panelUnhide, 1,
                    "triggered");
                equals(window.panelBeforeDestroy, 0,
                    "unchanged");
                // attributes tab
                equals(window.attributesShow, 0,
                    "unchanged");
                equals(window.attributesUnhide, 0,
                    "unchanged");
                equals(window.attributesHide, 0,
                    "unchanged");
                // report tab
                equals(window.reportShow, 1,
                    "triggered");
                equals(window.reportUnhide, 1,
                    "triggered");
                equals(window.reportHide, 0,
                    "unchanged");
                equals(window.reportBeforeDestroy, 0,
                    "unchanged");
                // subtab1
                equals(window.subtab1Show, 0,
                    "unchanged");
                equals(window.subtab1Unhide, 0,
                    "unchanged");
                equals(window.subtab1Hide, 0,
                    "unchanged");
                // subtab2
                equals(window.subtab2Show, 1,
                    "triggered");
                equals(window.subtab2Unhide, 1,
                    "triggered");
                equals(window.subtab2Hide, 0,
                    "unchanged");
                equals(window.subtab2BeforeDestroy, 0,
                    "unchanged");
                
                ok(window.subtab2Content && window.subtab2Content.length,
                    "event triggered only after content added to document");
            

                // change to information tab
                target.find('a:contains(Information)').click();
                
                // panel
                equals(window.panelShow, 1,
                    "unchanged");
                equals(window.panelUnhide, 1,
                    "unchanged");
                equals(window.panelBeforeDestroy, 0,
                    "unchanged");
                // attributes tab
                equals(window.attributesShow, 1,
                    "triggered");
                equals(window.attributesUnhide, 1,
                    "triggered");
                equals(window.attributesHide, 0,
                    "unchanged");
                // report tab
                equals(window.reportShow, 1,
                    "unchanged");
                equals(window.reportUnhide, 1,
                    "unchanged");
                equals(window.reportHide, 1,
                    "triggered");
                equals(window.reportBeforeDestroy, 0,
                    "unchanged");
                // subtab1
                equals(window.subtab1Show, 0,
                    "unchanged");
                equals(window.subtab1Unhide, 0,
                    "unchanged");
                equals(window.subtab1Hide, 0,
                    "unchanged");
                // subtab2
                equals(window.subtab2Show, 1,
                    "unchanged");
                equals(window.subtab2Unhide, 1,
                    "unchanged");
                equals(window.subtab2Hide, 1,
                    "triggered");
                equals(window.subtab2BeforeDestroy, 0,
                    "unchanged");                 

                // change back to report->subtab2 tab
                target.find('a:contains(Report)').click();

                // panel
                equals(window.panelShow, 1,
                    "unchanged");
                equals(window.panelUnhide, 1,
                    "unchanged");
                equals(window.panelBeforeDestroy, 0,
                    "unchanged");
                // attributes tab
                equals(window.attributesShow, 1,
                    "unchanged");
                equals(window.attributesUnhide, 1,
                    "unchanged");
                equals(window.attributesHide, 1,
                    "triggered");
                // report tab
                equals(window.reportShow, 1,
                    "unchanged");
                equals(window.reportUnhide, 2,
                    "triggered");
                equals(window.reportHide, 1,
                    "unchanged");
                equals(window.reportBeforeDestroy, 0,
                    "unchanged");
                // subtab1
                equals(window.subtab1Show, 0,
                    "unchanged");
                equals(window.subtab1Unhide, 0,
                    "unchanged");
                equals(window.subtab1Hide, 0,
                    "unchanged");
                // subtab2
                equals(window.subtab2Show, 1,
                    "unchanged");
                equals(window.subtab2Unhide, 2,
                    "triggered");
                equals(window.subtab2Hide, 1,
                    "triggered");
                equals(window.subtab2BeforeDestroy, 0,
                    "unchanged");                 

                // change back to report->subtab1 tab
                target.find('a:contains(subtab1)').click();

                // panel
                equals(window.panelShow, 1,
                    "unchanged");
                equals(window.panelUnhide, 1,
                    "unchanged");
                equals(window.panelBeforeDestroy, 0,
                    "unchanged");
                // attributes tab
                equals(window.attributesShow, 1,
                    "unchanged");
                equals(window.attributesUnhide, 1,
                    "unchanged");
                equals(window.attributesHide, 1,
                    "unchanged");
                // report tab
                equals(window.reportShow, 1,
                    "unchanged");
                equals(window.reportUnhide, 2,
                    "unchanged");
                equals(window.reportHide, 1,
                    "unchanged");
                equals(window.reportBeforeDestroy, 0,
                    "unchanged");
                // subtab1
                equals(window.subtab1Show, 1,
                    "triggered");
                equals(window.subtab1Unhide, 1,
                    "triggered");
                equals(window.subtab1Hide, 0,
                    "unchanged");
                // subtab2
                equals(window.subtab2Show, 1,
                    "unchanged");
                equals(window.subtab2Unhide, 2,
                    "unchanged");
                equals(window.subtab2Hide, 2,
                    "triggered");
                equals(window.subtab2BeforeDestroy, 0,
                    "unchanged");                 

                    
                loader.destroy();
                // panel
                equals(window.panelShow, 1,
                    "unchanged");
                equals(window.panelUnhide, 1,
                    "unchanged");
                equals(window.panelBeforeDestroy, 1,
                    "triggered");
                // attributes tab
                equals(window.attributesShow, 1,
                    "unchanged");
                equals(window.attributesUnhide, 1,
                    "unchanged");
                equals(window.attributesHide, 1,
                    "unchanged");
                // report tab
                equals(window.reportShow, 1,
                    "unchanged");
                equals(window.reportUnhide, 2,
                    "unchanged");
                equals(window.reportHide, 1,
                    "unchanged");
                equals(window.reportBeforeDestroy, 1,
                    "triggered");
                // subtab1
                equals(window.subtab1Show, 1,
                    "unchanged");
                equals(window.subtab1Unhide, 1,
                    "unchanged");
                equals(window.subtab1Hide, 0,
                    "unchanged");
                // subtab2
                equals(window.subtab2Show, 1,
                    "unchanged");
                equals(window.subtab2Unhide, 2,
                    "unchanged");
                equals(window.subtab2Hide, 2,
                    "unchanged");
                equals(window.subtab2BeforeDestroy, 1,
                    "triggered");
                    
                // cleanup
                // panel
                window.panelShow               = undefined;
                window.panelUnhide             = undefined;
                window.panelBeforeDestroy      = undefined;
                // attributes tab
                window.attributesShow          = undefined;
                window.attributesUnhide        = undefined;
                window.attributesHide          = undefined;
                // report tab
                window.reportShow              = undefined;
                window.reportUnhide            = undefined;
                window.reportHide              = undefined;
                window.reportBeforeDestroy     = undefined;
                // subtab1
                window.subtab1Show             = undefined;
                window.subtab1Unhide           = undefined;
                window.subtab1Hide             = undefined;
                // subtab2
                window.subtab2Show             = undefined;
                window.subtab2Unhide           = undefined;
                window.subtab2Hide             = undefined;
                window.subtab2BeforeDestroy    = undefined;

                $('#target').remove();
                start();
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();
    });
    
    // Other options
    // =============
    
    asyncTest('behaviors option is executed', function(){
        window.behaviorsRan = false;
        var target = $('<div id="target"></div>');
        $(document.body).append(target);
        var loader = lingcod.contentLoader({
            url: '../media/common/js/test/layout/example1.html',
            target: target,
            behaviors: function(staging){
                if($(staging).length > 0){
                    window.behaviorsRan = true;
                }
            },
            success: function(){
                ok(true, 'content loaded.');
                ok(target.find('.panel').length === 1, 
                    'content appended to target and success handler called.');
                ok(window.behaviorsRan);
                $('#target').remove();
                start();
            },
            error: function(){
                ok(false, 'Could not load url.');
                $('#target').remove();
                start();
            }
        });
        loader.load();        
    });
    
    module('panel');
    
    if(!lingcod.options){
        lingcod.options = {};
    }
    
    test('initializes', function(){
        var panel = lingcod.panel({});
        ok(panel.getEl());
        panel.destroy();
    });
        
})();