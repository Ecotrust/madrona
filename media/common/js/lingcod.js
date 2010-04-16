var lingcod = (function(){

    var options = {};
    var that = {};
    
    that.init = function(opts){
        options = opts;
        that.options = opts;
        
        $('#sidebar').tabs({
            select: function(event, ui){
                if($(this).hasClass('masked')){
                    event.preventDefault();
                }
            }
        });
        
        var selectedTab = getStore('selectedTab');
        if(selectedTab){
            $('#sidebar').tabs('select', selectedTab);
        };
        
        
        resize();
        
        $('.marinemap-panel').live('click', function(){
            if(!$(this).hasClass('marinemap-menu-items')){
                lingcod.menu_items.closeAll();
            }
        });
        
        if(window.google){
            google.earth.createInstance(
                "map", 
                function(i){
                    geInit(i);
                },
                function(code){
                    geFailure(code);
                });
            setupListeners();
            lingcod.menu_items.init($('.menu_items'));
            // makes button clicking a lot more reliable!!
        }else{
            geFailure();
        }
        $(document).find('#meta-navigation a, a.button, a.close, .menu_items span, .ui-tabs-nav a').live('dragstart', function(){
            return false;
        });
    };

    var geInit = function(pluginInstance){
        ge = pluginInstance;
        ge.getWindow().setVisibility(true); // required
        ge.getOptions().setStatusBarVisibility(true);
        gex = new GEarthExtensions(ge);
        
        // that.googleLayers = new lingcod.map.googleLayers(ge, 
        //     $('#ge_options'), $('#ge_layers'));
        that.geocoder = new lingcod.map.geocoder(gex, $('#flyToLocation'));
        that.measureTool = new lingcod.measureTool();

        //alert(ge.getPluginVersion().toString());
                
        $('#measure_distance').click(function(){
            that.measureTool.clear();
            that.measureTool.measureDistance(gex, "measureAmount");
            $('#measure_clear').removeClass('disabled');
            $('#measureAmountHolder').show();
        });
        $('#measure_area').click(function(){
            that.measureTool.clear();
            that.measureTool.measureArea(gex, "measureAmount");
            $('#measure_clear').removeClass('disabled');
            $('#measureAmountHolder').show();
        });
        $('#measure_clear').click(function(){
            that.measureTool.clear();
            $(this).addClass('disabled');
            $('#measureAmountHolder').hide();
        });
        $('#measure_units').change(function(){
            that.measureTool.setUnits($(this).val());
        });
        
        $('#datalayerstree').append('<div id="study_region"></div><div id="ecotrust_data"></div><div id="user_data"></div><div id="public_data"></div><div id="googlelayers"></div>');

        var studyRegion = kmltree({
            url: window.studyregion,
            ge: ge, 
            gex: gex, 
            map_div: $('#map'), 
            element: $('#study_region'),
            restoreState: !$.browser.msie
        });
        if(!setCameraFromLocalStorage()){
            $(studyRegion).bind('kmlLoaded', function(){
                $('#study_region').find('li').dblclick();
            });            
        }
        studyRegion.load();

        var publicData = kmltree({
            url: window.public_data_layers,
            ge: ge, 
            gex: gex, 
            map_div: $('#map'), 
            element: $('#public_data'),
            restoreState: !$.browser.msie
        });
        publicData.load();

        var googleLayers = kmltree({
            url: options.media_url + 'common/fixtures/earthLayers.kml',
            ge: ge, 
            gex: gex, 
            map_div: $('#map'), 
            element: $('#googlelayers'),
            restoreState: true,
            supportItemIcon: true,
            fireEvents: function(){
                return true;
            }
        });
        
        var updateGoogleLayers = function(tree){
            $('#googlelayers li').each(function(){
                var item = $(this);
                var name = item.find('span.name').text();
                switch(name){
                    case 'Grid':
                        ge.getOptions().setGridVisibility(item.hasClass('visible'));
                        break;
                    case '3d Buildings':
                        ge.getLayerRoot().enableLayerById(ge.LAYER_BUILDINGS, item.hasClass('visible'));
                        break;
                    case 'Low Resolution 3d Buildings':
                        ge.getLayerRoot().enableLayerById(ge.LAYER_BUILDINGS_LOW_RESOLUTION, item.hasClass('visible'));
                        break;
                    case 'Roads':
                        ge.getLayerRoot().enableLayerById(ge.LAYER_ROADS, item.hasClass('visible'));
                        break;
                    case 'Borders and Labels':
                        ge.getLayerRoot().enableLayerById(ge.LAYER_BORDERS, item.hasClass('visible'));
                        break;
                }
            });
        }
        
        $(googleLayers).bind('kmlLoaded', function(){
            updateGoogleLayers(googleLayers);
        });
        
        $(googleLayers).bind('toggleItem', function(){
            updateGoogleLayers(googleLayers);
        });
        
        googleLayers.load();
                
        var panel = lingcod.panel({appendTo: $('#panel-holder'), 
            showCloseButton: false});
            
        that.client = lingcod.rest.client(gex, panel);
        
        if(typeof options.form_shown === 'function'){
            $(that.client).bind('form_shown', options.form_shown);
        }
        
        if(options.ecotrust){
            var ecotrustData = kmltree({
                url: options.ecotrust,
                ge: ge, 
                gex: gex, 
                map_div: $('#map'), 
                element: $('#ecotrust_data'),
                restoreState: !$.browser.msie
            });
            ecotrustData.load();
        }
        
        var editors = [];
        
        if(options.myshapes){
            for(var i=0;i<options.myshapes.length; i++){
                var url = options.myshapes[i].url;
                var callback = options.myshapes[i]['callback'];
                var editor = lingcod.rest.kmlEditor({
                    ge: ge,
                    gex: gex,
                    appendTo: '#myshapestree',
                    div: '#map',
                    url: options.myshapes[i].url,
                    client: that.client,
                    shared: false,
                    allow_copy: options.allow_copy
                });
                if(callback){
                    $(editor).bind('kmlLoaded', function(event, original_event, kmlObject){
                        callback(this, this.el, kmlObject)
                    });
                }
                editors.push(editor);
                $(editor.tree).bind('copyDone', function(e,location) {
                    var myshapesEditor = editors[0];
                    myshapesEditor.tree.clearSelection();
                    myshapesEditor.refresh( function() {
                        var node = myshapesEditor.tree.getNodesById(location);
                        if(node.length === 1) {
                            myshapesEditor.tree.selectNode(node); 
                        }
                    });
                });
            }
        }
        
        $('a.myshapes-link').live('click', function(e){
            e.preventDefault();
            $('.marinemap-panel:visible a.close').click();
            var href = $(this).attr('href');
            for(var i=0;i<editors.length;i++){
                var editor = editors[i];
                var nodes = editor.tree.getNodesById(href);
                if(nodes.length === 1){
                    editor.tree.selectNode(nodes);
                    nodes.trigger('dblclick');
                    return false;
                }
            }
            return false;
        });
        
        that.editors = editors;

        if(options.sharedshapes){
            for(var i=0;i<options.sharedshapes.length; i++){
                var editor = lingcod.rest.kmlEditor({
                    ge: ge,
                    gex: gex,
                    appendTo: '#sharedshapestree',
                    div: '#map',
                    url: options.sharedshapes[i],
                    client: that.client,
                    shared: true,
                    allow_copy: options.allow_copy
                });
                $(editor.tree).bind('copyDone', function(e, location) {
                    $('#sidebar').tabs('select', "#MyShapes");
                    var myshapesEditor = that.editors[0];
                    myshapesEditor.tree.clearSelection();
                    myshapesEditor.refresh( function() {
                        var node = myshapesEditor.tree.getNodesById(location);
                        if(node.length === 1) {
                            myshapesEditor.tree.selectNode(node); 
                        }
                    });
                });
                editors.push(editor);
            }            
        }
        
        var onEditorSelect = function(e, originalEvent, node, kmlObject){
            if(node){
                if(node.parents('#MyShapes').length !== 0){
                    $('#sidebar').tabs('select', '#MyShapes');
                }else{
                    $('#sidebar').tabs('select', '#SharedShapes');
                }
            }
        };
        
        for(var i=0;i<editors.length;i++){
            $(editors[i]).bind('select', onEditorSelect);
        };
        
        $('#sidebar, #meta-navigation').click(function(e){
            if(e.target === this || e.target === $('#MyShapes')[0]){
                for(var i=0;i<editors.length;i++){
                    editors[i].clearSelection();
                }
            }
        });
        
        $('#news').click(function(e){
            opts = {};
            opts['load_msg'] = 'Loading News';
            opts['showClose'] = true;
            panel.showUrl(that.options.news_url, opts);
            e.preventDefault();
        });

        $('#about').click(function(e){
            opts = {};
            opts['load_msg'] = 'Loading Intro';
            opts['showClose'] = true;
            panel.showUrl(that.options.about_url, opts);
            e.preventDefault();
        });

        if (options.show_panel){
            opts = {};
            opts['showClose'] = true;
            if (options.show_panel == 'about') {
                panel.showUrl(that.options.about_url, opts);
            } else if (options.show_panel == 'news') {
                panel.showUrl(that.options.news_url, opts);
            }
        }

        var url = that.options.media_url + 'common/kml/shadow.kmz';
        google.earth.fetchKml(ge, url, function(k){
            ge.getFeatures().appendChild(k);
        });
        
        var setEarthOptions = function(){
            $('#earthOptions li').each(function(){
                var li = $(this);
                switch(li.attr('id')){
                    case 'nav':
                        if(li.hasClass('visible')){
                            ge.getNavigationControl().setVisibility(ge.VISIBILITY_AUTO);
                        }else{
                            ge.getNavigationControl().setVisibility(ge.VISIBILITY_HIDE);
                        }
                        break;
                    case 'overview':
                        ge.getOptions().setOverviewMapVisibility(li.hasClass('visible'));
                        break;
                    case 'scale':
                        ge.getOptions().setScaleLegendVisibility(li.hasClass('visible'));
                        break;
                    case 'atm':
                        ge.getOptions().setAtmosphereVisibility(li.hasClass('visible'));
                        break;
                    case 'terrain':
                        ge.getLayerRoot().enableLayerById(ge.LAYER_TERRAIN, li.hasClass('visible'));
                        break;
                }
            });
        }
        
        $('#earthOptions li').click(function(e){
            $(this).toggleClass('visible');
            setEarthOptions();
        });
        
        setEarthOptionsFromLocalStore();
        setEarthOptions();
        
        var unload = function(){
            setCameraToLocalStorage();
            saveEarthOptionsToLocalStore();
            setStore('selectedTab', $('#sidebar > ul > .ui-tabs-selected a').attr('href'));
            // $(window).die('beforunload', unload);
        }
        
        $('#sidebar-toggler').click(function(){
            $('#map_container').css({'width': '100%', 'left': 0, 'z-index': 10});
            $('.menu_items').hide();
            $('#sidebar > .ui-tabs-nav').hide();
            $(this).hide();
            $('#show-sidebar').show();
        });
        
        $('#show-sidebar').click(function(){
            $(this).hide();
            $('#map_container').css({left: 500});
            $('.menu_items').show();
            $('#sidebar > .ui-tabs-nav').show();            
            $('#sidebar-toggler').show();
            resize();
        });
        
        $(window).bind('beforeunload', unload);
    };
    
    var studyRegionLoaded = function(kmlObject, node){
        // Reorder so studyRegion is on top of the list
        $('#datalayerstree').prepend(node);
        if (kmlObject.getAbstractView()){
            ge.getView().setAbstractView(kmlObject.getAbstractView());
        }   
    };
    
    var setStore = function(key, value){
        if(!!window.localStorage){
            localStorage.setItem(key, value);
        }
    };
    
    var getStore = function(key){
        if(!!window.localStorage){
            return localStorage.getItem(key);
        }else{
            return false;
        }
    }
    
    var setEarthOptionsFromLocalStore = function(){
        if(!!window.localStorage && localStorage.getItem('earthOptions')){
            var json = JSON.parse(localStorage.getItem('earthOptions'));
            for(key in json){
                $('#earthOptions').find('#'+key).toggleClass('visible', json[key]);
            }
        }else{
            return false;
        }
    };
    
    var saveEarthOptionsToLocalStore = function(){
        if(!!window.localStorage){
            var json = {};
            $('#earthOptions li').each(function(){
                json[$(this).attr('id')] = $(this).hasClass('visible');
            });
            localStorage.setItem('earthOptions', JSON.stringify(json));
        }
    };
    
    var geFailure = function(errorCode){
        // alert("Failure loading the Google Earth Plugin: " + errorCode);
    }
    
    var setupListeners = function(){
        $(window).smartresize(function(){
            resize();
        });
        $('#meta-navigation').click(function(){
            lingcod.menu_items.closeAll();
            $('#panel-holder').find('a.close:visible').click();
        });
        $('#sidebar').bind('mouseup', function(e){
            lingcod.menu_items.closeAll();
            // return false;
        });
        $('#sidebar-mask').click(function(){
            lingcod.menu_items.closeAll();
        });
        $('#sidebar > .ui-tabs-nav li a').click(function(){
            $('#panel-holder').find('a.close:visible').click();
        });
        
        $('#panel-holder').click(function(e){
            if(e.originalTarget === this){
                lingcod.menu_items.closeAll();
                $('#panel-holder').find('a.close:visible').click();
            }
        });
    };
    
    var resize = function(){
        var mh = $('#meta-navigation').outerHeight();
        var h = $(document.body).height() - mh;
        $('#sidebar').css({top: mh, height: h});
        $('#panel-holder').css({top: mh, height: h});
        
        var w = $(document.body).width() - $('#sidebar').width();
        $('#map_container').height(h).width(w);
    };
    
    that.resize = resize;
    
    that.maskSidebar = function(){
        $('#panel-holder').show();
        $('#sidebar').addClass('masked');
    };
    
    that.unmaskSidebar = function(){
        if($('#panel-holder').find('.marinemap-panel:visible').length === 0){
            $('#panel-holder').hide();
            $('#sidebar').removeClass('masked');
        }
    };
    
    that.showLoadingMask = function(msg){
        var msg = msg || 'Loading';
        var lmsg = $('#sidebar-mask').find('span.loadingMsg');
        lmsg.text(msg);
        lmsg.show();
        lingcod.menu_items.disable();
        $('#sidebar').addClass('masked');
    };
    
    that.hideLoadingMask = function(){
        $('#sidebar-mask').find('span.loadingMsg').hide();
        lingcod.menu_items.enable();
        that.unmaskSidebar();
    }
    
    var panels = [];
    
    that.addPanel = function(panel){
        panels.push(panel);
        $(panel).bind('panelshow', onPanelShown);
        $(panel).bind('panelhide', onPanelHide);
        $(panel).bind('panelclose', onPanelHide);
    },
    
    that.removePanel = function(panel){
        // hmmm, I hope removing this doesn't cause any problems
        // if(panels){
        //     panels.remove(panel);
        // }
        // $(panel).unbind('panelshow', onPanelShown);
        // $(panel).unbind('panelhide', onPanelHide);
        // $(panel).unbind('panelclose', onPanelHide);
    };
    
    var onPanelShown = function(e, panel){
        that.maskSidebar();
    };
    
    var onPanelHide = function(e, panel){
        var count = 0;
        for(var i=0; i<panels.length; i++){
            var p = panels[i];
            if(p.shown){
                count++;
            }
        }
        if(count <= 0){
            that.unmaskSidebar();
        }
    };
    
    var setCameraToLocalStorage = function(){
        if(!!window.localStorage){
            localStorage.setItem('marinemap-camera', gex.view.serialize());
        }
    };
    
    var setCameraFromLocalStorage = function(){
        if(!!window.localStorage && localStorage.getItem('marinemap-camera')){
            gex.view.deserialize(localStorage.getItem('marinemap-camera'));
            return true;
        }
        return false;
    };
    
    var whenLoaded = function(selector, callback, count){
        if(!count){
            count = 1;
        }else{
            count = count + 1;
            if(count > 20){
                return;
            }
        }
        var el = $(selector+':visible');
        if(el.length){
            callback(el);
        }else{
            setTimeout(whenLoaded, 100, selector, callback, count);
        }
    };
    
    // Use this function within content that goes into panels in order to
    // specify javascript to be executed when the panel is shown, closed, 
    // and/or hidden.
    // 
    // For example, this content could be rendered in a django view:
    // 
    // <div id="foo"></div>
    // <script type="text/javascript" charset="utf-8">
    //     lingcod.panelEvents({
    //         show: function(){
    //             // I'll execute when the panel is shown
    //             $('#foo').html('panel shown and callback executed.');
    //         },
    //         hide: function(){
    //             $('#foo').html("I'm just temporarily hidden.");
    //         },
    //         close: function(){
    //             alert('you closed the panel!');
    //         }
    //     });
    // </script>
    // 
    // This is particularly useful for content shown via panel.showUrl()
    // 
    // Note that any javascript not specified using panelEvents() will be 
    // executed immediately, likely with unexpected consequences.
    var panelEvents = function(opts){
        whenLoaded('.marinemap-panel', function(el){
            if(opts.show){
                opts.show(el);
            }
            if(opts.close){
                var panel = el.data('panelComponent');
                var cback = function(){
                    $(this).unbind('panelclose', cback);
                    opts.close(el);
                };
                $(panel).bind('panelclose', cback);
            }
            if(opts.hide){
                var panel = el.data('panelComponent');
                var cback = function(){
                    $(this).unbind('panelhide', cback);
                    opts.hide(el);
                };
                $(panel).bind('panelhide', cback);                
            }
        });
    };
    
    that.panelEvents = panelEvents;
        
    that.persistentReports = {};
    
    return that;
})();
