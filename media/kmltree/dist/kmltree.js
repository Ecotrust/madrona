var kmltreeManager = (function(){
    that = {};
    var trees = [];
    var ge;
    var cache = {};
    
    function init(earthInstance){
        ge = earthInstance;
        google.earth.addEventListener(ge, 'balloonopening', balloonOpening);
        google.earth.addEventListener(ge, 'balloonclose', balloonClose);
        google.earth.addEventListener(ge.getGlobe(), 'click', function(e, d){
            if(e.getButton() === -1){
                // related to scrolling, ignore
                return;
            }
            var target = e.getTarget();
            if(target.getType() === 'GEGlobe' && $('.kmltree-selected').length){
                for(var i=0;i<trees.length;i++){
                    var treeEl = $(trees[i].api.opts.element);
                    if(treeEl.find('.kmltree-selected').length + treeEl.find('.kmltree-breadcrumb').length > 0){
                        trees[i].instance.clearSelection();
                    }
                }
            }
        });
    }
    
    var register = function(tree, privilegedApi){
        if(trees.length === 0){
            init(privilegedApi.opts.gex.pluginInstance);
        }
        trees.push({
            key: 'kmltree-tree-' + trees.length.toString(),
            instance: tree,
            api: privilegedApi
        });
    };
    
    that.register = register;
    
    var remove = function(tree){
        for(var i = 0; i<trees.length; i++){
            if(trees[i].instance === tree){
                trees.splice(i, 1);
                break;
            }
        }
        for(var key in cache){
            if(cache[key].instance === tree){
                delete cache[key];
            }
        }
        return tree;
    };
    
    that.remove = remove;
    
    var pauseListeners = function(callable){
        google.earth.removeEventListener(
            ge, 'balloonopening', balloonOpening);
        google.earth.removeEventListener(
            ge, 'balloonclose', balloonClose);
        callable();
        google.earth.addEventListener(
            ge, 'balloonopening', balloonOpening);
        google.earth.addEventListener(
            ge, 'balloonclose', balloonClose);        
    };
    
    that.pauseListeners = pauseListeners;
    
    var getApi = function(tree){
        for(var i=0;i<trees.length;i++){
            if(trees[i].instance === tree){
                return trees[i].api;
            }
        }
    };
    
    var balloonOpening = function(e){
        var f = e.getFeature();
        var tree = getOwner(f);
        if(tree){
            e.preventDefault();
            ge.setBalloon(null);
            var selectable = false;
            var id = f.getId();
            if(id){
                selectable = tree.api.opts.selectable;
                if(typeof selectable === 'function'){
                    selectable = selectable(f);
                }
            }
            if(selectable){
                tree.instance.selectById(id, f);
            }
            openBalloon(f, tree);
            return false;                
        } // otherwise feature likely loaded outside of a kmltree instance
    }
        
    var balloonClose = function(e){
        $('#kmltree-balloon-iframe').remove();
        for(var i=0;i<trees.length;i++){
            var treeEl = $(trees[i].api.opts.element);
            if(treeEl.find('.kmltree-selected').length + treeEl.find('.KmlNetworkLink.kmltree-breadcrumb:not(.loaded)').length === 1 && treeEl.find('.kmltree-cursor-2').length === 0){
                trees[i].instance.clearSelection();
            }else{
                // console.log('didnt find stuff', treeEl.find('.kmltree-selected'), treeEl.find('KmlNetworkLink.kmltree-breadcrumb:not(.loaded)'), treeEl.find('.kmltree-selected').length + treeEl.find('KmlNetworkLink.kmltree-breadcrumb:not(.loaded)').length);
            }
        }
    };
    
    var _clearEverythingButMe = function(tree){
        for(var i=0;i<trees.length;i++){
            if(trees[i].instance !== tree){
                if($(trees[i].api.opts.element).find('.kmltree-selected').length || $(trees[i].api.opts.element).find('.kmltree-breadcrumb').length){
                    trees[i].instance.clearSelection();                    
                }
            }
        }
    };
    
    that._clearEverythingButMe = _clearEverythingButMe;
        
    var ownsUrl = function(doc, url){
        if(doc.getUrl() === url){
            return true;
        }
        if(doc.getElementByUrl(url)){
            return true;
        }
    }

    var getOwner = function(kmlObject){
        var url = kmlObject.getUrl();
        var urlWithoutId = url.split('#')[0];
        if(cache[urlWithoutId]){
            return cache[urlWithoutId];
        }
        // First check if url matches root element
        for(var i=0;i<trees.length;i++){
            if(ownsUrl(trees[i].instance.kmlObject, url)){
                cache[urlWithoutId] = trees[i];
                return trees[i];
            }
        }
        // Then check each tree's expanded NetworkLinks
        // TODO: Test if this works
        for(var i=0;i<trees.length;i++){
            var tree = trees[i].instance;
            var api = trees[i].api;
            var docs = trees[i].api.docs;
            for(var j = 0; j<docs.length;j++){
                var doc = docs[j];
                if(ownsUrl(doc, url)){
                    cache[urlWithoutId] = trees[i];
                    return trees[i];
                }
            }
        }
        // Couldn't find. Could be content loaded outside kmltree. 
        // In any case, ignore
        return false;
    };
    
    that.getOwner = function(kmlObject){
        var t = getOwner(kmlObject);
        if(t){
            return t.instance;
        }else{
            return false;
        }
    };
    
    var openBalloon = function(kmlObject, tree){
        $(window).unbind("message.kmlTreeIframeEvents");
        var balloon;
        var tree = tree.instance ? tree.instance : tree;
        var api = tree.api ? tree.api : getApi(tree);
        // Compare getBalloonHtmlUnsafe to getBalloonHtml to determine whether
        // there is even any need to use an iframe to display unsafe content
        var allow = api.opts.displayEnhancedContent;
        if(typeof allow === 'function'){
            allow = allow(kmlObject);
        }
        if(allow){
            // don't bother checking if not going to display
            var unsafeHtml = kmlObject.getBalloonHtmlUnsafe();
            var safeHtml = kmlObject.getBalloonHtml();
            var safeHtml = $.trim(
                safeHtml.replace(
                    /\s*<!--\s*Content-type: mhtml-die-die-die\s*-->/, ''));
            var hasUnsafeContent = safeHtml != $.trim(unsafeHtml);
        }
        if(allow && hasUnsafeContent){
            balloon = ge.createHtmlDivBalloon('');
            var iframe = document.createElement('iframe');
            iframe.setAttribute('src', api.opts.iframeSandbox);
            iframe.setAttribute('frameBorder', '0'); 
            iframe.setAttribute('id', 'kmltree-balloon-iframe');
            var div = document.createElement('div');
            $(div).append(iframe);
            $(iframe).one('load', function(){
                $(window).bind("message.kmlTreeIframeEvents", {'window': iframe.contentWindow}, function(e){
                    var ev = e.originalEvent;
                    if(ev.source === e.data.window){
                        resize(ev);                        
                    }
                });
                var msg = JSON.stringify({
                    html: Base64.encode(unsafeHtml),
                    callback: Base64.encode(
                        api.opts.sandboxedBalloonCallback.toString())
                });
                // Posting to any domain since iframe popups may have their
                // window.location changed by javascript code in the 
                // description.
                this.contentWindow.postMessage(msg, '*');
            });
            balloon.setContentDiv(div);
        }else{
            balloon = ge.createFeatureBalloon('');
            // callback for normal popups. Enhanced popup balloonopen event is 
            // triggered by resize function
            var boCallback = function(e){
                // This has to be done within a setTimeout call. Otherwise you 
                // can't open another balloon using an event listener and 
                // count on that event to fire. I think this is so you can 
                // have callbacks like balloonOpening that don't go into an 
                // infinite loop
                google.earth.removeEventListener(
                    ge, 'balloonopening', boCallback);
                setTimeout(function(){
                    $(tree).trigger('balloonopen', [
                        e.getBalloon(), e.getFeature()]);
                }, 1);
            };
            google.earth.addEventListener(ge, 'balloonopening', boCallback);
        }
        balloon.setFeature(kmlObject);
        ge.setBalloon(balloon);
    };
    
    that._openBalloon = openBalloon;
        
    function resize(e){
        var b = ge.getBalloon();
        var f = b.getFeature();
        var iframe = $('#kmltree-balloon-iframe');
        if(
            // There should at least be an iframe present
            !iframe.length || 
            // Message must include a new dimension or specify that none could
            // be calculated
            !(e.data.match(/width/) || e.data.match(/unknownIframeDimensions/)
            ) || 
            // Make sure the current popup is an HtmlDivBalloon
            b.getType() !== 'GEHtmlDivBalloon'){
            // and if all those conditions aren't met...
            // Oooooo... A zombie Iframe!!!
            // don't do anything, that balloon has already closed
            return;
        }
        var tree = getOwner(f);
        var dim = JSON.parse(e.data)
        if(dim.unknownIframeDimensions){
            var dim = tree.api.opts.unknownIframeDimensionsDefault;
            if(typeof dim === 'function'){
                dim = dim(f);
            }
        }
        var el = $('#kmltree-balloon-iframe');
        b.setMinWidth(dim.width);
        b.setMaxWidth(dim.width + (dim.width * .1));
        b.setMinHeight(dim.height);
        b.setMaxHeight(dim.height + (dim.height * .1));
        el.height(dim.height);
        el.width(dim.width);
        $(tree.instance).trigger('balloonopen', [b, f]);            
    }
    
    // Implemented this because call window.frameElement on a cross-origin 
    // iframe results in a security exception.
    function frameElement(win){
        var iframes = document.getElementsByTagName('iframe');
        for(var i =0;i<iframes.length;i++){
            if(iframes[0].contentWindow === win){
                return iframes[i];
            }
        }
    }
        
    return that;
})();/**
*
*  Base64 encode / decode
*  http://www.webtoolkit.info/
*
**/
 
