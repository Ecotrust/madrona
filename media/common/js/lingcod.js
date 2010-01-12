var lingcod = (function(){

    var options = {};
    var that = {};
    
    that.init = function(opts){
        options = opts;
        that.options = opts;
        
        $('#sidebar').tabs();
        resize();
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
    };

    var geInit = function(pluginInstance){
        ge = pluginInstance;
        ge.getWindow().setVisibility(true); // required
        gex = new GEarthExtensions(ge);
        
        that.googleLayers = new lingcod.map.googleLayers(ge, 
            $('#ge_options'), $('#ge_layers'));
        that.geocoder = new lingcod.map.geocoder(gex, $('#flyToLocation'));
        that.measureTool = new lingcod.measureTool();
        that.drawTool = new lingcod.DrawTool(ge, gex);
        
        //part of mpa creation -- draw_panels and mpaCreator
        //will need to come up with a better solution for manipulator url
        that.draw_panels = { button_panel: 'mpa_draw_panel', 
            results_panel: 'mpa_results_panel' };
        that.mpaCreator = new lingcod.MpaCreator(that.drawTool, 
            that.draw_panels);
        
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
        $('#datalayerstree').kmlForest({ge: ge, gex: gex, div: $('#map')})
            .kmlForest('add', window.studyregion, {cachebust: true, 
                callback: studyRegionLoaded})
            .kmlForest('add', window.ecotrust_data_layers, {cachebust: true})
            .kmlForest('add', window.public_data_layers, {cachebust: true});
        
        var panel = lingcod.panel({appendTo: $('#panel-holder'), 
            showCloseButton: false});
        that.client = lingcod.rest.client(gex, panel);
        if(typeof options.form_shown === 'function'){
            $(that.client).bind('form_shown', options.form_shown);
        }
        if(options.myshapes){
            for(var i=0;i<options.myshapes.length; i++){
                lingcod.rest.kmlEditor({
                    ge: ge,
                    gex: gex,
                    appendTo: '#myshapestree',
                    div: '#map',
                    url: options.myshapes[i],
                    client: that.client
                });
            }            
        }
        var url = that.options.media_url + 'common/kml/shadow.kmz';
        google.earth.fetchKml(ge, url, function(k){
            ge.getFeatures().appendChild(k);
        });
    };
    
    var studyRegionLoaded = function(kmlObject, node){
        // Reorder so studyRegion is on top of the list
        $('#datalayerstree').prepend(node);
        if (kmlObject.getAbstractView()){
            ge.getView().setAbstractView(kmlObject.getAbstractView());
        }   
    };
    
    var geFailure = function(errorCode){
        alert("Failure loading the Google Earth Plugin: " + errorCode);
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
            return false;
        });
        $('#sidebar-mask').click(function(){
            lingcod.menu_items.closeAll();
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
    
    var panels = [];
    
    that.addPanel = function(panel){
        // console.log('adding panel', panel);
        panels.push(panel);
        $(panel).bind('panelshow', onPanelShown);
        $(panel).bind('panelhide', onPanelHide);
        $(panel).bind('panelclose', onPanelHide);
        // console.log(this.panels);
    },
    
    that.removePanel = function(panel){
        // console.log('removing panel', panel)
        panels.remove(panel);
        $(panel).unbind('panelshow', onPanelShown);
        $(panel).unbind('panelhide', onPanelHide);
        $(panel).unbind('panelclose', onPanelHide);
        // console.log(this.panels);
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
        if(count > 0){
            // console.log('another panel still shown');
        }else{
            that.unmaskSidebar();
        }
    };

    return that;
})();