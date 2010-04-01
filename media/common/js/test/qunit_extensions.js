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
        var map = $(document.body).append('<div id="map3d"></div>');
        $('#map3d').css({width:'400', height: '200', 'position': 'absolute', 'left': '-400px'});
        google.earth.createInstance('map3d', function(plugin){
            ge = plugin;
            gex = new GEarthExtensions(ge);
            callback();
        }, googleEarthFailureCallback);
    }

    module('Custom Earth Test Cases');

    var reference_to_first_google_earth_instance;

    earthAsyncTest('earthAsyncTest works', 2, function(ge, gex){
        ok(typeof ge === 'object', 'Google Earth Plugin initialized');
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
    
    var DEFAULT_USERNAME = 'integration_tester';
    var DEFAULT_PASSWORD = 'password';
    var LOGIN = '/accounts/login/';
    var LOGOUT = '/accounts/logout/';
        
    function login(username, password, callback){
        $.post(LOGIN, {username: username, password: password}, function(data, textStatus){
            if(textStatus === "success"){
                if(data.match('label for="id_username"')){
                    callback('username and password not valid.');
                }else{
                    callback(false);
                }
            }else{
                callback(textStatus);
            }
        }, "html");
    }
    
    
    // testLoggedIn, testLoggedInAsync, testLoggedOut, and testLoggedOutAsync
    // ======================================================================
    // 
    // These methods expose a way to develop tests which require first that a 
    // default user or specified user is logged in or out before the starting the
    // test.
    // 
    // Examples:
    //     
    // // optional `expected` argument specified.
    //     testLoggedIn('my test', 1, function(){
    //         ok([some condition], 'My user can do ...');
    //     });
    //     
    // // specify a different username and password
    //     testLoggedIn('my test', 'myusername', 'pword', function(){
    //         ok([some condition], 'myusername can do ...');
    //     });
    //     
    // // asynchronous tests can also be run
    //     testLoggedInAsync('my test', 2, function(){
    //         ok([some condition], 'My user can do ...');
    //         setTimeout(function(){
    //             ok(true, 'asynchronous testing works.');
    //             start();
    //         }, 100);
    //     });
    //     
    // // If you have a test that must be run with an unauthenticated user:
    //     testLoggedOut('my test', 1, function(){
    //         equals(can_do, false, 'user must be logged in to do x.');
    //     });
    // 
    window.testLoggedIn = function(name, expected, username, pword, callback){
        var options;
        if(arguments.length !== 1){
            options = parseArguments(arguments);
        }else{
            options = name;
        }
        var new_function = function(){
            login(options['username'], options['pword'], function(error){
                if(error){
                    ok(false, 'Could not login '+options['username'] + '. '+error);
                    start();
                }else{
                    options['callback'](options['username']);
                    if(!options['async']){
                        start();
                    }
                }
            });
        }
        asyncTest(options['name'], options['expected'], new_function);
    }
    
    window.testLoggedInAsync = function(name, expected, username, pword, callback){
        var options = parseArguments(arguments);
        options['async'] = true;
        window.testLoggedIn(options);
    }
    
    
    function logout(callback){
        $.get(LOGOUT, function(data, textStatus){
            if(textStatus === "success"){
                callback(false);
            }else{
                callback(textStatus);
            }
        });
    }
    
    window.testLoggedOut = function(name, expected, callback, async){
        if ( arguments.length === 2 ) {
        	callback = expected;
        	expected = 0;
        }
        var new_function = function(){
            logout(function(error){
                if(error){
                    ok(false, 'Could not logout');
                    start();
                }else{
                    callback();
                    if(!async){
                        start();
                    }
                }
            });
        }
        asyncTest(name, expected, new_function);
    }
    
    window.testLoggedOutAsync = function(name, expected, callback){
        if ( arguments.length === 2 ) {
        	callback = expected;
        	expected = 0;
        }
        window.testLoggedOut(name, expected, callback, true);
    }
    
    function parseArguments(args){
        var options = {
            username: DEFAULT_USERNAME,
            pword: DEFAULT_PASSWORD,
            expected: 0,
            async: false,
            name: args[0]
        };
        // if (arguments.length === 1 && typeof name === 'object'){
        //     callback = name['callback'];
        //     pword = name['pword'] || 'password';
        //     username = name['username'] || 'integration_tester';
        //     expected = name['expected'] || 0;
        //     async = name['async'];
        //     name = name['name'];
        // }else{
        if ( args.length === 2 ) {
            options['callback'] = args[1];
        }
        if ( args.length === 3 ) {
        	options['callback'] = args[2];
            options['expected'] = args[1];
        }
        if (args.length === 4) {
            options['callback'] = args[3];
            options['pword'] = args[2];
            options['username'] = args[1];
        }
        if (args.length === 5) {
            options['callback'] = args[4];
            options['pword'] = args[3];
            options['username'] = args[2];
            options['expected'] = args[1];
        }            
        return options;
    }
    
    $(document).ready(function(){
        if(typeof window.skipAuthTests === 'undefined' || window.skipAuthTests === false){
            module('Custom Login-Related Test Cases');

            test('options parsed correctly', function(){
                var callback = function(){};
                // with username and password
                // no expected
                var options = parseArguments(['mytest', 'myusername', 'mypassword', callback]);
                equals(options['name'], 'mytest', '`name` correctly set.');
                equals(options['expected'], 0, '`expected` loaded from defaults');
                equals(options['username'], 'myusername', '`username` correctly set.');
                equals(options['pword'], 'mypassword', '`pword` correctly set.');
                equals(options['callback'], callback, '`callback` correctly set.');
                equals(options['async'], false, '`async` correctly set.');

                // with expected
                var options = parseArguments(['mytest', 8, 'myusername', 'mypassword', callback]);
                equals(options['name'], 'mytest', '`name` correctly set.');
                equals(options['expected'], 8, '`expected` correctly set.');
                equals(options['username'], 'myusername', '`username` correctly set.');
                equals(options['pword'], 'mypassword', '`pword` correctly set.');
                equals(options['callback'], callback, '`callback` correctly set.');

                // without username and password
                // no expected
                var options = parseArguments(['mytest', callback]);
                equals(options['name'], 'mytest', '`name` correctly set.');
                equals(options['expected'], 0, '`expected` loaded from defaults');
                equals(options['username'], DEFAULT_USERNAME, '`username` loaded from default.');
                equals(options['pword'], DEFAULT_PASSWORD, '`pword` loaded from default.');
                equals(options['callback'], callback, '`callback` correctly set.');
                equals(options['async'], false, '`async` correctly set.');

                // with expected
                var options = parseArguments(['mytest', 4, callback]);
                equals(options['name'], 'mytest', '`name` correctly set.');
                equals(options['expected'], 4, '`expected` set correctly.');
                equals(options['username'], DEFAULT_USERNAME, '`username` loaded from default.');
                equals(options['pword'], DEFAULT_PASSWORD, '`pword` loaded from default.');
                equals(options['callback'], callback, '`callback` correctly set.');
                equals(options['async'], false, '`async` correctly set.');

            });

            testLoggedIn('testLoggedIn - username and password, expected specified', 1, DEFAULT_USERNAME, DEFAULT_PASSWORD, function(username){
                equals(username, DEFAULT_USERNAME);
            });

            testLoggedInAsync('testLoggedInAsync - username and password, expected specified', 2, DEFAULT_USERNAME, DEFAULT_PASSWORD, function(username){
                equals(username, DEFAULT_USERNAME);
                setTimeout(function(){
                    ok(true, 'asynchronous testing works.');
                    start();
                }, 100);
            });

            testLoggedIn('testLoggedIn - username and password, no expected argument', DEFAULT_USERNAME, DEFAULT_PASSWORD, function(username){
                equals(username, DEFAULT_USERNAME);
            });

            testLoggedInAsync('testLoggedInAsync - username and password, no expected argument', DEFAULT_USERNAME, DEFAULT_PASSWORD, function(username){
                equals(username, DEFAULT_USERNAME);
                setTimeout(function(){
                    ok(true, 'asynchronous testing works.');
                    start();
                }, 100);
            });

            testLoggedIn('testLoggedIn - default user, expected specified', 1, DEFAULT_USERNAME, DEFAULT_PASSWORD, function(username){
                equals(username, DEFAULT_USERNAME);
            });

            testLoggedInAsync('testLoggedInAsync - default user, expected specified', 2, function(username){
                equals(username, DEFAULT_USERNAME);
                setTimeout(function(){
                    ok(true, 'asynchronous testing works.');
                    start();
                }, 100);
            });

            testLoggedIn('testLoggedIn - default user, no expected argument', function(username){
                equals(username, DEFAULT_USERNAME);
            });

            testLoggedInAsync('testLoggedInAsync - default user, no expected argument', function(username){
                equals(username, DEFAULT_USERNAME);
                setTimeout(function(){
                    ok(true, 'asynchronous testing works.');
                    start();
                }, 100);
            });

            testLoggedOut('testLoggedOut - expected argument', 1, function(){
                ok(true, 'testLoggedOut works with expected argument.');
            });

            testLoggedOutAsync('testLoggedOutAsync - expected argument', 2, function(){
                ok(true, 'testLoggedOut works with expected argument.');
                setTimeout(function(){
                    ok(true, 'asynchronous testing works.');
                    start();
                }, 100);
            });

            testLoggedOut('testLoggedOut - expected argument', function(){
                ok(true, 'testLoggedOut works without expected.');
            });

            testLoggedOutAsync('testLoggedOutAsync - expected argument', function(){
                ok(true, 'testLoggedOut works without expected.');
                setTimeout(function(){
                    ok(true, 'asynchronous testing works.');
                    start();
                }, 100);
            });
            // testing
                // with username and password
                    // no expected
                    // with expected
                // without username and password
                    // with expected
                    // without expected
        }
    });
})();