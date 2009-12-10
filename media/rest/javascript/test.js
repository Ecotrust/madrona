module('rest');

earthTest("create client", function(ge, gex){
    var client = lingcod.rest.client(gex, {});
    ok(typeof client.parseDocument === 'function', 'Has parseDocument method');
});

lingcod.rest.testInterface = function(name, document_url, types){
    
    module('rest interface[Must run whole test module!]: ' + name);
    
    var client;

    earthTest('client initialized', function(ge, gex){
        client = lingcod.rest.client(gex, testPanel);
        ok(typeof client.parseDocument === 'function', 'Has parseDocument method');
    });
    
    var configs;
    
    testLoggedInAsync("parseDocument", 5, function(){
        $.ajax({
            dataType: "text",
            error: function(request, status, error){
                ok(false, 'Could not fetch document: '+document_url+' , ' + status);
            },
            success: function(text, status){
                if(status !== 'success'){
                    ok(false, 'Could not fetch document: '+document_url+' , ' + status);
                }else{
                    configs = client.parseDocument(text);
                    ok(configs, 'parseDocument returns a value.');
                    for(var model in types){
                        ok(configs[model], 'Configuration present for '+model);
                        ok(configs[model].href, 'href present in atom link for '+model);
                        ok(configs[model].title, 'title present in atom link for '+model);
                        ok(configs[model].model, 'model present in atom link for '+model);
                    }
                    start();
                }                
            },
            type: 'GET',
            url: document_url
        });
    });
    
    // provides the same api as lingcod.panel but for testing purposes rather 
    // than display.
    var testPanel = (function(){
                
        var that = {};
        
        that.showContent = function(elements){
            var el = that.getEl();
            el.append(elements);
            el.show();
            $(that).trigger('show', that);
        }
        
        that.close = function(){
            
        }
        
        that.spin = function(message){
            
        }
        
        that.showError = function(title, message){
            
        }
        
        // Methods needed for test management        
        that.destroy = function(){
            that.getEl().remove();
        }
        
        that.getEl = function(){
            return $('#testpanel');
        }
                
        return that;
    })();
        
    
    for(var model in types){        
        test("create "+model, function(){
            client.create(configs[model]);
            ok(testPanel.getEl().is(":visible"), 'panel should be shown.');
            // now we need to check that validation errors are handled gracefully.
            // fill out form values
            // submit
            // how do we know when it is done? - event listeners - show
            // 
        });
        
    }
    

    test("parseResource", function(){
        
    });

    test("update", function(){

    });

    test("delete", function(){

    });

    test("show", function(){

    });
};