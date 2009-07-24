// Modification of GEarthExtension function from:
// http://code.google.com/p/earth-api-utility-library/source/browse/trunk/extensions/src/util/shortcuts.js
// This modification has been submitted as a patch
// http://code.google.com/p/earth-api-utility-library/issues/detail?id=10

/**
 * Simply loads and shows the given KML URL in the Google Earth Plugin instance.
 * @param {String} url The URL of the KML content to show.
 * @param {Object} [options] KML display options.
 * @param {Boolean} [options.cacheBuster] Enforce freshly downloading the KML
 *       by introducing a cache-busting query parameter.
 */
GEarthExtensions.prototype.util.displayKml = function(url, options) {
    options = options || {};
    if (options.cacheBuster) {
        url += (url.match(/\?/) ? '&' : '?') + '_cacheBuster=' +
            Number(new Date()).toString();
    }
    // TODO: option to choose network link or fetchKml
    var me = this;
    google.earth.fetchKml(me.pluginInstance, url, function(kmlObject) {
        if (kmlObject) {
            me.pluginInstance.getFeatures().appendChild(kmlObject);
            if(options.flyToView){
                var la = kmlObject.getAbstractView();
                me.pluginInstance.getView().setAbstractView(la);
            }
        }
    });
};