var Base64 = {
 
	// private property
	_keyStr : "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
 
	// public method for encoding
	encode : function (input) {
		var output = "";
		var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
		var i = 0;
 
		input = Base64._utf8_encode(input);
 
		while (i < input.length) {
 
			chr1 = input.charCodeAt(i++);
			chr2 = input.charCodeAt(i++);
			chr3 = input.charCodeAt(i++);
 
			enc1 = chr1 >> 2;
			enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
			enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
			enc4 = chr3 & 63;
 
			if (isNaN(chr2)) {
				enc3 = enc4 = 64;
			} else if (isNaN(chr3)) {
				enc4 = 64;
			}
 
			output = output +
			this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) +
			this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);
 
		}
 
		return output;
	},
 
	// public method for decoding
	decode : function (input) {
		var output = "";
		var chr1, chr2, chr3;
		var enc1, enc2, enc3, enc4;
		var i = 0;
 
		input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
 
		while (i < input.length) {
 
			enc1 = this._keyStr.indexOf(input.charAt(i++));
			enc2 = this._keyStr.indexOf(input.charAt(i++));
			enc3 = this._keyStr.indexOf(input.charAt(i++));
			enc4 = this._keyStr.indexOf(input.charAt(i++));
 
			chr1 = (enc1 << 2) | (enc2 >> 4);
			chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
			chr3 = ((enc3 & 3) << 6) | enc4;
 
			output = output + String.fromCharCode(chr1);
 
			if (enc3 != 64) {
				output = output + String.fromCharCode(chr2);
			}
			if (enc4 != 64) {
				output = output + String.fromCharCode(chr3);
			}
 
		}
 
		output = Base64._utf8_decode(output);
 
		return output;
 
	},
 
	// private method for UTF-8 encoding
	_utf8_encode : function (string) {
		string = string.replace(/\r\n/g,"\n");
		var utftext = "";
 
		for (var n = 0; n < string.length; n++) {
 
			var c = string.charCodeAt(n);
 
			if (c < 128) {
				utftext += String.fromCharCode(c);
			}
			else if((c > 127) && (c < 2048)) {
				utftext += String.fromCharCode((c >> 6) | 192);
				utftext += String.fromCharCode((c & 63) | 128);
			}
			else {
				utftext += String.fromCharCode((c >> 12) | 224);
				utftext += String.fromCharCode(((c >> 6) & 63) | 128);
				utftext += String.fromCharCode((c & 63) | 128);
			}
 
		}
 
		return utftext;
	},
 
	// private method for UTF-8 decoding
	_utf8_decode : function (utftext) {
		var string = "";
		var i = 0;
		var c = c1 = c2 = 0;
 
		while ( i < utftext.length ) {
 
			c = utftext.charCodeAt(i);
 
			if (c < 128) {
				string += String.fromCharCode(c);
				i++;
			}
			else if((c > 191) && (c < 224)) {
				c2 = utftext.charCodeAt(i+1);
				string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
				i += 2;
			}
			else {
				c2 = utftext.charCodeAt(i+1);
				c3 = utftext.charCodeAt(i+2);
				string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
				i += 3;
			}
 
		}
 
		return string;
	}
 
};
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


/*
 * Copyright Â© 2007 Dominic Mitchell
 * 
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 * Neither the name of the Dominic Mitchell nor the names of its contributors
 * may be used to endorse or promote products derived from this software
 * without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/*
 * An URI datatype.  Based upon examples in RFC3986.
 *
 * TODO %-escaping
 * TODO split apart authority
 * TODO split apart query_string (on demand, anyway)
 * TODO handle parameters containing empty strings properly
 * TODO keyword escaping
 *
 * @(#) $Id$
 */

// Globals we introduce.
var URI;
var URIQuery;

