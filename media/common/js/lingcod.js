var lingcod = {
    
    isnamespace_:true,
    
    init: function(){
        $('#panelManager').panelManager({top: '1em', left: 0});
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
    },
    
    geInit: function(pluginInstance){
        ge = pluginInstance;
        ge.getWindow().setVisibility(true); // required
        gex = new GEarthExtensions(ge);
        // gex.util.lookAt([33, -118], { range: 800000, tilt: 40 });
        
        // set Earth lookat from study region
        $.get('/studyregion/lookAtKml/', 
            function(data) {
                var kmlObject = ge.parseKml(data);
                if (kmlObject) {
                    if (kmlObject.getAbstractView())
                        ge.getView().setAbstractView(kmlObject.getAbstractView());
                }
            });
            
        // show study region kml
        $.get('/studyregion/kml/', function(data) { //?n=34&s=32&e=-117&w=-117.5
            gex.util.displayKmlString( data );
        });
        
        this.googleLayers = new lingcod.map.googleLayers(ge, window.ge_options, window.ge_layers);
        this.geocoder = new lingcod.map.geocoder(gex, $('#flyToLocation'));
        this.measureTool = new lingcod.measureTool();
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
        $('#datalayerstree').kmlForest({ge: ge, gex: gex})
            .kmlForest('add', 'http://marinemap.org/kml_test/Public%20Data%20Layers.kmz');
    },
    
    geFailure: function(errorCode){
        alert("Failure loading the Google Earth Plugin: " + errorCode);
    },
    
    setupListeners: function(){
        var self = this;
        $(window).resize(function(){
            self.resize();
        });
        
        // $(document.options).find('input').click(lingcod.map.ge_options.updateOptions);
        // $(document.ge_layers).find('input').click(lingcod.map.ge_options.updateLayer);
    },
    
    resize: function(){
        $('#panelManager').panelManager('resize');
        var size = [$(window).width(), $(window).height()]
        var top_height = $('#meta-navigation').height();
        var body_height = size[1] - top_height - 7;
        var map_width = size[0] - $('.sidebar-panel').panel('width') - 20;
        $('#map_container').height(body_height - 10);
        $('.sidebar-panel').panel('resize', {height: body_height -10});
        // $('div.sidebar-panel').height(body_height - 10);
        $('#map_container').width(map_width - 10);
    }
};
