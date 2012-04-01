/**
 * jQuery Callback
 * @author Alberto Bottarini <alberto.bottarini@gmail.com
 * @version 1.1
 * @homepage http://code.google.com/p/jquerycallback
 *
 * jQuery-callback permits jQuery developer to have a real control to their callback functions. 
 * With this plugin you can set custom parameters and custom scope to each callback defined in your script. 
 */
 
(function(jq) {
	var asArray = function(a) {
		return Array.prototype.slice.call(a,0);
	}
	jq.delegate = function(func, scope, params, overwriteDefault) {
		if(!$.isArray(params)) params = [params];
		return function() {
			if(!overwriteDefault) func.apply(scope, asArray(arguments).concat(params));
			else func.apply(scope, args);
		}
	}	
	jq.callback = function(func, params, overwriteDefault) {
		return jq.delegate(func, this, params, overwriteDefault);
	}
})(jQuery);
