lingcod.kmlTree = (function(){

    var NetworkLinkQueue = function(opts){
        if(opts['success'] && opts['error'] && opts['tree'] && opts['my']){
            this.queue = [];
            this.opts = opts;
        }else{
            throw('missing required option');
        }
    };
    
    NetworkLinkQueue.prototype.add = function(node, callback){
        this.queue.push({node: node, callback: callback, loaded: false, errors: false});
    };
    
    NetworkLinkQueue.prototype.execute = function(){
        if(this.queue.length === 0){
            this.opts['success']([]);
        }else{
            for(var i=0;i<this.queue.length;i++){
                var item = this.queue[i];
                if(!item.loaded && !item.loading){
                    var self = this;
                    $(item.node).bind('loaded', function(){
                        $(item.node).unbind('loaded');
                        item.callback(item.node);
                        self.finish(item);
                    });
                    this.opts['my'].openNetworkLink(item.node);
                    item.loading = true;                    
                }
            }
            // start up opening networklinks
        }
    };
    
    NetworkLinkQueue.prototype.finish = function(item){
        item.loaded = true;
        item.loading = false;
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
        restoreStateOnRefresh: true,
        showTitle: true,
        bustCache: false,
        restoreState: false,
        whiteListed: false
    };
        
    // For some reason GEAPI can't switch between features when opening new
    // balloons accurately. Have to clear the old popup and add a timeout to
    // make sure the balloon A is closed before balloon b is opened.
    var openBalloon = function(kmlObject, plugin, whitelisted){
        var a = plugin.getBalloon();
        if(a){
            // there is already a balloon(a) open
            var f = a.getFeature();
            if(f !== kmlObject){
                // not trying to re-open the same balloon
                plugin.setBalloon(null);
                // try this function again in 50ms
                setTimeout(openBalloon, 50, kmlObject, plugin, whitelisted);
            }
        }else{
            // if balloon A closed or never existed, create & open balloon B
            kmlObject.setVisibility(true);
            if(whitelisted && kmlObject.getDescription()){
                var b = plugin.createHtmlStringBalloon('');
                b.setFeature(kmlObject); // optional
                b.setContentString(kmlObject.getDescription());
                plugin.setBalloon(b);
            }else{
                var b = plugin.createFeatureBalloon('');
                b.setFeature(kmlObject);
                plugin.setBalloon(b);                
            }
        }
    };
    
    return function(opts){
        var that = {};
        var lookupTable = {};
        that.kmlObject = null;
        var docs = {};
        var my = {};
        
        var opts = jQuery.extend({}, constructor_defaults, opts);
        var ge = opts.gex.pluginInstance;
        
        if(!opts.url || !opts.gex || !opts.element || !opts.trans){
            throw('kmlTree must be called with options url, gex, trans & element');
            return false;
        }
        
        if(!opts.element.attr('id')){
            opts.element.attr('id', 'kml-tree'+(new Date()).getTime());
        }
        
        if(opts.restoreState){
            $(window).unload(function(){
                that.destroy();
            });
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
            if(cachebust || opts.bustCache){
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
                prev.each(function(){
                    setModified($(this), 'selected', false);
                });
                $(that).trigger('select', [null, null]);                
            }
            var balloon = ge.getBalloon();
            if(balloon && !keepBalloons){
                ge.setBalloon(null);
            }
        }
        
        that.clearSelection = clearSelection;
        
        var restoreState = function(node, state, queue){
            if(node && state && queue){
                var unloadedNL = node.hasClass('KmlNetworkLink') && !node.hasClass('loaded');
                if(state.name !== 'root'){
                    if(state['modified']){
                        if(state['modified']['open'] !== undefined){
                            if(unloadedNL){
                                queue.add(node, function(loadedNode){
                                    restoreState(loadedNode, state, queue);
                                    queue.execute();
                                });
                            }else{
                                node.toggleClass('open', state['modified']['open'].current);
                                setModified(node, 'open', state['modified']['open'].current);
                            }
                        }
                        if(state['modified']['visibility'] !== undefined){
                            toggleItem(node, state['modified']['visibility'].current);
                        }
                        if(state['modified']['selected'] !== undefined){
                            selectNode(node, lookup(node));
                        }
                    }
                }
                if(!unloadedNL){
                    for(var i=0; i<state.children.length; i++){
                        var child = state.children[i];
                        var n = node.find('>ul>li>span.name:contains('+child.name+')').parent();
                        restoreState(n, child, queue);
                    }                    
                }
            }else{
                throw('called with invalid arguments');
            }
        }
        
        var processKmlObject = function(kmlObject, url){
            if (!kmlObject) {
                // show error
                setTimeout(function() {
                    var content = '<div class="marinemap-kmltree">';
                    if(opts.title){
                        content += '<h4 class="marinemap-kmltree-title">Error Loading</h4>';
                    }
                    opts.element.html(content + '<p class="error">could not load kml file with url '+url+'</p></div>');
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
            var queue = new NetworkLinkQueue({
                success: function(links){
                    $(that).trigger('kmlLoaded', kmlObject);
                },
                error: function(links){
                    $(that).trigger('kmlLoaded', kmlObject);
                },
                tree: that,
                my: my
            });
            if(!that.previousState){
                if(opts.restoreState && !!window.localStorage){
                    that.previousState = getStateFromLocalStorage();
                }
            }
            
            if(that.previousState && that.previousState.children.length){
                // This will need to be altered at some point to run the queue regardless of previousState, expanding networklinks that are set to open within the kml
                restoreState(opts.element.find('div.marinemap-kmltree'), that.previousState, queue);
            }else{
                queueOpenNetworkLinks(queue, $('#' + opts.element.attr('id')));
            }
            queue.execute();
        };
        
        var queueOpenNetworkLinks = function(queue, topNode){
            // $(that).trigger('kmlLoaded', kmlObject);
            topNode.find('li.KmlNetworkLink.open').each(function(){
                var node = $(this);
                setModified(node, 'open', node.hasClass('open'));
                node.removeClass('open');
                queue.add(node, function(loadedNode){
                    setModified(loadedNode, 'open', node.hasClass('open'));
                    loadedNode.removeClass('open');
                    queue.add(loadedNode, function(nn){
                        queueOpenNetworkLinks(queue, nn);
                    });
                });
            });
            queue.execute();
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
            if(opts.restoreStateOnRefresh){
                that.previousState = getState();
            }
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
        
        var getStateFromLocalStorage = function(){
            var json = localStorage.getItem('marinemap-kmltree-('+opts.url+')');
            if(json){
                return JSON.parse(json);
            }else{
                return false;
            }
        };
        
        var setStateInLocalStorage = function(){
            var state = JSON.stringify(getState());
            localStorage.setItem('marinemap-kmltree-('+opts.url+')', state);
        };
        
        
        var destroy = function(){
            if(opts.restoreState && !!window.localStorage){
                setStateInLocalStorage();
            }
            clearLookups();
            clearKmlObjects();
            var id = opts.element.attr('id');
            $('#'+id+' li > span.name').die();
            $('#'+id+' li').die();
            $('#'+id+' li > span.expander').die();
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
                    toggleItem($(this), false);
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
                    toggleItem($(this), false);
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
            lookup(node).setVisibility(toggling);
            node.toggleClass('visible', toggling);
            setModified(node, 'visibility', toggling);
            if(node.hasClass('KmlNetworkLink') && node.hasClass('loaded')){
                var doc = lookupNlDoc(node);
                doc.setVisibility(toggling);
            }
        };
        
        var setModified = function(node, key, value){
            var data = node.data('modified');
            if(!data || !data[key]){
                if(!data){
                    var data = {};
                }
                data[key] = {current: value, original: !value};
                node.data('modified', data);
                return;
            }else{
                if(data[key].original !== value){
                    data[key].current = value;
                    node.data('modified', data);
                }else{
                    delete data[key];
                    var nokeys = true;
                    for(var key in data){
                        nokeys = false;
                    }
                    if(nokeys){
                        node.removeData('modified');
                    }else{
                        node.data('modified', data);
                    }
                }
            }
        };
        
        var getState = function(){
            var asdf = opts.element.find('span.name:contains(asdf)').parent().find('ul span.name:contains(asdf)').parent();
            var state = {name: 'root', remove: false, children: [], parent: false};
            walk(function(node, context){
                var me = {name: node.find('>span.name').text(), remove: true, children: [], parent: context};
                var modified = node.data('modified');
                if(modified){
                    me.modified = modified;
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
                var link = NetworkLink.getLink().getHref();
                if(opts.bustCache){
                    var buster = (new Date()).getTime();
                    if(link.indexOf('?') === -1){
                        link = link + '?' + buster;
                    }else{
                        link = link + '&cachebuster=' + buster;
                    }
                }
                node.addClass('loading');
                google.earth.fetchKml(ge, link, function(kmlObject){
                    if(!kmlObject){
                        // alert('Error loading ' + link);
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
                    setModified(node, 'open', node.hasClass('open'));
                    node.removeClass('loading');
                    node.addClass('loaded');
                    node.find('.nlDocId').text(getDocId(kmlObject));
                    $(node).trigger('loaded', [node, kmlObject]);
                    $(that).trigger('networklinkload', [node, kmlObject]);
                });
            }
        };
        
        my.openNetworkLink = openNetworkLink;
        
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
                node = opts.element.find('div.marinemap-kmltree');
            }
            recurse_(node, context);
        };
        
        that.walk = walk;
        var id = opts.element.attr('id');
        
        
        $('#'+id+' li > span.name').live('click', function(){
            var node = $(this).parent();
            var kmlObject = lookup(node);
            if(node.hasClass('select')){
                selectNode(node, kmlObject);
            }else{
                clearSelection();
                if(node.hasClass('hasDescription')){
                    toggleVisibility(node, true);
                    openBalloon(kmlObject, ge, opts.whiteListed);
                }                
            }
            if(node.hasClass('fireEvents')){
                $(that).trigger('click', [node[0], kmlObject]);
            }
        });
            
        $('#'+id+' li.fireEvents > span.name').live('contextmenu', function(){
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
        
        // expand events
        $('#'+id+' li > span.expander').live('click', function(e){
            var el = $(this).parent();
            if(el.hasClass('KmlNetworkLink') && !el.hasClass('loaded') && !el.hasClass('loading')){
                openNetworkLink(el);
            }else{
                el.toggleClass('open');
                setModified(el, 'open', el.hasClass('open'));
            }
        });
        
        $('#'+id+' li > span.toggler').live('click', function(){
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
                // http://code.google.com/apis/kml/documentation/kmlreference.html#liststyle
                return;
            }else{
                toggleVisibility(node, toggle);
            }
        });
        
        $('#'+id+' li').live('dblclick', function(e){
            var target = $(e.target);
            var parent = target.parent();
            if(target.hasClass('expander') || target.hasClass('toggler') || parent.hasClass('expander') || parent.hasClass('toggler')){
                // Double-clicking the expander icon or checkbox should not zoom
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