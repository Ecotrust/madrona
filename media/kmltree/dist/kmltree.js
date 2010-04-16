
// src/tmpl.js

// Simple JavaScript Templating
// John Resig - http://ejohn.org/ - MIT Licensed
(function(){
  var cache = {};
  
  this.tmpl = function tmpl(str, data){
    // Figure out if we're getting a template, or if we need to
    // load the template - and be sure to cache the result.
    var fn = !/\W/.test(str) ?
      cache[str] = cache[str] ||
        tmpl(document.getElementById(str).innerHTML) :
      
      // Generate a reusable function that will serve as a template
      // generator (and which will be cached).
      new Function("obj",
        "var p=[],print=function(){p.push.apply(p,arguments);};" +
        
        // Introduce the data as local variables using with(){}
        "with(obj){p.push('" +
        
        // Convert the template into pure JavaScript
        str
          .replace(/[\r\t\n]/g, " ")
          .split("<%").join("\t")
          .replace(/((^|%>)[^\t]*)'/g, "$1\r")
          .replace(/\t=(.*?)%>/g, "',$1,'")
          .split("\t").join("');")
          .split("%>").join("p.push('")
          .split("\r").join("\\'")
      + "');}return p.join('');");
    
    // Provide some basic currying to the user
    return data ? fn( data ) : fn;
  };
})();



// src/kmldom.js

// returns a jquery object that wraps the kml dom
kmldom = (function(){
    return function(kml){
        if( window.ActiveXObject && window.GetObject ) { 
            var dom = new ActiveXObject( 'Microsoft.XMLDOM' ); 
            dom.loadXML(kml); 
            return jQuery(dom);
        } 
        if( window.DOMParser ) {
            return jQuery(new DOMParser().parseFromString( kml, 'text/xml' ));
        }
        throw new Error( 'No XML parser available' );
    }
})();



// src/kmltree.js

var kmltree = (function(){

    openBalloon = function(kmlObject, ge, whitelisted){
        var b = ge.createFeatureBalloon('');
        b.setFeature(kmlObject);
        b.setMinWidth(100);
        ge.setBalloon(b);
    }
    
    // can be removed when the following ticket is resolved:
    // http://code.google.com/p/earth-api-samples/issues/detail?id=290
    function qualifyURL(url) {
        var a = document.createElement('a');
        a.href = url;
        return a.href;
    }

    var NetworkLinkQueue = function(opts){
        if(opts['success'] && opts['error'] && opts['tree'] && opts['my']){
            this.queue = [];
            this.opts = opts;
        }else{
            throw('missing required option');
        }
    };
    
    NetworkLinkQueue.prototype.add = function(node, callback){
        this.queue.push({
            node: node,
            callback: callback,
            loaded: false,
            errors: false
        });
    };
    
    NetworkLinkQueue.prototype.execute = function(){
        if(this.queue.length === 0){
            this.opts['success']([]);
        }else{
            for(var i=0;i<this.queue.length;i++){
                var item = this.queue[i];
                item.node.data('queueItem', item);
                if(!item.loaded && !item.loading){
                    var self = this;
                    $(item.node).bind('loaded', function(e, node, kmlObject){
                        self.nodeLoadedCallback(e, node, kmlObject)
                    });
                    this.opts['tree'].openNetworkLink(item.node);
                    item.loading = true;
                }
            }
        }
    };
    
    NetworkLinkQueue.prototype.nodeLoadedCallback = function(e, node, kmlObj){
        var item = node.data('queueItem');
        if(item.loaded === true){
            throw('event listener fired twice for '
                + node.find('>span.name').text());
        }
        item.loaded = true;
        item.loading = false;
        $(node).unbind('loaded');
        item.callback(node);
        this.finish(item);
    };
    
    NetworkLinkQueue.prototype.finish = function(item){
        var done = true;
        var noerrors = true;
        for(var i=0;i<this.queue.length;i++){
            done = (done && this.queue[i].loaded);
            noerrors = (noerrors && !this.queue[i].errors);
        }
        if(done){
            if(noerrors){
                this.opts['success'](this.queue);
                this.destroy();                
            }else{
                this.opts['error'](this.queue);
                this.destroy();                
            }
        }
    };
    
    NetworkLinkQueue.prototype.destroy = function(){
        for(var i=0;i<this.queue.length;i++){
            var item = this.queue[i];
            item.node.unbind('load');
        }
        this.queue = [];
    };
    
    // Returns a jquery object representing a kml file
    
    var template = tmpl([
        '<li UNSELECTABLE="on" class="',
        '<%= listItemType %> ',
        '<%= type %> ',
        '<%= customClass %> ',
        '<%= (visible ? "visible " : "") %>',
        '<%= (customIcon ? "hasIcon " : "") %>',
        '<%= (alwaysRenderNodes ? "alwaysRenderNodes " : "") %>',
        '<%= (select ? "select " : "") %>',
        '<%= (open ? "open " : "") %>',
        '<%= (description ? "hasDescription " : "") %>',
        '<%= (snippet ? "hasSnippet " : "") %>',
        '<%= (customIcon ? "customIcon " : "") %>',
        'kmltree-id-<%= id %> kmltree-item',
        '">',
            '<span class="kmlId"><%= kmlId %></span>',
            '<span class="nlDocId"></span>',
            '<div UNSELECTABLE="on" class="expander">',
                '&nbsp;',
            '</div>',
            '<div UNSELECTABLE="on" class="toggler">',
                '&nbsp;',
            '</div>',
            '<div ',
            '<% if(customIcon){ %>',
                'style="background:url(<%= customIcon %>);"',
            '<% } %>',
            'class="icon">',
                '&nbsp;',
            '</div>',
            '<span UNSELECTABLE="on" class="name"><%= name %></span>',
            '<% if(snippet){ %>',
                '<p UNSELECTABLE="on" class="snippet"><%= snippet %></p>',
            '<% } %>',
            '<% if(children.length) { %>',
            '<ul><%= renderOptions(children) %></ul>',
            '<% } %>',
        '</li>'
    ].join(''));
    
    var constructor_defaults = {
        enableSelection: function(){return false;},
        visitFunction: function(kmlObject, config){return config},
        openNetworkLinks: true,
        refreshWithState: true,
        bustCache: false,
        restoreState: false,
        // whiteListed: false,
        supportItemIcon: false,
        loadingMsg: 'Loading data'
    };
        
        
    return function(opts){
        
        var that = {};
        var errorCount = 0;
        var lookupTable = {};
        that.lookupTable = lookupTable;
        that.kmlObject = null;
        var docs = {};
        var my = {};
        var opts = jQuery.extend({}, constructor_defaults, opts);
        var ge = opts.gex.pluginInstance;
        var destroyed = false;

        if(parseFloat(ge.getPluginVersion()) < 5.1){
            throw('kmltree requires a google earth plugin version >= 5.1');
        }
                
        if(!opts.url || !opts.gex || !opts.element){
            throw('kmltree requires options url, gex & element');
        }
        
        if(!opts.element.attr('id')){
            opts.element.attr('id', 'kml-tree'+(new Date()).getTime());
            opts.element.attr('UNSELECTABLE', "on");
        }
        
        if(opts.restoreState){
            $(window).unload(function(){
                that.destroy();
            });
        }
        
        if(opts.element.css('position') !== 'absolute'){
          $(opts.element).css({position: 'relative'});
        }
        
        
        var load = function(cachebust){
            if(that.kmlObject){
                throw('KML already loaded');
            }
            showLoading();
            var url = qualifyURL(opts.url);
            if(cachebust || opts.bustCache){
                var buster = (new Date()).getTime();
                if(url.indexOf('?') === -1){
                    url = url + '?cachebuster=' + buster;
                }else{
                    url = url + '&cachebuster=' + buster;
                }
            }
            google.earth.fetchKml(ge, url, function(kmlObject){
                if(!destroyed){
                    processKmlObject(kmlObject, url);
                }
            });
        };
        
        that.load = load;
        
        // returns all nodes that represent a kmlObject with a matching ID
        var getNodesById = function(id){
            if(id){
                id = id.replace(/\//g, '-');
                return opts.element.find('.kmltree-id-'+id);
            }
        };
        
        that.getNodesById = getNodesById;
                
        // Selects the first node found matching the ID
        var selectById = function(id){
            var node = getNodesById(id)[0];
            return selectNode(node, lookup(node));
        };
        
        that.selectById = selectById;
        
        var clearSelection = function(keepBalloons, dontTriggerEvent){
            var prev = $('#'+opts.element.attr('id'))
                .find('.selected').removeClass('selected');
            if(prev.length){
                prev.each(function(){
                    setModified($(this), 'selected', false);
                });
                if(!dontTriggerEvent){
                    $(that).trigger('select', [null, null]);
                }
            }
            var balloon = ge.getBalloon();
            if(balloon && !keepBalloons){
                ge.setBalloon(null);
            }
        }
        
        that.clearSelection = clearSelection;
        
        var restoreState = function(node, state, queue){
            if(node && state && queue){
                var unloadedNL = node.hasClass('KmlNetworkLink') 
                    && !node.hasClass('loaded');
                if(state.name !== 'root'){
                    var mods = state['modified'];
                    // console.log(node, node.find('>span.name').text(), mods);
                    if(mods){
                        var opening = false;
                        if(mods['open'] !== undefined){
                            if(unloadedNL){
                                if(mods['open'].current){
                                    opening = true;
                                    queue.add(node, function(loadedNode){
                                        restoreState(loadedNode, state, queue);
                                        queue.execute();
                                    });                                    
                                }else{
                                    if(node.hasClass('open')){
                                        node.removeClass('open');
                                        setModified(node, 'open', false);
                                    }
                                }
                            }else{
                                node.toggleClass('open', mods.open.current);
                                setModified(node, 'open', mods.open.current);
                            }
                        }
                        if(mods['visibility'] !== undefined){
                            if(node.hasClass('KmlNetworkLink') 
                            && node.hasClass('alwaysRenderNodes') 
                            && mods['visibility'].current
                            && !opening
                            && !node.hasClass('loading') 
                            && !node.hasClass('loaded')){
                                openNetworkLink(node);
                                $(node).bind('loaded', function(e, node, kmlObject){
                                    toggleVisibility(node, true);
                                    node.removeClass('open');
                                });                                
                            }else{
                                toggleItem(node, mods['visibility'].current);                                
                            }
                        }
                        if(mods['selected'] !== undefined){
                            selectNode(node, lookup(node));
                        }
                    }
                }else{
                    node.find('.KmlNetworkLink.open').removeClass('open');
                }
                if(!unloadedNL){
                    for(var i=0; i<state.children.length; i++){
                        var child = state.children[i];
                        var n = node.find('>ul>li>span.name:contains(' 
                            + child.name + ')').parent();
                        if(n.length === 1){
                            restoreState(n, child, queue);
                        }else if(n.length > 1){
                            n.each(function(){
                                var name = $(this).find('>span.name').text();
                                if(name === child.name){
                                    restoreState($(this), child, queue);
                                }
                            });
                        }
                    }
                }
                // node.find('.KmlNetworkLink.open').each(function(){
                //     var n = $(this);
                //     if(!n.hasClass('loading') && !n.hasClass('checkHideChildren')){
                //         queue.add(n, function(loadedNode){
                //             console.log('restoreState', loadedNode, state, queue);
                //             restoreState(loadedNode, state, queue);
                //             queueOpenNetworkLinks(queue, loadedNode);
                //             queue.execute();                                    
                //         });
                //     }
                // });                    
            }else{
                throw('called with invalid arguments');
            }
        }
        
        var showLoading = function(msg){
            hideLoading();
            var msg = msg || opts.loadingMsg;
            var h = $('<div class="kmltree-loading"><span>' + 
                msg + '</span></div>');
            var height = opts.element.height();
            if(height !== 0){
                h.height(height);
            }else{
                // h.height(200);
            }
            opts.element.append(h);
        };
        
        that.showLoading = showLoading;
        
        var hideLoading = function(){
            opts.element.find('.kmltree-loading').remove();
        };
        
        that.hideLoading = hideLoading;
        
        var processKmlObject = function(kmlObject, url){
            if (!kmlObject) {
                if(errorCount === 0){
                    errorCount++;
                    setTimeout(function(){
                        // Try to reset the browser cache, then try again
                        jQuery.ajax({
                            url: url,
                            success: function(){
                                that.load(true);
                            },
                            error: function(){
                                processKmlObject(kmlObject, url);
                            }
                        });
                        // try to load 
                    }, 100);
                    return;                    
                }else{
                    // show error
                    setTimeout(function() {
                        opts.element.html([
                            '<div class="kmltree">',
                                '<h4 class="kmltree-title">',
                                    'Error Loading',
                                '</h4>',
                                '<p class="error">',
                                    'could not load kml file. Try clicking ',
                                    '<a target="_blank" href="', url, '">',
                                        'this link',
                                    '</a>',
                                    ', then refreshing the application.',
                                '<p>',
                            '</div>'
                        ].join(''));
                        $(that).trigger('kmlLoadError', [kmlObject]);
                    },
                    0);
                    return;                    
                }
            }
            errorCount = 0;
            that.kmlObject = kmlObject;
            that.kmlObject.setVisibility(true);
            var options = buildOptions(kmlObject);
            
            
            var rendered = renderOptions(options.children[0].children);
            opts.element.find('div.kmltree').remove();
            opts.element.find('.kmltree-loading').before([
                '<div UNSELECTABLE="on" class="kmltree">',
                    '<h4 UNSELECTABLE="on" class="kmltree-title">',
                        options.children[0].name,
                    '</h4>',
                    '<ul UNSELECTABLE="on" class="kmltree">',
                        rendered,
                    '</ul>',
                '</div>'
            ].join(''));
            ge.getFeatures().appendChild(kmlObject);
            var queue = new NetworkLinkQueue({
                success: function(links){
                    hideLoading();
                    $(that).trigger('kmlLoaded', [kmlObject]);
                },
                error: function(links){
                    hideLoading();
                    $(that).trigger('kmlLoadError', [kmlObject]);
                },
                tree: that,
                my: my
            });
            // console.log('processKmlHandler: that.previousState: ', that.previousState);
            if(!that.previousState){
                if(opts.restoreState && !!window.localStorage){
                    that.previousState = getStateFromLocalStorage();
                }
            }
            
            if(that.previousState && that.previousState.children.length){
                // This will need to be altered at some point to run the queue
                // regardless of previousState, expanding networklinks that 
                // are set to open within the kml
                // console.log('restoring state with', that.previousState);
                restoreState(
                    opts.element.find('div.kmltree'), 
                    that.previousState, 
                    queue);
            }else{
                queueOpenNetworkLinks(queue, 
                    $('#' + opts.element.attr('id')));
            }
            queue.execute();
        };
        
        var queueOpenNetworkLinks = function(queue, topNode){
            // $(that).trigger('kmlLoaded', kmlObject);
            var links = topNode.find('li.KmlNetworkLink.open');
            // links.removeClass('open');
            // console.log(links);
            links.each(function(){
                // no need to open if checkHideChildren is set
                if(!$(this).hasClass('checkHideChildren')){
                    var node = $(this);
                    // console.log('queueOpenNetworkLinks', '"' + node.find('span.name').text() + '"');
                    // setModified(node, 'open', node.hasClass('open'));
                    node.removeClass('open');
                    queue.add(node, function(loadedNode){
                        // console.log('loadedNode', loadedNode);
                        loadedNode.addClass('open');
                        setModified(loadedNode, 'open', node.hasClass('open'));
                        // loadedNode.removeClass('open');
                        queueOpenNetworkLinks(queue, loadedNode);
                        queue.execute();
                    });                    
                }
            });
        };
        
        var buildOptions = function(kmlObject){
            var docid = addDocLookup(kmlObject);
            var topTreeNode;
            var options = {name: kmlObject.getName()};
            google.earth.executeBatch(ge, function(){
                opts.gex.dom.walk({
                    visitCallback: function(context){
                        var parent = context.current;
                        if(!parent.children){
                            parent.children = [];
                        }
                        var lookupId = addLookup(docid, this);
                        var snippet = this.getSnippet();
                        if(!snippet || snippet === 'empty'){
                            snippet = false;
                        }
                        var child = {
                            renderOptions: renderOptions,
                            name: this.getName() || '&nbsp;',
                            visible: !!this.getVisibility(),
                            type: this.getType(),
                            open: this.getOpen(),
                            id: this.getId().replace(/\//g, '-'),
                            description: this.getDescription(),
                            snippet: snippet,
                            select: opts.enableSelection(this),
                            // fireEvents: opts.fireEvents(this),
                            listItemType: getListItemType(this),
                            customIcon: customIcon(this),
                            customClass: '',
                            children: [],
                            kmlId: lookupId,
                            alwaysRenderNodes: false
                        }
                        child = opts.visitFunction(this, child);
                        parent.children.push(child);
                        if(child.listItemType !== 'checkHideChildren'){
                            context.child = child;
                        }else{
                            context.walkChildren = false;
                        }
                    },
                    rootObject: kmlObject,
                    rootContext: options
                });
            });
            return options;
        };
        
        var customIcon = function(kmlObject){
            if(!opts.supportItemIcon){
                return false;
            }
            var doc = kmldom(kmlObject.getKml());
            var root = doc.find('kml>Folder, kml>Document, kml>Placemark, ' + 
                'kml>NetworkLink');
            var href = root.find('>Style>ListStyle>ItemIcon>href').text();
            if(href){
                return href;
            }else{
                return false;
            }
        }
        
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
            if(opts.refreshWithState){
                // console.log('should restore state');
                that.previousState = getState();
                // console.log('that.previousState=', that.previousState);
            }
            clearLookups();
            clearKmlObjects();
            clearNetworkLinks();
            // opts.element.html('');
            ge.setBalloon(null);
            load(true);
        };

        that.refresh = refresh;
        
        // Deletes references to networklink kmlObjects, removes them from the
        // dom. Prepares for refresh or tree destruction.
        var clearNetworkLinks = function(){
            for(var key in docs){
                var nl = docs[key];
                if(nl && nl.getParentNode()){
                    opts.gex.dom.removeObject(nl);
                }
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
        
        var getStateFromLocalStorage = function(){
            var json = localStorage.getItem(
                'kmltree-('+opts.url+')');
            if(json){
                return JSON.parse(json);
            }else{
                return false;
            }
        };
        
        var setStateInLocalStorage = function(){
            var state = JSON.stringify(getState());
            localStorage.setItem('kmltree-('+opts.url+')', state);
        };
        
        
        var destroy = function(){
            destroyed = true;
            if(opts.restoreState && !!window.localStorage){
                setStateInLocalStorage();
            }
            clearLookups();
            clearKmlObjects();
            var id = opts.element.attr('id');
            $('#'+id+' li > span.name').die();
            $('#'+id+' li').die();
            $('#'+id+' li > .expander').die();
            opts.element.html('');
            // $(that).unbind();
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
        };
        
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
        };
        
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
            if(!kmlObject){
                kmlObject = lookup(node);
            }
            node = $(node);
            clearSelection(true, true);
            node.addClass('selected');
            toggleVisibility(node, true);
            node.addClass('selected');
            openBalloon(kmlObject, ge);
            
            var parent = node.parent().parent();
            
            while(!parent.hasClass('kmltree') 
                && !parent.find('>ul:visible').length){
                parent.addClass('open');
                var parent = parent.parent().parent();
            }
            
            setModified(node, 'selected', true);
            $(that).trigger('select', [node, kmlObject]);
        };
        
        that.selectNode = selectNode;
        
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
                                toggleItem($(children[0]), true);
                                toggleDown($(children[0]), true);
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
                    toggleItem($(this), false);
                });
            }
        };
        
        var toggleUp = function(node, toggling, from){
            var parent = node.parent().parent();
            if(!parent.hasClass('kmltree')){
                if(toggling){
                    var herParent = parent.parent().parent();
                    if(herParent.hasClass('radioFolder')){
                        // toggle off any siblings and toggle them down
                        herParent.find('>ul>li.visible').each(function(){
                            if(this !== parent[0]){
                                var sib = $(this);
                                toggleItem(sib, false);
                                toggleDown(sib, false);                               
                            }else{
                            }
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
                    toggleItem($(this), false);
                    toggleDown($(this), false);
                });
            }
            toggleItem(node, toggle);
            toggleDown(node, toggle);
            toggleUp(node, toggle);
        };
        
        var toggleItem = function(node, toggling){
            var node = $(node);
            if(node.hasClass('visible') === toggling){
                return;
            }
            setModified(node, 'visibility', toggling);
            var o = lookup(node);
            lookup(node).setVisibility(toggling);
            node.toggleClass('visible', toggling);
            
            if(node.hasClass('KmlNetworkLink') && node.hasClass('loaded')){
                var doc = lookupNlDoc(node);
                doc.setVisibility(toggling);
            }
        };
        
        var setModified = function(node, key, value){
            // console.log('setModified', node, key, value);
            var data = node.data('modified');
            if(!data){
                data = {};
            }
            if(!data[key]){
                data[key] = {};
                if(key === 'open'){
                    data[key].original = lookup(node).getOpen();
                }else if(key === 'visibility'){
                    data[key].original = lookup(node).getVisibility();
                }else{
                    data[key].original = !value;
                }
            }
            data[key].current = value;
            node.data('modified', data);
        };
        
        var getState = function(){
            var state = {
                name: 'root', 
                remove: false, 
                children: [], 
                parent: false
            };
            walk(function(node, context){
                var me = {
                    name: node.find('>span.name').text(), 
                    remove: true, 
                    children: [], 
                    parent: context
                };
                var modified = node.data('modified');
                var new_modified = {};
                var anykey = false;
                for(var key in modified){
                    if(modified[key].current !== modified[key].original){
                        new_modified[key] = modified[key];
                        anykey = key;
                    }
                }
                if(anykey){
                    me.modified = new_modified;
                    me.remove = false;
                    var other_context = context;
                    while(other_context.parent){
                        other_context.remove = false;
                        other_context = other_context.parent;
                    }
                }
                context.children.push(me);
                return me;
            }, state);
            
            // go back and remove any limbs of the tree with remove=true
            
            var removeRecursive_ = function(parent){
                if(parent.remove === true){
                    return false;
                }else{
                    var children = [];
                    for(var i=0; i<parent.children.length; i++){
                        var child = removeRecursive_(parent.children[i]);
                        if(child){
                            delete child.remove;
                            delete child.parent;
                            children.push(child);
                        }
                    }
                    parent.children = children;
                    return parent;
                }
            };
            var result = removeRecursive_(state);
            return result;
        };
        
        that.getState = getState;
        
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
                var link = NetworkLink.getLink();
                if(link){
                    link = link.getHref();
                }else{
                    // console.log('could not find link: ', '"' + node.find('span.name').text() + '"');
                    node.addClass('error');
                    // setModified(node, 'visibility', false);
                    $(node).trigger('loaded', [node, false]);
                    node.removeClass('open');
                    setModified(node, 'open', false);
                    return;
                }
                if(opts.bustCache){
                    var buster = (new Date()).getTime();
                    if(link.indexOf('?') === -1){
                        link = link + '?cachebuster=' + buster;
                    }else{
                        link = link + '&cachebuster=' + buster;
                    }
                }
                node.addClass('loading');
                google.earth.fetchKml(ge, link, function(kmlObject){
                    if(!kmlObject){
                        alert('Error loading ' + link);
                        node.addClass('error');
                        // setModified(node, 'visibility', false);
                        $(that).trigger('kmlLoadError', [kmlObject]);
                        node.removeClass('open');
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
                    setModified(node, 'open', node.hasClass('open'));
                    node.removeClass('loading');
                    node.addClass('loaded');
                    node.find('.nlDocId').text(getDocId(kmlObject));
                    $(node).trigger('loaded', [node, kmlObject]);
                    $(that).trigger('networklinkload', [node, kmlObject]);
                });
            }
        };
        
        that.openNetworkLink = openNetworkLink;
        
        // Depth-first traversal of all nodes in the tree
        // Will start out with all the children of the root KmlDocument, but
        // does not include the KmlDocument itself
        var walk = function(callback, context, node){
            var recurse_ = function(node, context){
                node.find('>ul>li').each(function(){
                    var el = $(this);
                    var newcontext = callback(el, context);
                    if(newcontext === false){
                        // Don't follow into child nodes
                        return true;
                    }else{
                        recurse_(el, newcontext);
                    }
                });
            };
            if(!node){
                node = opts.element.find('div.kmltree');
            }
            recurse_(node, context);
        };
        
        that.walk = walk;
        var id = opts.element.attr('id');
        
        $('#'+id+' li > span.name').live('click', function(){
            var node = $(this).parent();
            var kmlObject = lookup(node);
            if(node.hasClass('error') && node.hasClass('KmlNetworkLink')){
                if(kmlObject.getLink() && kmlObject.getLink().getHref()){
                    alert('Could not load NetworkLink with url ' + 
                        kmlObject.getLink().getHref())
                }else{
                    alert('Could not load NetworkLink. Link tag with href not found');
                }
            }
            if(node.hasClass('select')){
                selectNode(node, kmlObject);
            }else{
                clearSelection();
                if(node.hasClass('hasDescription') || kmlObject.getType() === 'KmlPlacemark'){
                    if(kmlObject.getType() === 'KmlPlacemark'){
                        toggleVisibility(node, true);
                    }
                    openBalloon(kmlObject, ge, opts['whiteListed']);
                }
            }
            $(that).trigger('click', [node[0], kmlObject]);
        });

        $('#'+id+' li > span.name').live('contextmenu', function(){            
            var parent = $(this).parent();
            var kmlObject = lookup(parent);
            $(that).trigger('contextmenu', [parent[0], kmlObject]);
        });
        
        // Events to handle clearing selection
                
        opts.element.click(function(e){
            if(e.target === this){
                clearSelection();
            }else{
                var el = $(e.target);
                if(el.hasClass('toggle') && !el.hasClass('select')){
                    clearSelection();
                }
            }
        });
        
        // expand events
        $('#'+id+' li > .expander').live('click', function(e){
            var el = $(this).parent();
            if(el.hasClass('KmlNetworkLink') && !el.hasClass('loaded') 
                && !el.hasClass('loading')){
                openNetworkLink(el);
            }else{
                el.toggleClass('open');
                setModified(el, 'open', el.hasClass('open'));
            }
        });
        
        $('#'+id+' li > .toggler').live('click', function(){
            var node = $(this).parent();
            var toggle = !node.hasClass('visible');
            if(!toggle && node.hasClass('selected')){
                clearSelection();
            }
            if(!toggle && ge.getBalloon()){
                ge.setBalloon(null);
            }
            if(node.hasClass('checkOffOnly') && toggle){
                // do nothing. Should not be able to toggle-on from this node.
                return;
            }else{
                if(node.hasClass('KmlNetworkLink') 
                    && node.hasClass('alwaysRenderNodes') 
                    && !node.hasClass('open') 
                    && !node.hasClass('loading') 
                    && !node.hasClass('loaded')){
                    openNetworkLink(node);
                    $(node).bind('loaded', function(e, node, kmlObject){
                        toggleVisibility(node, true);
                        node.removeClass('open');
                    });
                }else{
                    toggleVisibility(node, toggle);                    
                }
                // if(node.hasClass('fireEvents')){
                    $(that).trigger('toggleItem', [node, toggle]);
                // }
            }
        });
        
        $('#'+id+' li').live('dblclick', function(e){
            var target = $(e.target);
            var parent = target.parent();
            if(target.hasClass('expander')
                || target.hasClass('toggler') 
                || parent.hasClass('expander') 
                || parent.hasClass('toggler')){
                // dblclicking the expander icon or checkbox should not zoom
                return;
            }
            var node = $(this);
            var kmlObject = lookup(node);
            if(node.hasClass('error')){
                if(kmlObject.getLink() && kmlObject.getLink().getHref()){
                    alert('Could not load NetworkLink with url ' + 
                        kmlObject.getLink().getHref())
                }else{
                    alert('Could not load NetworkLink. Link tag with href not found');
                }                
                return;
            }
            toggleVisibility(node, true);
            if(kmlObject.getType() == 'KmlTour'){
                ge.getTourPlayer().setTour(kmlObject);
            }else{
                var aspectRatio = null;
                var m = $(opts.map_div);
                if(m.length){
                    var aspectRatio = m.width() / m.height();
                }
                if(kmlObject.getType() === 'KmlNetworkLink' 
                    && node.hasClass('loaded')){
                    opts.gex.util.flyToObject(lookupNlDoc(node), {
                        boundsFallback: true,
                        aspectRatio: aspectRatio
                    });                    
                }else{
                    opts.gex.util.flyToObject(kmlObject, {
                        boundsFallback: true,
                        aspectRatio: aspectRatio
                    });
                }
            }
            // if(node.hasClass('fireEvents')){
                $(that).trigger('dblclick', [node, kmlObject]);
            // }
            
        });
        
        // Google Earth Plugin Events
        var geAddListener = google.earth.addEventListener;
        
        geAddListener(ge.getGlobe(), 'click', function(e, d){
            if(e.getButton() === -1){
                // related to scrolling, ignore
                return;
            }
            var target = e.getTarget();
            var balloon = ge.getBalloon();
            if(target.getType() === 'GEGlobe' && !balloon){
                // Seems like this combo makes balloons close when the user 
                // clicks on the globe. When that !balloon test is not there, 
                // random click events fired when the user zooms in and out 
                // close the balloon. Not sure why
                clearSelection();
            }else if(target.getType() === 'KmlPlacemark'){
                var id = target.getId();
                var nodes = getNodesById(id);
                if(nodes.length >= 1){
                    // e.preventDefault();
                    selectNode(nodes[0], lookup(nodes[0]));
                }else{
                    clearSelection();
                    // there should be an optimal way to handle this.
                }
            }
        });
        
        var doubleClicking = false;
        
        geAddListener(ge.getGlobe(), 'dblclick', function(e, d){
            if(e.getButton() === -1){
                // related to scrolling, ignore
                return;
            }
            var target = e.getTarget();
            if(target.getType() === 'GEGlobe'){
                // do nothing
            }else if(target.getType() === 'KmlPlacemark'){
                var id = target.getId();
                var nodes = getNodesById(id);
                if(nodes.length >= 1){
                    // e.preventDefault();
                    if(!doubleClicking){
                        doubleClicking = true;
                        setTimeout(function(){
                            doubleClicking = false;
                            var n = $(nodes[0]);
                            $(that).trigger('dblclick', [n, target]);
                        }, 200);
                    }
                }else{
                    // do nothin
                }
            }
        });
        
        return that;
    };
})();