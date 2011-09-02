var lingcod = (function(){

    var options = {};
    var that = {};    
    var layers = [];
    
    var localAuthority = new URI(window.location.href).getAuthority();
    
    var constructor_defaults = {
        hideGoogleLayers: false,
        rememberMapExtent: true,
        displayEnhancedContent: false,
        srcWhitelist: [new RegExp('^http://' + localAuthority)],
        targetWhitelist: [new RegExp('^http://' + localAuthority)]
    };
    
    
    that.addLayer = function(url, opts){
        layers.push({url: url, opts: opts});
    };

    that.init = function(opts){
        options = jQuery.extend({}, constructor_defaults, opts);
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
        // just so that buttons act more like buttons
        $(document).find('#meta-navigation a, a.button, a.close, ' +
            '.menu_items span, .ui-tabs-nav a').live('dragstart', function(){
            return false;
        });
    };

    var geInit = function(pluginInstance){
        ge = pluginInstance;
        ge.getWindow().setVisibility(true); // required
        ge.getOptions().setStatusBarVisibility(true);
        gex = new GEarthExtensions(ge);
        
        that.geocoder = new lingcod.map.geocoder(gex, $('#flyToLocation'));
        that.measureTool = new lingcod.measureTool();
                
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
        
        var setEarthOptions = function(){
            $('#earthOptions li').each(function(){
                var li = $(this);
                switch(li.attr('id')){
                    case 'nav':
                        if(li.hasClass('visible')){
                            ge.getNavigationControl().setVisibility(
                                ge.VISIBILITY_AUTO);
                        }else{
                            ge.getNavigationControl().setVisibility(
                                ge.VISIBILITY_HIDE);
                        }
                        break;
                    case 'overview':
                        ge.getOptions().setOverviewMapVisibility(
                            li.hasClass('visible'));
                        break;
                    case 'scale':
                        ge.getOptions().setScaleLegendVisibility(
                            li.hasClass('visible'));
                        break;
                    case 'atm':
                        ge.getOptions().setAtmosphereVisibility(
                            li.hasClass('visible'));
                        break;
                    case 'terrain':
                        ge.getLayerRoot().enableLayerById(
                            ge.LAYER_TERRAIN, li.hasClass('visible'));
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
        
        var cameraSet = false;
        if(options.rememberMapExtent){
            cameraSet = setCameraFromLocalStorage();
        }
                
        for(var i=0; i<layers.length; i++){
            var div = $('<div id="datalayerstree'+i+'"></div>');
            $('#datalayerstree').append(div);
            layers[i].tree = kmltree({
                url: layers[i].url,
                gex: gex,
                mapElement: $('#map'),
                element: div,
                restoreState: !$.browser.msie,
                refreshWithState: false,
                displayEnhancedContent: options.displayEnhancedContent,
                setExtent: !cameraSet && layers[i].opts && 
                    layers[i].opts.setExtent
            });
            layers[i].tree.load();
            if(layers[i]['opts'] && layers[i]['opts'].showDownloadLink){
                $('#datalayerstree').append('<p class="download_layer"><a href="'+layers[i].url+'">Download this layer</a> for use in Google Earth or your own website.</p>');
            }
        }

        that.layers = layers;

        if(!that.options.hideGoogleLayers){
            var div = $('<div id="googlelayers"></div>');
            $('#datalayerstree').append(div);

            var googleLayers = kmltree({
                url: options.media_url + 'common/fixtures/earthLayers.kml',
                gex: gex, 
                mapElement: $('#map'), 
                element: div,
                restoreState: true,
                supportItemIcon: true
            });

            var updateGoogleLayers = function(tree){
                $('#googlelayers li').each(function(){
                    var item = $(this);
                    var name = item.find('span.name').text();
                    switch(name){
                        case 'Grid':
                            ge.getOptions().setGridVisibility(
                                item.hasClass('visible'));
                            break;
                        case '3d Buildings':
                            ge.getLayerRoot().enableLayerById(
                                ge.LAYER_BUILDINGS, item.hasClass('visible'));
                            break;
                        case 'Low Resolution 3d Buildings':
                            ge.getLayerRoot().enableLayerById(
                                ge.LAYER_BUILDINGS_LOW_RESOLUTION, 
                                item.hasClass('visible'));
                            break;
                        case 'Roads':
                            ge.getLayerRoot().enableLayerById(
                                ge.LAYER_ROADS, item.hasClass('visible'));
                            break;
                        case 'Borders and Labels':
                            ge.getLayerRoot().enableLayerById(
                                ge.LAYER_BORDERS, item.hasClass('visible'));
                            break;
                    }
                });
            }

            $(googleLayers).bind('kmlLoaded', function(){
                updateGoogleLayers(googleLayers);
                $(that).trigger('earthReady', [ge, gex]);
            });

            $(googleLayers).bind('toggleItem', function(){
                updateGoogleLayers(googleLayers);
            });

            googleLayers.load();
        } else {
            // No google layers, just trigger the event
            $(that).trigger('earthReady', [ge, gex]);
        }
                
        var panel = lingcod.panel({appendTo: $('#panel-holder'), 
            showCloseButton: false});
            
        setupSidebarLinkHandler(panel);
        
        var editors = [];
        
        if(options.myshapes){
            for(var i=0;i<options.myshapes.length; i++){
                var url = options.myshapes[i].url;
                var callback = options.myshapes[i]['callback'];
                var editor = lingcod.features.kmlEditor({
                    gex: gex,
                    appendTo: '#myshapestree',
                    url: options.myshapes[i].url,
                    enhancedContent: options.displayEnhancedContent,
                    panel: panel
                });
                if(callback){
                    $(editor).bind('kmlLoaded', function(event, e, kmlObject){
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
                var editor = lingcod.features.kmlEditor({
                    gex: gex,
                    appendTo: '#sharedshapestree',
                    url: options.sharedshapes[i],
                    enhancedContent: options.displayEnhancedContent,
                    panel: panel
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
                
        var onEditorEdit = function(e, data, status, xhr, context){
            // myshapes panel is the only one that needs refreshing
            var editor = editors[0];
            $('a[href=#MyShapes]').click();
            var info = typeof data === 'object' ? data:jQuery.parseJSON(data);
            var select = info['X-MarineMap-Select'];
            var show = info['X-MarineMap-Show'];
            var untoggle = info['X-MarineMap-UnToggle'];
            var hint = info['X-MarineMap-Parent-Hint'];
            // var select = xhr.getResponseHeader('X-MarineMap-Select');
            $(editor.tree).one('kmlLoaded', function(){
                if(select){
                    editor.tree.clearSelection();
                    select = select.split(' ');
                    var nodes = [];
                    for(var i = 0; i < select.length; i++){
                        var id = select[i];
                        var ns = editor.tree.getNodesById(id);
                        if(ns.length){
                            nodes.push(ns[0]);
                        }
                    }
                    if(nodes.length){
                        editor.tree.selectNodes($(nodes));                        
                    }else{
                        // only supports one hint for now. TODO? Not needed?
                        var nl = editor.tree.getNodesById(hint.split(' ')[0]);
                        if(nl.length){
                            $(editor.tree).one('networklinkload', function(){
                                var nodes = [];
                                for(var i = 0; i < select.length; i++){
                                    var id = select[i];
                                    var ns = editor.tree.getNodesById(id);
                                    if(ns.length){
                                        nodes.push(ns[0]);
                                    }
                                }
                                if(nodes.length){
                                    editor.tree.selectNodes($(nodes));                        
                                };
                            });
                            editor.tree.openNetworkLink(nl);
                        }
                    }
                }
                // Not sure why a timeout helps here, but otherwise the 
                // dblclick event wont trigger
                setTimeout(function(){
                    if(untoggle){
                        untoggle = untoggle.split(' ');
                        for(var i = 0; i < untoggle.length; i++){
                            var id = untoggle[i];
                            var ns = editor.tree.getNodesById(id);
                            $(ns[0]).find('> .toggler').click();
                        }
                    }
                    if(show){
                        var node = editor.tree.getNodesById(show);
                        if(node.length){
                            $(node).trigger('dblclick');
                        }
                    }
                }, 20);
            });
            editor.refresh();
        }
        
        for(var i=0;i<editors.length;i++){
            $(editors[i]).bind('select', onEditorSelect);
            $(editors[i]).bind('edit', onEditorEdit);
        };
        
        $('#sidebar, #meta-navigation').click(function(e){
            if(e.target === this || e.target === $('#MyShapes')[0]){
                for(var i=0;i<editors.length;i++){
                    editors[i].clearSelection();
                }
            }
        });
        
        // If news or about links aren't included in the interface these will
        // do nothing (good for extensible templates).
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

        $('#signin').click(function(e){
            opts = {};
            opts['load_msg'] = 'Loading Sign In Form';
            opts['showClose'] = true;
            panel.showUrl(that.options.signin_url, opts);
            e.preventDefault();
        });

        $('#profile').click(function(e){
            opts = {};
            opts['load_msg'] = 'Loading User Profile';
            opts['showClose'] = true;
            panel.showUrl(that.options.profile_url, opts);
            e.preventDefault();
        });

        $('#register').click(function(e){
            opts = {};
            opts['load_msg'] = 'Loading Registration Form';
            opts['showClose'] = true;
            panel.showUrl(that.options.registration_url, opts);
            e.preventDefault();
        });

        $('#help').click(function(e){
            opts = {};
            opts['load_msg'] = 'Loading Help Page';
            opts['showClose'] = true;
            panel.showUrl(that.options.help_url, opts);
            e.preventDefault();
        });

        // for showing the news or about panels if they haven't been viewed 
        // yet (that determination is done with cookies in the django view)
        if(options.show_panel){
            opts = {};
            opts['showClose'] = true;
            if(options.show_panel == 'about' && that.options.about_url){
                panel.showUrl(that.options.about_url, opts);
            }else if(options.show_panel == 'news' && that.options.news_url){
                panel.showUrl(that.options.news_url, opts);
            }else if(options.show_panel == 'signin' && that.options.signin_url){
                panel.showUrl(that.options.signin_url, opts);
            }
        }

        // A UI enhancement to add a drop-shadow from sidebar falling on map
        var url = that.options.media_url + 'common/kml/shadow.kmz';
        google.earth.fetchKml(ge, url, function(k){
            ge.getFeatures().appendChild(k);
        });
                
        $('#sidebar-toggler').click(function(){
            $('#map_container').css({
                'width': '100%', 
                'left': 0, 
                'z-index': 10
            });
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

        $('#create_bookmark').click( function() {
            var camera = ge.getView().copyAsCamera(ge.ALTITUDE_RELATIVE_TO_GROUND);
            var url = "/bookmark/tool/";
            // Get public layer state
            var tree = null;
            for(var i=0; i<lingcod.layers.length; i++){
                if(lingcod.layers[i].url.indexOf('public') != -1) {
                    tree = lingcod.layers[i].tree;
                    break;
                }
            }
            if (tree) { 
                var publicstate = JSON.stringify(tree.getState());
            } else {
                var publicstate = '{}';
            }
            // Get camera params
            var params = { 
                Latitude : camera.getLatitude(),
                Longitude : camera.getLongitude(),
                Altitude : camera.getAltitude(),
                Heading : camera.getHeading(),
                Tilt : camera.getTilt(),
                Roll : camera.getRoll(),
                AltitudeMode : camera.getAltitudeMode(),
                publicstate: publicstate
            };
            // Post the info and display the returned URL
            xhr = $.post( url, params,
                function( data, status, xhr ) {
                    $('#bookmark_url').text(data);
                }
            )
            .error(function(a,b,c) {
                $('#bookmark_url').html("We encountered an error while saving your bookmark:<br/>" + a.responseText + " <br/> " + c + " , " + a.status );
            })
            .complete(function() { 
                $('#bookmark_results').show();
                $('#bookmark_url').selText();
            });
        });
        
        window.onbeforeunload = function(){
            setCameraToLocalStorage();
            saveEarthOptionsToLocalStore();
            setStore('selectedTab', 
                $('#sidebar > ul > .ui-tabs-selected a').attr('href'));
        }
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
                $('#earthOptions').find('#'+key).toggleClass('visible', 
                    json[key]);
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
        
    that.persistentReports = {};

    var setupSidebarLinkHandler = function(panel){
        $('#map a[rel=sidebar]').live('click', function(e){
            var balloon = ge.getBalloon();
            if(balloon){
                var feature = balloon.getFeature();
                if(feature && 'getUrl' in feature){
                    var src = feature.getUrl();
                    if(src){
                        var target = $(this).attr('href');
                        if(safeURI(src, target)){
                            panel.showUrl(target, {
                                load_msg: $(this).attr('title')
                            });
                            e.preventDefault();
                        }
                    }
                }
            }
        });
    };
    
    var safeURI = function(src, target){
        var src = new URI(src);
        var target = new URI(target);
        var wuri = new URI(window.location.href);
        if(target.getAuthority() === null){
            target = target.resolve(wuri);
        }
        if(src.getAuthority() === null){
            src = src.resolve(wuri);
        }
        src = src.toString();
        target = target.toString();
        var safeSrc = false;
        for(var i = 0; i<options.srcWhitelist.length; i++){
            if(safeSrc === false){
                safeSrc = options.srcWhitelist[i].test(src);
            }
        }
        var safeTarget = false;
        for(var i = 0; i<options.targetWhitelist.length; i++){
            if(safeTarget === false){
                safeTarget = options.targetWhitelist[i].test(target);
            }
        }
        return (safeTarget && safeSrc);
    };

    return that;
})();
