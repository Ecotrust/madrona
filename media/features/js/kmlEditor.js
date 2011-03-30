// Provides an editable instance of kmltree whose behavior is driven by the 
// contents of a workspace document linked to within the target kml file
lingcod.features.kmlEditor = (function(){
    
    // Static Methods
    // ##############
    
    function checkOptions(opts){
        if(!opts || !opts.url || !opts.appendTo || !opts.gex){
            throw('kmlEditor needs url, appendTo, and gex options');
        }
        return opts;
    }

    
    // Constructor
    return function(options){
        
        options = checkOptions(options);
        
        // public api
        var that = {};
        
        // public vars
        that.workspace;
        that.tree;
        that.el;
        
        // private vars
        var tbar;
        var create_menu;
        var tree;
        var kmlEl;
        
        // Create html skeleton for the editor, toolbar menu, and tree
        that.el = $([
            '<div class="kmlEditor">',
                '<h1 class="name"></h1>',
                '<div class="toolbar"></div>',
                '<div class="kmllist"></div>',
            '</div>'
        ].join(''));
        
        kmlEl = that.el.find('.kmllist');
        
        // Setup toolbar as much as possible before workspace is loaded
        var tbar = new goog.ui.Toolbar();
        var create_menu = new goog.ui.Menu();
        
        tbar.render(that.el.find('.toolbar')[0]);

        var tree = kmltree({
            url: options.url,
            gex: options.gex, 
            mapElement: $('#map'), 
            element: kmlEl,
            bustCache: true,
            restoreState: true,
            supportItemIcon: true
        });        
        
        that.tree = tree;
        
        $(options.appendTo).append(that.el);

        function renderToolbar(workspace){
            
        }
        
        function onKmlLoad(){
            
        }
                
        return that;
    }
})();