var lingcod = {
    
    isnamespace_:true,
    
    init: function(options){
        this.options = options;
        $('#sidebar').tabs();
        this.resize();
        var self = this;
        google.earth.createInstance(
            "map", 
            function(i){
                self.geInit(i);
            },
            function(code){
                self.geFailure(code);
            });
        this.setupListeners();
        lingcod.menu_items.init($('.menu_items'));
    },
    
    geInit: function(pluginInstance){
        ge = pluginInstance;
        ge.getWindow().setVisibility(true); // required
        gex = new GEarthExtensions(ge);
        
        this.googleLayers = new lingcod.map.googleLayers(ge, $('#ge_options'), $('#ge_layers'));
        this.geocoder = new lingcod.map.geocoder(gex, $('#flyToLocation'));
        this.measureTool = new lingcod.measureTool();
        this.drawTool = new lingcod.DrawTool(ge, gex);
        
        //part of mpa creation -- draw_panels and mpaCreator
        //will need to come up with a better solution for manipulator url
        this.draw_panels = { button_panel: 'mpa_draw_panel', results_panel: 'mpa_results_panel' };
        this.mpaCreator = new lingcod.MpaCreator(this.drawTool, this.draw_panels);
        
        var self = this;
        $('#measure_distance').click(function(){
            self.measureTool.clear();
            self.measureTool.measureDistance(gex, "distance");
        });
        $('#measure_area').click(function(){
            self.measureTool.clear();
            self.measureTool.measureArea(gex, "area");
        });
        $('#measure_clear').click(function(){
            self.measureTool.clear();
        });
        $('#measure_units').change(function(){
            self.measureTool.setUnits($(this).val());
        });
        $('#datalayerstree').kmlForest({ge: ge, gex: gex, div: $('#map')})
            .kmlForest('add', window.studyregion, {cachebust: true, callback: this.studyRegionLoaded})
            .kmlForest('add', window.public_data_layers, {cachebust: true});
        
        var panel = lingcod.panel();
        this.client = lingcod.rest.client(gex, panel);
        
        for(var i=0;i<options.myshapes.length; i++){
            lingcod.rest.kmlEditor({
                ge: ge,
                gex: gex,
                appendTo: '#myshapestree',
                div: '#map',
                url: options.myshapes[i],
                client: this.client
            });
        }
        var url = this.options.media_url + 'common/kml/shadow.kmz';
        google.earth.fetchKml(ge, url, function(k){
            ge.getFeatures().appendChild(k);
        });
    },
    
    studyRegionLoaded: function(kmlObject, node){
        // Reorder so studyRegion is on top of the list
        $('#datalayerstree').prepend(node);
        if (kmlObject.getAbstractView()){
            ge.getView().setAbstractView(kmlObject.getAbstractView());
        }
        
    },
    
    geFailure: function(errorCode){
        alert("Failure loading the Google Earth Plugin: " + errorCode);
    },
    
    setupListeners: function(){
        var self = this;
        $(window).resize(function(){
            self.resize();
        });
        $('#meta-navigation').click(function(){
            lingcod.menu_items.closeAll();
        });
        $('#sidebar').bind('tabsselect', function(){
            lingcod.menu_items.closeAll();
        });
        $('#sidebar-mask').click(function(){
            lingcod.menu_items.closeAll();
        });
    },
    
    resize: function(){
        var mh = $('#meta-navigation').outerHeight();
        var h = $(document.body).height() - mh;
        $('#sidebar').css({top: mh, height: h});
        
        // $('#panelManager').height(h);
        var w = $(document.body).width() - $('#sidebar').width();
        $('#map_container').height(h).width(w);
        
        // $('#layout').height($(window).height())
        // $('#panelManager').panelManager('resize');
        // var size = [$(window).width(), $(window).height()];
        // var top_height = $('#meta-navigation').height();
        // var body_height = size[1] - top_height - 7;
        // var map_width = size[0] - $('.sidebar-panel').panel('width') - 20;
        // $('#map_container').height(body_height - 10);
        // $('.sidebar-panel').panel('resize', {height: body_height -10});
        // // $('div.sidebar-panel').height(body_height - 10);
        // $('#map_container').width(map_width - 10);
    },
    
    maskSidebar: function(){
        $('#sidebar').addClass('masked');
    },
    
    unmaskSidebar: function(){
        $('#sidebar').removeClass('masked');
    }
};