// Introduce a new scope to define some private helper functions.
(function () {

    //// HELPER FUNCTIONS /////
  
    // RFC3986 Â§5.2.3 (Merge Paths)
    function merge(base, rel_path) {
        var dirname = /^(.*)\//;
        if (base.authority && !base.path) {
            return "/" + rel_path;
        }
        else {
            return base.getPath().match(dirname)[0] + rel_path;
        }
    }

    // Match two path segments, where the second is ".." and the first must
    // not be "..".
    var DoubleDot = /\/((?!\.\.\/)[^\/]*)\/\.\.\//;

    function remove_dot_segments(path) {
        if (!path) {
            return "";
        }
        // Remove any single dots
        var newpath = path.replace(/\/\.\//g, '/');
        // Remove any trailing single dots.
        newpath = newpath.replace(/\/\.$/, '/');
        // Remove any double dots and the path previous.  NB: We can't use
        // the "g", modifier because we are changing the string that we're
        // matching over.
        while (newpath.match(DoubleDot)) {
            newpath = newpath.replace(DoubleDot, '/');
        }
        // Remove any trailing double dots.
        newpath = newpath.replace(/\/([^\/]*)\/\.\.$/, '/');
        // If there are any remaining double dot bits, then they're wrong
        // and must be nuked.  Again, we can't use the g modifier.
        while (newpath.match(/\/\.\.\//)) {
            newpath = newpath.replace(/\/\.\.\//, '/');
        }
        return newpath;
    }

    // give me an ordered list of keys of this object
    function hashkeys(obj) {
        var list = [];
        for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
                list.push(key);
            }
        }
        return list.sort();
    }

    // TODO: Make these do something
    function uriEscape(source) {
        return source;
    }

    function uriUnescape(source) {
        return source;
    }


    //// URI CLASS /////

    // Constructor for the URI object.  Parse a string into its components.
    // note that this 'exports' 'URI' to the 'global namespace'
    URI = function (str) {
        if (!str) {
            str = "";
        }
        // Based on the regex in RFC2396 Appendix B.
        var parser = /^(?:([^:\/?\#]+):)?(?:\/\/([^\/?\#]*))?([^?\#]*)(?:\?([^\#]*))?(?:\#(.*))?/;
        var result = str.match(parser);
        
        // Keep the results in private variables.
        var scheme    = result[1] || null;
        var authority = result[2] || null;
        var path      = result[3] || null;
        var query     = result[4] || null;
        var fragment  = result[5] || null;
        
        // Set up accessors.
        this.getScheme = function () {
            return scheme;
        };
        this.setScheme = function (newScheme) {
            scheme = newScheme;
        };
        this.getAuthority = function () {
            return authority;
        };
        this.setAuthority = function (newAuthority) {
            authority = newAuthority;
        };
        this.getPath = function () {
            return path;
        };
        this.setPath = function (newPath) {
            path = newPath;
        };
        this.getQuery = function () {
            return query;
        };
        this.setQuery = function (newQuery) {
            query = newQuery;
        };
        this.getFragment = function () {
            return fragment;
        };
        this.setFragment = function (newFragment) {
            fragment = newFragment;
        };
    };

    // Restore the URI to it's stringy glory.
    URI.prototype.toString = function () {
        var str = "";
        if (this.getScheme()) {
            str += this.getScheme() + ":";
        }
        if (this.getAuthority()) {
            str += "//" + this.getAuthority();
        }
        if (this.getPath()) {
            str += this.getPath();
        }
        if (this.getQuery()) {
            str += "?" + this.getQuery();
        }
        if (this.getFragment()) {
            str += "#" + this.getFragment();
        }
        return str;
    };

    // RFC3986 Â§5.2.2. Transform References;
    URI.prototype.resolve = function (base) {
        var target = new URI();
        if (this.getScheme()) {
            target.setScheme(this.getScheme());
            target.setAuthority(this.getAuthority());
            target.setPath(remove_dot_segments(this.getPath()));
            target.setQuery(this.getQuery());
        }
        else {
            if (this.getAuthority()) {
                target.setAuthority(this.getAuthority());
                target.setPath(remove_dot_segments(this.getPath()));
                target.setQuery(this.getQuery());
            }        
            else {
                // XXX Original spec says "if defined and empty"â€¦;
                if (!this.getPath()) {
                    target.setPath(base.getPath());
                    if (this.getQuery()) {
                        target.setQuery(this.getQuery());
                    }
                    else {
                        target.setQuery(base.getQuery());
                    }
                }
                else {
                    if (this.getPath().charAt(0) === '/') {
                        target.setPath(remove_dot_segments(this.getPath()));
                    } else {
                        target.setPath(merge(base, this.getPath()));
                        target.setPath(remove_dot_segments(target.getPath()));
                    }
                    target.setQuery(this.getQuery());
                }
                target.setAuthority(base.getAuthority());
            }
            target.setScheme(base.getScheme());
        }

        target.setFragment(this.getFragment());

        return target;
    };

    URI.prototype.parseQuery = function () {
        return URIQuery.fromString(this.getQuery(), this.querySeparator);
    };

    //// URIQuery CLASS /////

    URIQuery = function () {
        this.params    = {};
        this.separator = "&";
    };

    URIQuery.fromString = function (sourceString, separator) {
        var result = new URIQuery();
        if (separator) {
            result.separator = separator;
        }
        result.addStringParams(sourceString);
        return result;
    };

    
    // From http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4.1
    // (application/x-www-form-urlencoded).
    // 
    // NB: The user can get this.params and modify it directly.
    URIQuery.prototype.addStringParams = function (sourceString) {
        var kvp = sourceString.split(this.separator);
        var list, key, value;
        for (var i = 0; i < kvp.length; i++) {
            // var [key,value] = kvp.split("=", 2) only works on >= JS 1.7
            list  = kvp[i].split("=", 2);
            key   = uriUnescape(list[0].replace(/\+/g, " "));
            value = uriUnescape(list[1].replace(/\+/g, " "));
            if (!this.params.hasOwnProperty(key)) {
                this.params[key] = [];
            }
            this.params[key].push(value);
        }
    };

    URIQuery.prototype.getParam = function (key) {
        if (this.params.hasOwnProperty(key)) {
            return this.params[key][0];
        }
        return null;
    };

    URIQuery.prototype.toString = function () {
        var kvp = [];
        var keys = hashkeys(this.params);
        var ik, ip;
        for (ik = 0; ik < keys.length; ik++) {
            for (ip = 0; ip < this.params[keys[ik]].length; ip++) {
                kvp.push(keys[ik].replace(/ /g, "+") + "=" + this.params[keys[ik]][ip].replace(/ /g, "+"));
            }
        }
        return kvp.join(this.separator);
    };

})();// src/kmltree.js

// I don't like documentation being in more than one place, and I couldn't 
// find any javascript documentation tools that I found satisfactory. So,
// docs can be found on the project page and should be kept up to date there:
// http://code.google.com/p/kmltree/wiki/ApiReference
var kmltree = (function(){
        
    // can be removed when the following ticket is resolved:
    // http://code.google.com/p/earth-api-samples/issues/detail?id=290
    function qualifyURL(url) {
        var a = document.createElement('a');
        a.href = url;
        return a.href;
    }

    var NetworkLinkQueue = function(opts){
        if(opts['success'] && opts['error'] && opts['tree']){
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
        this.execute();
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
        '<li UNSELECTABLE="on" id="<%= id %>" class="kmltree-item ',
        '<%= listItemType %> ',
        '<%= type %> ',
        '<%= classname %> ',
        '<%= (visible ? "visible " : "") %>',
        '<%= (customIcon ? "hasIcon " : "") %>',
        '<%= (alwaysRenderNodes ? "alwaysRenderNodes " : "") %>',
        '<%= (select ? "select " : "") %>',
        '<%= (open ? "open " : "") %>',
        '<%= (description ? "hasDescription " : "") %>',
        '<%= (snippet ? "hasSnippet " : "") %>',
        '<%= (customIcon ? "customIcon " : "") %>',
        '<% if(kmlId){ %>',
            '<%= kmlId %> ',
        '<% } %>',
        '<% if(geoType){ %>',
            '<%= geoType %>',
        '<% } %>',
        '"',
        '<% if(kmlId){ %>',
            ' data-id="<%= kmlId %>"',
        '<% } %>',
        '>',
            '<div UNSELECTABLE="on" class="expander">&nbsp;</div>',
            '<div UNSELECTABLE="on" class="toggler">&nbsp;</div>',
            '<div ',
            '<% if(customIcon){ %>',
                'style="background:url(<%= customIcon %>); -moz-background-size:16px 16px; -webkit-background-size:16px 16px;"',
            '<% } %>',
            'class="icon">',
                '<% if(type === "KmlNetworkLink"){ %>',
                    '<div class="nlSpinner">&nbsp;</div>',
                '<% } %>',                
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
        refreshWithState: true,
        bustCache: false,
        restoreState: false,
        whitelist: [],
        supportItemIcon: false,
        loadingMsg: 'Loading data',
        setExtent: false,
        displayDocumentRoot: 'auto',
        displayEnhancedContent: false,
        iframeSandbox: 'http://kmltree.googlecode.com/hg/src/iframe.html',
        unknownIframeDimensionsDefault: {height: 450, width:530},
        sandboxedBalloonCallback: function(){},
        selectable: function(kmlObject){return false;},
        multipleSelect: false,
        classname: function(kmlObject){return ''}
    };
        
        
    return function(opts){
        
        var that = {};
        var errorCount = 0;
        var lookupTable = {};
        that.lookupTable = lookupTable;
        that.kmlObject = null;
        var docs = [];
        var opts = jQuery.extend({}, constructor_defaults, opts);
        var ge = opts.gex.pluginInstance;
        var destroyed = false;
        var internalState = {};
        var selectData = [];

        function clearSelectData(){
            selectData = [];
        }
        
        function indexOfSelectData(node, kmlObject){
            for(var i=0;i<selectData.length;i++){
                if($(selectData[i]['node'])[0] === $(node)[0]){
                    return i;
                }
            }
            return -1;            
        };
        
        function addSelectData(node, kmlObject){
            var index = indexOfSelectData(node, kmlObject);
            if(index === -1){
                selectData.push({'node': node, 'kmlObject': kmlObject});                
            }
        }
        
        function removeSelectData(node, kmlObject){
            var index = indexOfSelectData(node, kmlObject);
            if(index === -1){
                throw('removeSelectData error');                
            }else{
                selectData.splice(index, 1);
            }
        }

        if(parseFloat(ge.getPluginVersion()) < 5.2){
            alert('kmltree requires a google earth plugin version >= 5.2');
        }
                
        if(!opts.url || !opts.gex || !opts.element || !opts.mapElement){
            throw('kmltree requires options url, gex, mapElement & element');
        }
        
        opts.element = $(opts.element);
        
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
        
        // check for background-size support
        var div = $(['<div class="kmltree" style="',
            'background-size: 16px 16px; ',
            '-moz-background-size: 16px 16px; ',
            '-o-background-size: 16px 16px; ',
            '-webkit-background-size: 16px 16px; ',
            '-khtml-background-size: 16px 16px;"></div>'].join(''));

        var supportsBgSize = (div[0].style.backgroundSize !== undefined 
            || div[0].style.MozBackgroundSize  !== undefined
            || div[0].style.oBackgroundSize !== undefined
            || div[0].style.khtmlBackgroundSize !== undefined
            || div[0].style.webkitBackgroundSize !== undefined);
        
        
        
        var buildOptions = function(kmlObject, docUrl, extra_scope){
            var options = {name: kmlObject.getName(), 
                id: 'kml' + 
                (extra_scope ? extra_scope.replace(/\W/g, '-') : '') + 
                docUrl.replace(/\W/g, '-')};
            google.earth.executeBatch(ge, function(){
                opts.gex.dom.walk({
                    visitCallback: function(context){
                        var parent = context.current;
                        if(!parent.children){
                            parent.children = [];
                        }
                        var name = this.getName();
                        var id = addLookup(this, parent.id, docUrl, name);
                        var snippet = this.getSnippet();
                        // To support generated output from certain software 
                        // (Arc2Earth, etc)
                        if(!snippet || snippet === 'empty'){
                            snippet = false;
                        }
                        var type = this.getType();
                        var geotype = false;
                        if(type === 'KmlPlacemark'){
                            var geo = this.getGeometry();
                            if(geo){
                                geotype = geo.getType();
                            }
                        }
                        var style = this.getComputedStyle();
                        var selectable = opts.selectable;
                        if(typeof selectable === 'function'){
                            selectable = selectable(this);
                        }
                        selectable = selectable && this.getId();
                        var child = {
                            renderOptions: renderOptions,
                            name: name || '&nbsp;',
                            visible: !!this.getVisibility(),
                            type: type,
                            open: this.getOpen(),
                            id: id,
                            description: this.getDescription(),
                            snippet: snippet,
                            select: selectable,
                            listItemType: getListItemType(style),
                            customIcon: customIcon(this),
                            classname: opts.classname(this),
                            children: [],
                            alwaysRenderNodes: false,
                            kmlId: this.getId().replace(/\W/g, '-'),
                            geoType: geotype
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
                    processKmlObject(kmlObject, url, opts.url);
                }
            });
        };
        
        that.load = load;
        
        var refresh = function(){
            if(opts.refreshWithState){
                that.previousState = getState();
            }
            clearKmlObjects();
            clearLookups();
            // opts.element.html('');
            ge.setBalloon(null);
            load(true);
        };

        that.refresh = refresh;
        
        // returns all nodes that represent a kmlObject with a matching ID
        var getNodesById = function(id){
            return opts.element.find('.'+id.replace(/\W/g, '-'));
        };
        
        that.getNodesById = getNodesById;
        
        
        var expandParentsOf = function(node){
            node = $(node);
            var parent = node.parent().parent();
            while(!parent.hasClass('kmltree') 
                && !parent.find('>ul:visible').length){
                parent.addClass('open');
                var parent = parent.parent().parent();
            }
        };
        
        that.expandParentsOf = expandParentsOf;
        
        // Selects the first node found matching the ID
        var selectById = function(id, kmlObject, silent){
            var nodes = getNodesById(id);
            if(nodes.length){
                var node = $(nodes[0]);
                clearSelection(true, true);
                selectNode(node, kmlObject || lookup(node), silent);
                return true;
            }else{
                // couldn't find feature in list. Might be in unexpanded 
                // networklink
                // highlight parent networklink if feature isn't shown in 
                // the tree yet
                var node = getFirstRenderedParentNetworkLink(kmlObject);
                if(node){
                    node = $(node);
                    if(node.is(':visible')){
                        clearSelection(true, true);
                        node.addClass('kmltree-breadcrumb');
                        if(!silent){
                            triggerSelect(node, kmlObject);
                        }
                        return true;                        
                    }else{
                        setExpanderBreadcrumbs(node);
                        // var parent = firstVisibleParentOf(node);
                        node.addClass('kmltree-breadcrumb');
                        // setModified maybe someday
                        if(!silent){
                            triggerSelect(parent, kmlObject);
                        }
                    }
                }else{
                    clearSelection();
                    return false;                    
                }
            }
        };
        
        that.selectById = selectById;
        
        var getParentNetworkLink = function(kmlObject){
            var parent = kmlObject.getParentNode();
            switch(parent.getType()){
                case 'KmlNetworkLink':
                    return parent;
                    break;
                case 'GEGlobe':
                    return false;
                    break;
                default:
                    return getParentNetworkLink(parent);
            }
        };
        
        var getFirstRenderedParentNetworkLink = function(kmlObject, loadedNl){
            var treeid = opts.element.attr('id');
            if(!loadedNl){
                var loadedNl = [];
                $('#'+treeid+' li.KmlNetworkLink').each(function(){
                    if(!$(this).hasClass('loaded')){
                        loadedNl.push([this, lookup(this)]);                        
                    }
                });
            }
            var nL = getParentNetworkLink(kmlObject);
            if(nL === false){
                // walked all the way up to GEGlobe, couldn't find it.
                return false;
            }else{
                // if nL has an ID, look for that
                // look at all networklinks in tree that aren't expanded
                var url = nL.getLink().getHref();
                for(var i=0;i<loadedNl.length;i++){
                    var loadedHref = loadedNl[i][1].getLink().getHref();
                    var nLHref = nL.getLink().getHref()
                    if(nLHref === loadedHref){
                        return loadedNl[i][0];
                    }
                }
                // if none match, keep moving up until hitting ge globe
                return getFirstRenderedParentNetworkLink(nL, loadedNl);
            }
        };
        
        var selectNode = function(node, kmlObject, silent){
            if(!kmlObject){
                kmlObject = lookup(node);
            }
            node = $(node);
            var visible = $(node).is(':visible'); // need to make this actually work
            toggleVisibility(node, true);
            node.addClass('kmltree-selected');
            setModified(node, 'selected', true);         
            if(!visible){
                setExpanderBreadcrumbs(node);
            }
            if(!silent){
                kmltreeManager._clearEverythingButMe(that);
                triggerSelect(node, kmlObject);
            }else{
                addSelectData(node, kmlObject);
            }
        };
        
        that.selectNode = selectNode;
        
        var selectNodes = function(nodes, silent){
            var last = nodes.length - 1;
            nodes.each(function(i){
                selectNode(this, null, !!silent || (!silent && i !== nodes.length - 1));
            });
        };
        
        that.selectNodes = selectNodes;
                
        var deselectNodes = function(nodes, silent){
            nodes.each(function(i){
                deselectNode(this, null, !!silent || (!silent && i !== nodes.length - 1));
            });
        };
                
        that.deselectNodes = deselectNodes;

        var deselectNode = function(node, kmlObject, silent){
            if(!kmlObject){
                kmlObject = lookup(node);
            }
            node = $(node);
            // var visible = $(node).is(':visible');
            node.removeClass('kmltree-selected');
            setModified(node, 'selected', false);
            // if(!visible){
            //     setExpanderBreadcrumbs(node);
            // }
            if(!silent){
                removeAndTrigger(node, kmlObject);
            }else{
                removeSelectData(node, kmlObject);
            }
        };
        
        var triggerSelect = function(node, kmlObject){
            if(node && kmlObject){
                addSelectData(node, kmlObject);
            }else{
                clearSelectData();
            }
            setTimeout(function(){
                $(that).trigger('select', [selectData]);
            }, 1);
        };
        
        var removeAndTrigger = function(node, kmlObject){
            removeSelectData(node, kmlObject);
            setTimeout(function(){
                $(that).trigger('select', [selectData]);
            }, 1);
        }
        
        var setExpanderBreadcrumbs = function(node){
            var node = $(node);
            var parent = node.parent().parent();
            parent.addClass('kmltree-breadcrumb');
            if(!parent.is(':visible')){
                return setExpanderBreadcrumbs(parent);
            }else{
                return parent;
            }
        };
                
        var clearSelection = function(keepBalloons, dontTriggerEvent){
            clearSelectData();
            var treeEl = $('#'+opts.element.attr('id'));
            var prev = treeEl
                .find('.kmltree-selected').removeClass('kmltree-selected');
            treeEl.find('.kmltree-breadcrumb')
                .removeClass('kmltree-breadcrumb');
            treeEl.find('.kmltree-cursor-1').removeClass('kmltree-cursor-1');
            treeEl.find('.kmltree-cursor-2').removeClass('kmltree-cursor-2');
            if(prev.length){
                prev.each(function(){
                    setModified($(this), 'selected', false);
                });
            }
            if(!dontTriggerEvent){
                triggerSelect(null, null);
            }
            var balloon = ge.getBalloon();
            if(balloon && !keepBalloons){
                ge.setBalloon(null);
            }
        }
        
        // Don't give external callers access to the keepBalloons and 
        // dontTriggerEvent arguments
        that.clearSelection = function(){
            return clearSelection();
        };
                    
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
        
        // url has cachebusting GET vars, original_url does not
        var processKmlObject = function(kmlObject, url, original_url){
            internalState = {};
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
                                processKmlObject(
                                    kmlObject, url, original_url);
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
            docs.push(kmlObject);
            that.kmlObject.setVisibility(true);
            var options = buildOptions(kmlObject, original_url);
            var root;
            if(opts.displayDocumentRoot === false){
                root = options.children[0].children;
            }else if(opts.displayDocumentRoot === true){
                root = options.children[0];
            }else{ // opts.displayDocumentRoot === 'auto'
                var children = options.children[0].children;
                var i = 0;
                var placemarks = false;
                while(i < children.length && placemarks === false){
                    placemarks = children[i].type === 'KmlPlacemark';
                    i++;
                }
                if(placemarks){
                    root = options.children[0];
                }else{
                    root = options.children[0].children;
                }
            }
            var rendered = renderOptions(root);
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
            
            if(!that.previousState){
                if(opts.restoreState && !!window.localStorage){
                    that.previousState = getStateFromLocalStorage();
                }
            }
            var queue = new NetworkLinkQueue({
                success: function(links){
                    hideLoading();
                    if(opts.setExtent){
                        var aspectRatio = null;
                        var m = $(opts.mapElement);
                        if(m.length){
                            var aspectRatio = m.width() / m.height();
                        }
                        opts.gex.util.flyToObject(kmlObject, {
                            boundsFallback: true,
                            aspectRatio: aspectRatio
                        });
                        opts.setExtent = false;
                    }
                    $(that).trigger('kmlLoaded', [kmlObject]);
                },
                error: function(links){
                    hideLoading();
                    $(that).trigger('kmlLoadError', [kmlObject]);
                },
                tree: that
            });
            if(that.previousState){
                restoreState(that.previousState, queue);
            }else{
                queueOpenNetworkLinks(queue, 
                    $('#' + opts.element.attr('id')));
            }
        };
        
        var restoreState = function(state, queue){
            // go thru the whole state, opening, changing visibility, 
            // and selecting
            for(var id in state){
                var el = $('#'+id);
                if(el.length === 1){
                    for(var key in state[id]){
                        el.toggleClass(key, state[id][key]['value']);
                        setModified(el, key, state[id][key]['value']);
                        if(key === 'visible'){
                            lookup(el).setVisibility(state[id][key]['value']);
                        }
                    }
                    delete state[id];
                }
            }
            var links = $('#' + opts.element.attr('id')).find(
                'li.KmlNetworkLink.open');
            links.each(function(){
                var n = $(this);
                // no need to open if checkHideChildren is set
                if(!n.hasClass('checkHideChildren') && !n.hasClass('loading') 
                    && !n.hasClass('loaded') && !n.hasClass('error')){
                    queue.add(n, function(loadedNode){
                        restoreState(state, queue);
                    });                    
                }
            });
            queue.execute();
        }
        
        var queueOpenNetworkLinks = function(queue, topNode){
            var links = topNode.find('li.KmlNetworkLink.open');
            links.each(function(){
                var n = $(this);
                // no need to open if checkHideChildren is set
                if(!n.hasClass('checkHideChildren') && !n.hasClass('loading') 
                    && !n.hasClass('loaded')){
                    n.removeClass('open');
                    queue.add(n, function(loadedNode){
                        loadedNode.addClass('open');
                        setModified(loadedNode, 'open', 
                            n.hasClass('open'));
                        queueOpenNetworkLinks(queue, loadedNode);
                    });                    
                }
            });
            queue.execute();
        };
                
        var customIcon = function(kmlObject){
            var result = false;
            
            if(supportsBgSize && kmlObject.getType() === 'KmlPlacemark' && 
                kmlObject.getGeometry() && 
                kmlObject.getGeometry().getType() === 'KmlPoint'){
                result = kmlObject.getComputedStyle().getIconStyle()
                    .getIcon().getHref();
            }
            if(!opts.supportItemIcon){
                return result;
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
        var getListItemType = function(style){
            var listItemType = 'check';
            var lstyle = style.getListStyle();
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
        
        // Deletes references to networklink kmlObjects, removes them from the
        // dom. Prepares for refresh or tree destruction.
        var clearNetworkLinks = function(){
            $('.KmlNetworkLink').each(function(){
                var kmlObject = lookup($(this));
                if(kmlObject && kmlObject.getParentNode()){
                    opts.gex.dom.removeObject(lookup($(this)));
                }
            });
        };
        
        var clearKmlObjects = function(){
            clearNetworkLinks();
            if(that.kmlObject && that.kmlObject.getParentNode()){
                opts.gex.dom.removeObject(that.kmlObject);
                // that.kmlObject.release();
            }
            that.kmlObject = null;
            docs = [];
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
            kmltreeManager.remove(that);
            if(opts.restoreState && !!window.localStorage){
                setStateInLocalStorage();
            }
            clearKmlObjects();
            clearLookups();
            var b = ge.getBalloon();
            if(b){
                var f = b.getFeature();
                if(f){
                    var owner = kmltreeManager.getOwner(f);
                    if(owner && owner.instance === that){
                        ge.setBalloon(null);
                    }
                }
            }
            ge.setBalloon(null);
            var id = opts.element.attr('id');
            $('#'+id+' li > span.name').die();
            $('#'+id+' li').die();
            $('#'+id+' li > .expander').die();
            $(that).die();
            $(that).unbind();
            $('#kmltree-balloon-iframe').remove();
            opts.element.html('');
        };
        
        that.destroy = destroy;
        
        var lookup = function(li){
            var li = $(li);
            if(li.length){
                return lookupTable[li.attr('id')];
            }else{
                return false;
            }
        };
        
        that.lookup = lookup;
        
        var addLookup = function(kmlObject, parentID, docUrl, name){
            var id = getID(kmlObject, parentID, docUrl, name);
            // if the ID exists already, just append the position of the 
            // repeated name to the id.
            var tries = 0;
            while(!!lookupTable[id]){
                tries++;
                id = id + tries;
            }
            lookupTable[id] = kmlObject;
            return id;
        };
        
        // Returns an ID that is used on the DOM element representing this 
        // kmlObject. If the kmlObject has it's own ID, the generated ID will
        // be created from that ID + the kml document's url. If not, the name
        // of the element and the name of it's parents will be used to 
        // generate an ID.
        // 
        // Arguments: kmlObject, parentID
        var getID = function(kmlObject, parentID, docUrl, name, ignoreID){
            if(name){
                key = name.replace(/\W/g, '-');
            }else{
                key = "blank"
            }
            return parentID + key;
        };

        var setLookup = function(node, kmlObject){
            lookupTable[node.attr('id')] = kmlObject;
        };
                
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
            if(toggle && node.find('li.visible').length){
                // if children are already toggled, do nothing
            }else{
                toggleDown(node, toggle);                
            }
            toggleUp(node, toggle);
        };
        
        var toggleItem = function(node, toggling){
            var node = $(node);
            if(node.hasClass('visible') === toggling){
                return;
            }
            setModified(node, 'visible', toggling);
            lookup(node).setVisibility(toggling);
            node.toggleClass('visible', toggling);            
        };
        
        var setModified = function(node, key, value){
            var id = node.attr('id');
            if(!internalState[id]){
                internalState[id] = {};
            }
            var record = internalState[id];
            if(!record[key]){
                record[key] = {original: !value, value: value}
            }else{
                record[key]['value'] = value;
            }
        };
        
        var getState = function(){
            for(var id in internalState){
                for(var key in internalState[id]){
                    if(internalState[id][key]['original'] === 
                        internalState[id][key]['value']){
                        delete internalState[id][key];
                    }
                }
                var len = 0;
                for(var key in internalState[id]){
                    if(internalState[id].hasOwnProperty(key)){
                        len++;
                    }
                }
                if(len === 0){
                    delete internalState[id];
                }
            }
            return internalState;
        };
        
        that.getState = getState;
        
        var openNetworkLink = function(node){
            if(node.find('> ul').length){
                throw('networklink already loaded');
            }else{
                var NetworkLink = lookup(node);
                var link = NetworkLink.getLink();
                if(link){
                    link = link.getHref();
                    var original_url = link;
                }else{
                    var dom = kmldom(NetworkLink.getKml());
                    var href = dom.find('Url>href');
                    if(href.length){
                        var link = href.text();
                        var original_url = link;
                    }else{
                        node.addClass('error');
                        // setModified(node, 'visibility', false);
                        $(node).trigger('loaded', [node, false]);
                        node.removeClass('open');
                        setModified(node, 'open', false);
                        return;                        
                    }
                }
                var uri = new URI(link);
                if(uri.getAuthority() === null){
                    window.nl = NetworkLink;
                    var doc = NetworkLink.getOwnerDocument();
                    window.doc = doc;
                    if(doc && doc.getUrl()){
                        var base = doc.getUrl();
                        if(base){
                            var base = new URI(base);
                            var new_url = uri.resolve(base);
                        }
                    }
                    if(!new_url){
                        alert(['Could not resolve relative link in kml ',
                                'document. You may need to upgrade to the ',
                                'latest Google Earth Plugin.'].join());
                    }else{
                        link = new_url.toString();
                    }
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
                    var extra_scope = NetworkLink.getName();
                    var parent = NetworkLink.getParentNode();
                    parent.getFeatures().removeChild(NetworkLink);
                    var data = buildOptions(kmlObject, original_url, 
                        extra_scope);
                    var html = renderOptions(data.children[0].children);
                    node.append('<ul>'+html+'</ul>');
                    node.addClass('open');
                    setModified(node, 'open', node.hasClass('open'));
                    node.removeClass('loading');
                    node.addClass('loaded');
                    setLookup(node, kmlObject);
                    docs.push(kmlObject);
                    rememberNetworkLink(node, NetworkLink);
                    $(node).trigger('loaded', [node, kmlObject]);
                    $(that).trigger('networklinkload', [node, kmlObject]);                        
                });
            }
        };
        
        that.openNetworkLink = openNetworkLink;
        
        var rememberedLinks = [];
        
        var rememberNetworkLink = function(node, networkLink){
            $(node).attr(
                'data-rememberedLink', rememberedLinks.length.toString());
            rememberedLinks.push(networkLink);
        };
        
        var getNetworkLink = function(node){
            var id = $(node).attr('data-rememberedLink');
            if(id && rememberedLinks.length >= id){
                return rememberedLinks[id];
            }else{
                return false;
            }
        };
        
        that.getNetworkLink = getNetworkLink;
        
        // Creates a new NetworkLinkQueue that simply opens up the given 
        // NetworkLink and any open NetworkLinks within it.
        var openNetworkLinkRecursive = function(node, callback){
            var queue = new NetworkLinkQueue({
                success: function(links){
                    if(callback){
                        callback(node, links);
                    };
                },
                error: function(links){
                },
                tree: that
            });
            queue.add(node, function(loadedNode){
                loadedNode.addClass('open');
                setModified(loadedNode, 'open', 
                    node.hasClass('open'));
                queueOpenNetworkLinks(queue, loadedNode);
            });
            queue.execute();
        }
        
        var id = opts.element.attr('id');
        
        $('#'+id+' li > span.name').live('click', function(e){
            e.stopPropagation();
            var dontOpen = false;
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
                if(opts.multipleSelect && e.metaKey){
                    if(node.hasClass('kmltree-selected')){
                        $('.kmltree-cursor-1').removeClass('kmltree-cursor-1');
                        node.removeClass('kmltree-cursor-1');
                        deselectNode(node, kmlObject)
                    }else{
                        $('.kmltree-cursor-1').removeClass('kmltree-cursor-1');
                        $('.kmltree-cursor-2').removeClass('kmltree-cursor-2');
                        node.addClass('kmltree-cursor-1');
                        selectNode(node, kmlObject);                      
                    }
                    kmltreeManager.pauseListeners(function(){
                        ge.setBalloon(null);
                    });
                    dontOpen = true;
                }else if(opts.multipleSelect && e.shiftKey){
                    // if(node.hasClass('kmltree-selected') || node.hasClass('kmltree-breadcrumbs')){
                    //     // do nothing
                    // }else{
                    // make sure not shift+selecting something in a 
                    // different part of the tree (shift select only works 
                    // with siblings)
                    var treeEl = $('#'+opts.element.attr('id'));
                    selected = treeEl.find('.kmltree-selected');
                    if(selected.length === 1){
                        selected.addClass('kmltree-cursor-1');
                    }
                    var cursor1 = treeEl.find('.kmltree-cursor-1');
                    if(cursor1.length === 0){
                        // just do a normal selection
                        clearSelection(true, true);
                        selectNode(node, kmlObject);
                    }else{
                        var parent = node.parent().parent();
                        var first_cursor = treeEl.find('.kmltree-cursor-1');
                        if(first_cursor.parent().parent()[0] !== parent[0]){
                            // do nothing. can only shift-select siblings
                        }else{
                            var cursor2 = treeEl.find('.kmltree-cursor-2');
                            if(cursor2.length){
                                var cursors = treeEl.find('.kmltree-cursor-1, .kmltree-cursor-2');
                                var first = cursors.first();
                                var last = cursors.last()
                                var siblings = first.parent().parent().find('> ul > li');
                                // already have a range selected. Need to deselect
                                var range = first.nextUntil('[id="'+last.attr('id')+'"]').andSelf().add(last);
                                cursor2.removeClass('kmltree-cursor-2');
                                deselectNodes(range, true)
                            }
                            node.addClass('kmltree-cursor-2');
                            var cursors = treeEl.find('.kmltree-cursor-1, .kmltree-cursor-2');
                            var first = cursors.first();
                            var last = cursors.last();
                            var range;
                            if(first[0] === last[0]){
                                // just one is selected
                                range = first;
                                treeEl.find('.kmltree-cursor-1, .kmltree-cursor-2').removeClass('kmltree-cursor-2').removeClass('kmltree-cursor-1');
                            }else{
                                var siblings = first.parent().parent().find('> ul > li');
                                var range = first.nextUntil('[id="'+last.attr('id')+'"]').andSelf().add(last);                                
                            }
                            selectNodes(range);
                            kmltreeManager.pauseListeners(function(){
                                ge.setBalloon(null);
                            });
                        }
                            // if(selected.first)
                        // get furthest selected sibling
                        // deselect everything quickly
                        // select range 
                        dontOpen = true;
                    }
                }else{
                    clearSelection(true, true);
                    selectNode(node, kmlObject);
                }
            }else{
                clearSelection();
                node.addClass('kmltree-cursor-1');
                if(node.hasClass('hasDescription') || kmlObject.getType() === 
                    'KmlPlacemark'){
                    if(kmlObject.getType() === 'KmlPlacemark'){
                        toggleVisibility(node, true);
                    }
                }
            }
            if(!dontOpen){
                kmltreeManager.pauseListeners(function(){
                    kmltreeManager._openBalloon(kmlObject, that);
                });                
            }
            $(that).trigger('click', [node[0], kmlObject]);
        });

        $('#'+id+' li').live('contextmenu', function(e){
            var node = $(this);
            if(node.hasClass('select')){
                if(!node.hasClass('kmltree-selected')){
                    clearSelection(true, true);
                    selectNode(node);
                }
                setTimeout(function(){
                    // Set timeout so that it fires after select event if 
                    // selecting new feature
                    $(that).trigger('context', [selectData]);                    
                }, 2);
            }
            e.preventDefault();
            return false;
        });
        
        // Events to handle clearing selection
                
        opts.element.click(function(e){
            var el = $(e.target);
            var fire = false;
            if(e.target === this){
                fire = true;
            }else{
                if(el.hasClass('toggle') && !el.hasClass('select')){
                    fire = true;
                }
            }
            if(el.find('.kmltree-selected').length || el.find('.kmltree-breadcrumb').length){
                clearSelection();
            }            
        });
        
        // expand events
        $('#'+id+' li > .expander').live('click', function(e){
            var el = $(this).parent();
            var closing = el.hasClass('open');
            if(el.hasClass('KmlNetworkLink') && !el.hasClass('loaded') 
                && !el.hasClass('loading')){
                openNetworkLinkRecursive(el, function(node, links){
                    if(node.hasClass('kmltree-breadcrumb')){
                        if(closing){
                            if(el.find('.kmltree-selected').length){
                                el.addClass('kmltree-breadcrumb');
                            }
                        }else{
                            el.removeClass('kmltree-breadcrumb');                    
                        }
                        var kmlObject = ge.getBalloon().getFeature();
                        selectById(kmlObject.getId(), kmlObject, true);
                    }
                });
            }else{
                el.toggleClass('open');
                setModified(el, 'open', el.hasClass('open'));
                if(closing){
                    if(el.find('.kmltree-selected').length){
                        el.addClass('kmltree-breadcrumb');
                    }
                }else{
                    el.removeClass('kmltree-breadcrumb');                    
                }
            }
        });
        
        $('#'+id+' li > .toggler').live('click', function(){
            var node = $(this).parent();
            var toggle = !node.hasClass('visible');
            if(!toggle && node.hasClass('kmltree-selected')){
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
                    openNetworkLinkRecursive(node);
                    $(node).bind('loaded', function(e, node, kmlObject){
                        toggleVisibility(node, true);
                        node.removeClass('open');
                    });
                }else{
                    toggleVisibility(node, toggle);                    
                }
                $(that).trigger('toggleItem', [node, toggle, lookup(node)]);
            }
        });
        
        $('#'+id+' li').live('dblclick', function(e){
            e.stopPropagation();
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
                var m = $(opts.mapElement);
                if(m.length){
                    var aspectRatio = m.width() / m.height();
                }
                opts.gex.util.flyToObject(kmlObject, {
                    boundsFallback: parent.find('li').length < 1000,
                    aspectRatio: aspectRatio
                });
            }
            $(that).trigger('dblclick', [node, kmlObject]);            
        });
        
        var doubleClicking = false;
        
        google.earth.addEventListener(ge.getGlobe(),'dblclick',function(e, d){
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
        
        // fix for jquery 1.4.2 compatibility. See http://forum.jquery.com/topic/javascript-error-when-unbinding-a-custom-event-using-jquery-1-4-2
        that.removeEventListener = that.detachEvent = function(){};

        var privilegedApi = {
            opts: opts,
            docs: docs
        };
        
        kmltreeManager.register(that, privilegedApi);
        return that;
    };
})();var enableGoogleLayersControl = (function(){

    var setVisibility = function(kmlObject, toggle, ge){
        var id = kmlObject.getId();
        if(id && id.match(/^LAYER/)){
            ge.getLayerRoot().enableLayerById(ge[id], toggle);
        }else{
            var options = ge.getOptions();
            switch(id){
                case 'SUN':
                    ge.getSun().setVisibility(toggle);
                    break;
                case 'NAVIGATION_CONTROLS':
                    var vis = ge.VISIBILITY_SHOW
                    if(!toggle){
                        vis = ge.VISIBILITY_HIDE
                    }
                    ge.getNavigationControl().setVisibility(vis);
                    break;
                case 'STATUS_BAR':
                    options.setStatusBarVisibility(toggle);
                    break;
                case 'OVERVIEW_MAP':
                    options.setOverviewMapVisibility(toggle);
                    break;
                case 'SCALE_LEGEND':
                    options.setScaleLegendVisibility(toggle);
                    break;
                case 'ATMOSPHERE':
                    options.setAtmosphereVisibility(toggle);
                    break;
                case 'HISTORICAL_IMAGERY':
                    ge.getTime().setHistoricalImageryEnabled(toggle);
                    break;
                case 'GRID':
                    options.setGridVisibility(toggle);
                    break;
                case 'STREET_VIEW':
                    ge.getNavigationControl().setStreetViewEnabled(toggle); 
            }
        }
    };

    return function(tree, ge){
        if(!tree || !ge){
            alert('Must call enableGoogleLayersControl with both tree'+
                ' and ge options!');
        }
        
        $(tree).bind('toggleItem', function(e, node, toggle, kmlObject){
            setVisibility(kmlObject, toggle, ge);
        });
        
        $(tree).bind('kmlLoaded', function(e, kmlObject){
            var list = kmlObject.getFeatures().getChildNodes();
            var length = list.getLength();
            for(var i = 0; i < length; i++){
                var item = list.item(i);
                setVisibility(item, item.getVisibility(), ge);
            }
        });
        
    }
})();