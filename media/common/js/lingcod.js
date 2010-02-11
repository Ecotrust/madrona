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
        $(document).find('a.button').live('dragstart', function(){
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
        
        $('#datalayerstree').append('<div id="study_region"></div><div id="public_data"></div><div id="googlelayers"></div><div id="ecotrust_data"></div>');

        var studyRegion = lingcod.kmlTree({
            url: window.studyregion,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map'), 
            element: $('#study_region'),
            trans: options.media_url + 'common/images/transparent.gif',
            title: true,
            restoreState: true
        });
        if(!setCameraFromLocalStorage()){
            $(studyRegion).bind('kmlLoaded', function(){
                $('#study_region').find('li').dblclick();
            });            
        }
        studyRegion.load();

        var publicData = lingcod.kmlTree({
            url: window.public_data_layers,
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map'), 
            element: $('#public_data'),
            trans: options.media_url + 'common/images/transparent.gif',
            title: true,
            restoreState: true
        });
        publicData.load();

        var googleLayers = lingcod.kmlTree({
            url: options.media_url + 'common/fixtures/earthLayers.kml',
            ge: ge, 
            gex: gex, 
            animate: false, 
            map_div: $('#map'), 
            element: $('#googlelayers'),
            trans: options.media_url + 'common/images/transparent.gif',
            title: true,
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
                    case 'Grey 3d Buildings':
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
            var ecotrustData = lingcod.kmlTree({
                url: options.ecotrust,
                ge: ge, 
                gex: gex, 
                animate: false, 
                map_div: $('#map'), 
                element: $('#ecotrust_data'),
                trans: options.media_url + 'common/images/transparent.gif',
                title: true,
                restoreState: true
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
                $(editor.tree).bind('copyDone', function(e,location) {
                    this.refresh();
                    this.clearSelection();
                    var node = this.getNodesById(location);
                    if(node.length === 1) {
                        this.selectNode(node, this.lookup(node)); 
                    } else {
                        alert("No node found with Id " + location);
                    }
                });
                editors.push(editor);
            }
        }
        
        $('a.myshapes-link').live('click', function(e){
            e.preventDefault();
            $('.marinemap-panel:visible a.close').click();
            var href = $(this).attr('href');
            for(var i=0;i<editors.length;i++){
                var editor = editors[0];
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
                    var myshapesEditor = that.editors[0];
                    myshapesEditor.tree.refresh();
                    myshapesEditor.tree.clearSelection();
                    var node = myshapesEditor.tree.getNodesById(location);
                    if(node.length === 1) {
                        myshapesEditor.tree.selectNode(node); //, this.lookup(node));
                    } else {
                        alert("No node found with Id " + location);
                    }

                    // MP TODO switch to myshapes panel
                });
                editors.push(editor);
            }            
        }
        
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
            $(window).die('beforunload', unload);
        }
        
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
        });
        $('#sidebar').bind('mouseup', function(e){
            lingcod.menu_items.closeAll();
            // return false;
        });
        $('#sidebar-mask').click(function(){
            lingcod.menu_items.closeAll();
        });
        $('#panel-holder').click(function(e){
            if(e.originalTarget === this){
                lingcod.menu_items.closeAll();
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
    
    that.maskSidebar = function(){
        $('#panel-holder').show();
        $('#sidebar').addClass('masked');
    };
    
    that.unmaskSidebar = function(){
        $('#panel-holder').hide();
        $('#sidebar').removeClass('masked');
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
        panels.remove(panel);
        $(panel).unbind('panelshow', onPanelShown);
        $(panel).unbind('panelhide', onPanelHide);
        $(panel).unbind('panelclose', onPanelHide);
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
    
    var whenLoaded = function(selector, callback){
        var el = $(selector+':visible');
        if(el.length){
            callback(el);
        }else{
            setTimeout(whenLoaded, 100, selector, callback);
        }
    };
    
    that.whenLoaded = whenLoaded;
    
    return that;
})();