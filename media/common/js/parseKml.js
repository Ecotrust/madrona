// JQuery's $(...) method can't reliably produce a DOM for arbitrary xml. This
// function creates a DOM using the browser's built-in methods, then creates
// a jQuery object from that. It also adds a findLinks() function to find atom
// links within kml.
lingcod.parseKml = (function(){

    function decorate(dom){
        var jq = jQuery(dom);
        jq.findLinks = function(opts){
            var query = '[nodeName=atom:link]';
            for(var key in opts){
                query = query+'['+key+'='+opts[key]+']';
            }
            return jq.find(query);
        }
        return jq;
    }

    return function(kml){
        if( window.ActiveXObject && window.GetObject ) { 
            var dom = new ActiveXObject( 'Microsoft.XMLDOM' ); 
            dom.loadXML(kml); 
            return decorate(dom);
        } 
        if( window.DOMParser ) {
            return decorate(new DOMParser().parseFromString( kml, 'text/xml' ));
        }
        throw new Error( 'No XML parser available' );
    }
})();