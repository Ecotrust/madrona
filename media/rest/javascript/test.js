module('rest');

earthTest("create client", function(ge, gex){
    var client = lingcod.rest.client(gex);
    ok(typeof client.parseDocument === 'function', 'Has parseDocument method');
});

lingcod.rest.testInterface = function(name, document_url){
    
    module('rest interface: ' + name);

    earthTest('client initialized', function(ge, gex){
        console.log(ge, gex);
        var client = lingcod.rest.client(gex);
        ok(typeof client.parseDocument === 'function', 'Has parseDocument method');
    });
    
    test("parseDocument", function(){
    });

    test("parseResource", function(){

    });

    test("create", function(){

    });

    test("update", function(){

    });

    test("delete", function(){

    });

    test("show", function(){

    });
};

if(!REST_INTERFACES){
    var REST_INTERFACES = {};
}

for(var key in REST_INTERFACES){
    lingcod.rest.testInterface(key, REST_INTERFACES[key]);
}