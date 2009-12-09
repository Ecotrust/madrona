(function(){
    // earthTest and earthAsyncTest
    // ============================
    // 
    // Use earthTest rather than QUnit::test for testing functionality that 
    // requires an instance of the Google Earth Plugin and/or the 
    // earth-api-utility-library.
    // 
    // Test functions will be called with two arguments, the plugin instance and
    // the utility library. Here is an example:
    // 
    //     earthTest('Test grid', 1, function(ge, gex){
    //         equals(ge.getOptions().getGridVisibility(), true, 'Grid should be visible.');
    //     });
    //     
    // For asynchronous tests, use earthAsyncTest as a replacement for
    // QUnit::testAsync:
    // 
    //     earthAsyncTest('Test parse kml', 1, function(ge, gex){
    //         $.get('/path/to/kml', function(data){
    //             var doc = ge.parseKml(data);
    //             equals(doc.getName(), 'My Name');
    //             start();
    //         });
    //     });
    // 
    // When testing using asynchronous calls and the Earth Plugin it is
    // important to fill in the `expected` argument. Otherwise, it can be
    // difficult to pin down which test caused an error.
    // 
    // See the following for more information on using QUnit:
    // http://docs.jquery.com/QUnit
    window.earthTest = function(name, expected, callback, async){
        if ( arguments.length === 2 ) {
        	callback = expected;
        	expected = 0;
        }

        var new_function = function(){
            if(ge && gex){
                if(!async){
                    start();                            
                }
                callback(ge, gex);
            }else{
                initializePlugin(function(){
                    if(!async){
                        start();                            
                    }
                    callback(ge, gex);                        
                });
            }
        }
        asyncTest(name, expected, new_function);
    }

    window.earthAsyncTest = function(name, expected, callback){
        if ( arguments.length === 2 ) {
        	callback = expected;
        	expected = 0;
        }
        earthTest(name, expected, callback, true);
    }
    
    
    var ge;
    var gex;

    function initializePlugin(callback){
        console.warn('initialize Plugin');
        google.earth.createInstance('map3d', function(plugin){
            ge = plugin;
            gex = new GEarthExtensions(ge);
            callback();
        }, googleEarthFailureCallback);
    }

    module('Custom test cases');

    var reference_to_first_google_earth_instance;

    earthAsyncTest('earthAsyncTest works', 2, function(ge, gex){
        ok(typeof ge.parseKml === 'function', 'Google Earth Plugin initialized');
        reference_to_first_google_earth_instance = ge;
        setTimeout(function(){
            start();
            ok(true === true, 'Additional asynchronous events can be run');
        }, 1000);
    });

    earthTest('only loads once', 1, function(ge, gex){
        ok(ge === reference_to_first_google_earth_instance, 
            'Google Earth Plugin should initialize only once.');
    });

    function googleEarthFailureCallback(){
        alert('failed to load google earth plugin.');
    }

})();