lingcod.kmlTree = (function(){

    var template = tmpl([
        '<li class="',
        '<%= listItemType %> ',
        '<%= type %> ',
        '<%= (visible ? "visible " : "") %>',
        '<%= (customIcon ? "hasIcon " : "") %>',
        '<%= (fireEvents ? "fireEvents " : "") %>',
        '<%= (select ? "select " : "") %>',
        '<%= (open ? "open " : "") %>',
        '<%= (description ? "hasDescription " : "") %>',
        '<%= (snippet ? "hasSnippet " : "") %>',
        'marinemap-kmltree-id-<%= id %> marinemap-kmltree-item',
        '">',
            '<span class="kmlId"><%= kmlId %></span>',
            '<span class="nlDocId"></span>',
            '<span class="expander"><img width="16" height="16" src="<%= trans %>" /></span>',
            '<span class="toggler"><img width="16" height="16" src="<%= trans %>" /></span>',
            '<span class="icon"><img width="16" height="16" src="<%= trans %>" /></span>',
            '<span class="name"><%= name %></span>',
            '<% if(snippet){ %>',
                '<p class="snippet"><%= snippet %></p>',
            '<% } %>',
            '<% if(children.length) { %>',
            '<ul><%= renderOptions(children) %></ul>',
            '<% } %>',
        '</li>'
    ].join(''));
    
    var constructor_defaults = {
        enableSelection: function(){return false;},
        fireEvents: function(){return false;},
        openNetworkLinks: true,
        historyCookie: true,
        showTitle: true
    };
        
    // For some reason GEAPI can't switch between features when opening new
    // balloons accurately. Have to clear the old popup and add a timeout to
    // make sure the balloon A is closed before balloon b is opened.
    var openBalloon = function(kmlObject, plugin){
        var a = plugin.getBalloon();
        if(a){
            // there is already a balloon(a) open
            var f = a.getFeature();
            if(f !== kmlObject){
                // not trying to re-open the same balloon
                plugin.setBalloon(null);
                // try this function again in 50ms
                setTimeout(openBalloon, 50, kmlObject, plugin);
            }
        }else{
            // if balloon A closed or never existed, create & open balloon B
            kmlObject.setVisibility(true);
            var b = plugin.createFeatureBalloon('');
            b.setFeature(kmlObject);
            plugin.setBalloon(b);
        }
    };
    
    return function(opts){
        var that = {};
        var lookupTable = {};
        that.kmlObject = null;
        var docs = {};
        
        var opts = jQuery.extend({}, constructor_defaults, opts);
        var ge = opts.gex.pluginInstance;
        
        if(!opts.url || !opts.gex || !opts.element || !opts.trans){
            throw('kmlTree must be called with options url, gex, trans & element');
            return false;
        }
        
        var load = function(cachebust){
            if(that.kmlObject){
                throw('KML already loaded');
            }
            var url = opts.url;
            // can be removed when the following ticket is resolved:
            // http://code.google.com/p/earth-api-samples/issues/detail?id=290&q=label%3AType-Defect&sort=-stars%20-status&colspec=ID%20Type%20Summary%20Component%20OpSys%20Browser%20Status%20Stars
            if(!url.match('http')){
                url = window.location.protocol + "//" + window.location.host + "/" + url;
                url = url.replace(/(\w)\/\//g, '$1/');
            }
            if(cachebust){
                url = url + '?' + (new Date()).valueOf();
            }
            google.earth.fetchKml(ge, url, function(kmlObject){
                processKmlObject(kmlObject, url);
            });
        };
        
        that.load = load;
        
        // returns all nodes that represent a kmlObject with a matching ID
        var getNodesById = function(id){
            if(id){
                id = id.replace(/\//g, '-');
                return opts.element.find('.marinemap-kmltree-id-'+id);
            }
        };
        
        that.getNodesById = getNodesById;
                
        // Selects the first node found matching the ID
        var selectById = function(id){
            var node = getNodesById(id)[0];
            return selectNode(node, lookup(node));
        };
        
        that.selectById = selectById;
        
        var clearSelection = function(keepBalloons){
            var prev = opts.element.find('.selected').removeClass('selected');
            if(prev.length){
                $(that).trigger('select', [null, null]);                
            }
            var balloon = ge.getBalloon();
            if(balloon && !keepBalloons){
                ge.setBalloon(null);
            }
        }
        
        that.clearSelection = clearSelection;
        
        var processKmlObject = function(kmlObject, url){
            if (!kmlObject) {
                // show error
                setTimeout(function() {
                    alert('Error loading KML - '+url);
                },
                0);
                return;
            }
            that.kmlObject = kmlObject;
            that.kmlObject.setVisibility(true);
            var options = buildOptions(kmlObject);
            
            
            var rendered = renderOptions(options.children[0].children);
            var content = '<div class="marinemap-kmltree">';
            if(opts.title){
                content += '<h4 class="marinemap-kmltree-title">'+options.children[0].name+'</h4>';
            }
            opts.element.html(content + '<ul class="marinemap-kmltree">' + rendered +'</ul></div>');
            ge.getFeatures().appendChild(kmlObject);
            $(that).trigger('kmlLoaded', kmlObject);
        };
        
        var buildOptions = function(kmlObject){
            var docid = addDocLookup(kmlObject);
            var topTreeNode;
            var options = {name: kmlObject.getName()};
            opts.gex.dom.walk({
                visitCallback: function(context){
                    var parent = context.current;
                    if(!parent.children){
                        parent.children = [];
                    }
                    var lookupId = addLookup(docid, this);
                    var child = {
                        renderOptions: renderOptions,
                        name: this.getName(),
                        visible: !!this.getVisibility(),
                        type: this.getType(),
                        open: this.getOpen() && this.getType() !== 'KmlNetworkLink',
                        id: this.getId().replace(/\//g, '-'),
                        description: this.getDescription(),
                        snippet: this.getSnippet(),
                        select: opts.enableSelection(this),
                        fireEvents: opts.fireEvents(this),
                        listItemType: getListItemType(this),
                        customIcon: false,
                        children: [],
                        kmlId: lookupId,
                        trans: opts.trans
                    }
                    parent.children.push(child);
                    if(child.listItemType !== 'checkHideChildren'){
                        context.child = child;
                    }
                },
                rootObject: kmlObject,
                rootContext: options
            });
            return options;
        };
        
        // See http://code.google.com/apis/kml/documentation/kmlreference.html#listItemType
        var getListItemType = function(kmlObject){
            var listItemType = 'check';
            var selector = kmlObject.getStyleSelector();
            if(selector && selector.getType() === 'KmlStyle'){
                var lstyle = selector.getListStyle();
                if(lstyle){
                    var ltype = lstyle.getListItemType();
                    switch(ltype){
                        case 0:
                            // 'check'
                            break;
                        case 5:
                            listItemType = 'radioFolder';
                            break;
                        case 2:
                            listItemType = 'checkOffOnly';
                            break;
                        case 3:
                            listItemType = 'checkHideChildren';
                            break;
                    }
                }
            }
            return listItemType;
        };
        
        var renderOptions = function(options){
            if(jQuery.isArray(options)){
                var strings = [];
                for(var i=0;i<options.length;i++){
                    strings.push(_render(options[i]));
                }
                return strings.join('');
            }else{
                var string = _render(options);
                return string;
            }
        };
                
        var defaults = {
            renderOptions: renderOptions
        };

        var _render = function(options){
            var s = template(jQuery.extend({}, defaults, options));
            return s;
        };
        
        var clearLookups = function(){
            // try to clear some memory
            lookupTable = null;
            lookupTable = {};
        };
        
        var refresh = function(){
            clearLookups();
            clearKmlObjects();
            clearNetworkLinks();
            opts.element.html('');
            ge.setBalloon(null);
            load(true);
        };

        that.refresh = refresh;
        
        // Deletes references to networklink kmlObjects, removes them from the
        // dom. Prepares for refresh or tree destruction.
        var clearNetworkLinks = function(){
            for(var key in docs){
                opts.gex.dom.removeObject(docs[key]);
                // docs[key].release();
            }
            docs = {};
        };
        
        var clearKmlObjects = function(){
            clearNetworkLinks();
            if(that.kmlObject && that.kmlObject.getParentNode()){
                opts.gex.dom.removeObject(that.kmlObject);
                // that.kmlObject.release();
            }
            that.kmlObject = null;
        };
        
        var destroy = function(){
            clearLookups();
            clearKmlObjects();
            opts.element.find('li > span.name').die();
            opts.element.find('li').die();
            opts.element.find('li > span.expander').die();
            opts.element.html('');
            $(that).unbind();
        };
        
        that.destroy = destroy;
        
        var lookup = function(li){
            var li = $(li);
            if(li.length && li.find('> .kmlId').length){
                var ids = $($(li)[0]).find('> .kmlId').text().split('-');
                var docId = ids[0];
                var id = parseInt(ids[1]);
                return lookupTable[docId][id];    
            }else{
                return false;
            }
        }
        
        that.lookup = lookup;
        
        var addLookup = function(docid, value){
            lookupTable[docid].push(value);
            return docid + '-' + (lookupTable[docid].length - 1);
        };
        
        var lookupDoc = function(li){
            var li = $(li);
            if(li.length && li.find('> .kmlId').length){
                var id = $($(li)[0]).find('> .kmlId').text().split('-')[0];
                return docs[id];
            }else{
                return false;
            }
        };
        
        var lookupNlDoc = function(li){
            var li = $(li);
            if(li.length && li.find('> .nlDocId').length){
                return docs[li.find('> .nlDocId').text()];
            }else{
                return false;
            }
        }
        
        var addDocLookup = function(kmlObject){
            var docid = kmlObject.getName() + (new Date()).getTime();
            if(lookupTable[docid]){
                throw('document already added to lookup');
            }
            docs[docid] = kmlObject;
            lookupTable[docid] = [];
            return docid;
        };
                
        var selectNode = function(node, kmlObject){
            node = $(node);
            clearSelection(true);
            node.addClass('selected');
            toggleVisibility(node, true);
            node.addClass('selected');
            openBalloon(kmlObject, ge);
            var parent = node.parent().parent();
            while(!parent.hasClass('marinemap-kmltree') && !parent.find('>ul:visible').length){
                parent.addClass('open');
                var parent = parent.parent().parent();
            }
            $(that).trigger('select', [node, kmlObject]);
        };
        
        that.selectNode = selectNode;
        
        
        opts.element.find('li > span.name').live('click', function(){
            var node = $(this).parent();
            var kmlObject = lookup(node);
            if(node.hasClass('select')){
                selectNode(node, kmlObject);
            }else{
                clearSelection();
                if(node.hasClass('hasDescription')){
                    toggleVisibility(node, true);
                    openBalloon(kmlObject, ge);
                }                
            }
            if(node.hasClass('fireEvents')){
                $(that).trigger('click', [node[0], kmlObject]);
            }
        });
            
        opts.element.find('li.fireEvents > span.name').live('contextmenu', function(){
            var parent = $(this).parent();
            var kmlObject = lookup(parent);
            if(parent.hasClass('fireEvents')){
                $(that).trigger('contextmenu', [parent[0], kmlObject]);
            }
        });
        
        // Events to handle clearing selection
        
        opts.element.click(function(e){
            if(e.target === this){
                clearSelection();
            }else{
                if($(e.target).hasClass('toggle') && !$(e.target).hasClass('select')){
                    clearSelection();
                }
            }
        });
        
        var toggleDown = function(node, toggling){
            if(toggling){
                if(node.hasClass('checkOffOnly')){
                    return;
                }else{
                    if(node.hasClass('radioFolder')){
                        if(node.find('>ul>li.visible').length){
                            // one node already turned on, do nothing
                            return;
                        }else{
                            var children = node.find('>ul>li');
                            if(children.length){
                                toggleItem(children[0], true);
                                toggleDown($(children[0]));
                            }else{
                                return;
                            }
                        }
                    }else{
                        node.find('>ul>li').each(function(){
                            var n = $(this);
                            if(!n.hasClass('checkOffOnly')){
                                toggleItem(n, true);
                                toggleDown(n, true);
                            }
                        });
                    }
                }
            }else{
                node.find('li').each(function(){
                    toggleItem(this, false);
                });
            }
        };
        
        var toggleUp = function(node, toggling){
            var parent = node.parent().parent();
            if(!parent.hasClass('marinemap-kmltree')){
                if(toggling){
                    var herParent = parent.parent().parent();
                    if(herParent.hasClass('radioFolder')){
                        // toggle off any siblings and toggle them down
                        herParent.find('>ul>li.visible').each(function(){
                            var sib = $(this);
                            toggleItem(sib, false);
                            toggleDown(sib, false);
                        });
                    }
                    if(!parent.hasClass('visible')){
                        toggleItem(parent, true);
                        toggleUp(parent, true);                        
                    }
                }else{
                    if(parent.find('>ul>li.visible').length === 0){
                        toggleItem(parent, false);
                        toggleUp(parent, false);
                    }
                }
            }
        };
        
        var toggleVisibility = function(node, toggle){
            if(node.hasClass('checkOffOnly') && toggle){
                return;
            }
            var parent = node.parent().parent();
            if(parent.hasClass('radioFolder')){
                parent.find('>ul>li.visible').each(function(){
                    toggleItem(this, false);
                });
            }
            toggleItem(node, toggle);
            toggleDown(node, toggle);
            toggleUp(node, toggle);
        };
        
        var toggleItem = function(node, toggling){
            lookup(node).setVisibility(toggling);
            $(node).toggleClass('visible', toggling);
            if($(node).hasClass('KmlNetworkLink') && $(node).hasClass('loaded')){
                var doc = lookupNlDoc(node);
                doc.setVisibility(toggling);
            }
        };
        
        var getDocId = function(kmlObject){
            for(var key in docs){
                if(docs[key] === kmlObject){
                    return key;
                }
            }
            throw('could not getDocId');
        }
        
        var openNetworkLink = function(node){
            if(node.find('> ul').length){
                throw('networklink already loaded');
            }else{
                var NetworkLink = lookup(node);
                var link = NetworkLink.getLink().getHref();
                node.addClass('loading');
                google.earth.fetchKml(ge, link, function(kmlObject){
                    if(!kmlObject){
                        alert('Error loading ' + link);
                        node.addClass('error');
                        node.addClass('checkHideChildren');
                        return;
                    }
                    ge.getFeatures().appendChild(kmlObject);
                    kmlObject.setVisibility(NetworkLink.getVisibility());
                    var parent = NetworkLink.getParentNode();
                    parent.getFeatures().removeChild(NetworkLink);
                    var data = buildOptions(kmlObject);
                    var html = renderOptions(data.children[0].children);
                    node.append('<ul>'+html+'</ul>');
                    node.addClass('open');
                    node.removeClass('loading');
                    node.addClass('loaded');
                    node.find('.nlDocId').text(getDocId(kmlObject));
                    $(that).trigger('networklinkload', [node, kmlObject]);
                });
            }
        };
        
        
        // expand events
        opts.element.find('li > span.expander').live('click', function(){
            var el = $(this).parent();
            if(el.hasClass('KmlNetworkLink') && !el.hasClass('loaded') && !el.hasClass('loading')){
                openNetworkLink(el);
            }else{
                $(this).parent().toggleClass('open');
            }
        });
        
        opts.element.find('li > span.toggler').live('click', function(){
            var node = $(this).parent();
            var toggle = !node.hasClass('visible');
            if(!toggle && node.hasClass('selected')){
                clearSelection();
            }
            if(!toggle && ge.getBalloon()){
                ge.setBalloon(null);
            }
            // toggleVisibility(node, toggle);
            if(node.hasClass('checkOffOnly') && toggle){
                // do nothing. Should not be able to toggle-on from this node.
                // http://code.google.com/apis/kml/documentation/kmlreference.html#liststyle
                return;
            }else{
                toggleVisibility(node, toggle);
            }
        });
        
        opts.element.find('li').live('dblclick', function(e){
            if($(e.originalTarget).parent().hasClass('expander')){
                return;
            }
            var node = $(this);
            var kmlObject = lookup(node);
            toggleVisibility(node, true);
            if(kmlObject.getType() == 'KmlTour'){
                ge.getTourPlayer().setTour(kmlObject);
            }else{
                var aspectRatio = null;
                if(opts.map_div){
                    var aspectRatio = $(opts.map_div).width() / $(opts.map_div).height();
                }
                opts.gex.util.flyToObject(kmlObject, {
                    boundsFallback: true,
                    aspectRatio: aspectRatio
                });
            }
            if(node.hasClass('fireEvents')){
                $(that).trigger('dblclick', [node, kmlObject]);
            }
            
        });
        
        // Google Earth Plugin Events
        
        google.earth.addEventListener(ge.getGlobe(), 'click', function(e, d){
            if(e.getButton() === -1){
                // related to scrolling, ignore
                return;
            }
            var target = e.getTarget();
            var balloon = ge.getBalloon();
            if(target.getType() === 'GEGlobe' && !balloon){
                // Seems like this combo makes balloons close when the user clicks
                // on the globe. When that !balloon test is not there, random 
                // click events fired when the user zooms in and out close the 
                // balloon. Not sure why
                clearSelection();
            }else if(target.getType() === 'KmlPlacemark'){
                var id = target.getId();
                var nodes = getNodesById(id);
                if(nodes.length === 1){
                    e.preventDefault();
                    selectNode(nodes[0], lookup(nodes[0]));
                }else{
                    // there should be an optimal way to handle this.
                }
            }
        });
        
        return that;
    };
})();