module('rest');

earthTest("create client", function(ge, gex){
    var client = lingcod.rest.client(gex, {});
    ok(typeof client.parseDocument === 'function', 
        'Has parseDocument method');
});

lingcod.rest.testInterface = function(name, document_url, types){
    
    // provides the same api as lingcod.panel but for testing purposes rather 
    // than display.
    var testPanel = (function(){
                
        var that = {};
        that.closed = true;
        
        that.showContent = function(elements){
            var el = that.getEl();
            el.html('');
            el.append(elements);
            el.show();
            that.closed = false;
            $(that).trigger('show', that);
        }
        
        that.close = function(){
            var el = that.getEl();
            el.html('');
            el.hide();
            that.closed = true;
        }
        
        that.spin = function(message){
            
        }
        
        that.showError = function(title, message){
            
        }
        
        that.showUrl = function(url, options){
            // throw('what the fucking fuck!');
            var new_url = url;
            that.spin(options.load_msg || "Loading");
            $.ajax({
                url: url,
                method: 'GET',
                complete: function(response, status){
                    switch(response.status){
                        case 200:
                            that.showContent(response.responseText)
                            if(options && options.success){
                                options.success(response, status);
                                $(that).trigger('show', response, status);
                            }
                            // get content
                            // that.showContent
                            break;
                            
                        default:
                            that.showError('A Server Error Occured.', 
                                'Please try again.');
                                
                            if(options && options.error){
                                options.error(response, status);
                            }
                            $(that).trigger('error', response, status);
                    }
                }
            });
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
    
    module('rest interface[Must run whole test module!]: ' + name);
    
    var client;

    earthTest('client initialized', function(ge, gex){
        client = lingcod.rest.client(gex, testPanel);
        ok(typeof client.parseDocument === 'function', 
            'Has parseDocument method');
    });
    
    var configs;
    
    testLoggedInAsync("parseDocument", 5, function(){
        $.ajax({
            dataType: "text",
            error: function(request, status, error){
                ok(false, 'Could not fetch document: '+document_url+
                    ' , ' + status);
            },
            success: function(text, status){
                if(status !== 'success'){
                    ok(false, 'Could not fetch document: '+
                        document_url+' , ' + status);
                }else{
                    configs = client.parseDocument(text);
                    ok(configs, 'parseDocument returns a value.');
                    for(var model in types){
                        ok(configs[model], 
                            'Configuration present for '+model);
                        ok(configs[model].href, 
                            'href present in atom link for '+model);
                        ok(configs[model].title, 
                            'title present in atom link for '+model);
                        ok(configs[model].model, 
                            'model present in atom link for '+model);
                    }
                    start();
                }                
            },
            type: 'GET',
            url: document_url
        });
    }); 
    
    for(var model in types){
        var form_values = types[model]['form_values'];
        var invalid_form_values = types[model]['invalid_form_values']
        // Test that the form has been shown, then submit it and run the 
        // validation test
        var afterShow = function(e, p){
            $(testPanel).unbind('show', afterShow);
            var el = testPanel.getEl();
            ok(el.is(":visible"), 'panel should be shown.');
            equals(el.find('form').length, 1, 'Form should be present.');
            var form = el.find('form');
            fill_in_form(form, invalid_form_values);
            $(testPanel).bind('show', validationTest);
            form.submit();
        }
        
        var validationTest = function(e){
            $(testPanel).unbind('show', validationTest);
            var el = testPanel.getEl();
            ok(el.find('.errorlist').length > 0, 
                'Should show user validation errors.');
            var form = el.find('form');
            fill_in_form(form, form_values);
            form.submit();
        }
        
        var fill_in_form = function(form, values){
            for(var key in values){
                var id = '#id_'+key;
                form.find(id).val(values[key]);
            }            
        }
        
        var created_object_location;
        // startup these tests
        asyncTest("create - part 1 "+model, 5, function(){
            $(testPanel).bind('show', afterShow);
            client.create(configs[model], {
                success: function(location){
                    ok(location, 'Should pass the function a location.');
                    created_object_location = location;
                    ok(testPanel.closed, 'Panel should now be closed.');
                    start();
                }
            });
        });
        
        asyncTest('create - part 2 '+model, 2, function(){
            $.ajax({
                dataType: "text",
                error: function(request, status, error){
                    ok(false, 'Could not fetch document: '+
                        document_url+' , ' + status);
                },
                success: function(text, status){
                    if(status !== 'success'){
                        ok(false, 'Could not fetch document: '+
                            document_url+' , ' + status);
                    }else{
                        var resource = client.findResourceInString(
                            created_object_location, text);
                        ok(resource, 'Object found within listing document');
                        equals(form_values.name, resource.find('name').text(), 
                            'Correctly named.');
                        start();
                    }                
                },
                type: 'GET',
                url: document_url
            });
        });
        
        var resourceConfig = false;
        var kmlResource = false;
        
        earthAsyncTest('parseResource '+model, 8, function(ge, gex){
            $.ajax({
                dataType: "text",
                error: function(request, status, error){
                    ok(false, 'Could not fetch document: '+
                        document_url+' , ' + status);
                },
                success: function(text, status){
                    if(status !== 'success'){
                        ok(false, 'Could not fetch document: '+
                            document_url+' , ' + status);
                    }else{
                        var kmlObject = ge.parseKml(text);
                        ok(kmlObject, 'Got and parsed kml document.');
                        var resource = client.findResource(
                            created_object_location, kmlObject);
                        ok(resource, 'Found created resource.');
                        kmlResource = resource;
                        equals(resource.getName(), form_values.name, 
                            'Has correct name.');
                        resourceConfig = client.parseResource(resource);
                        if(resourceConfig){
                            equals(resourceConfig['location'], 
                                client.getPath(created_object_location),
                                'Has a link to the object representation.');

                            ok(resourceConfig['form_link'], 
                                'Has a link to the object update form.');

                            ok(resourceConfig['form_title'], 
                                'Form has a title.');

                            equals(resourceConfig['title'], form_values.name, 
                                'Has a name.');
                        
                            equals(resourceConfig['model'], model, 
                                'Model listed correctly');
                        }else{
                            ok(false, 'parseResource did not return result');
                        }

                        start();
                    }                
                },
                type: 'GET',
                url: document_url
            });
        });
        
        earthAsyncTest('show from config '+model, 2, function(ge, gex){
            client.show(resourceConfig, {
                success: function(){
                    ok(testPanel.getEl().is(':visible'), 
                        'Panel should be shown');
                    equals(testPanel.getEl().find(
                        'h1:contains('+form_values.name+')').length, 1, 
                        'Has header of named object.');
                    testPanel.close();
                    start();
                }
            });
        });
        
        earthAsyncTest('show from kmlFeatureObject '+model, function(ge, gex){
            client.show(kmlResource, {
                success: function(){
                    ok(testPanel.getEl().is(':visible'), 
                        'Panel should be shown');
                    equals(testPanel.getEl().find(
                        'h1:contains('+form_values.name+')').length, 1, 
                        'Has header of named object.');
                    testPanel.close();
                    start();
                }
            });            
        });

        
        earthAsyncTest('show error handled '+model, function(ge, gex){
            // modify resourceConfig
            // client.show(resourceConfig);
            // handle error
            start();
        });
        
        var updateFormShown = function(){
            $(testPanel).unbind('show', updateFormShown);
            var el = testPanel.getEl();
            equals(form_values.name, el.find(':input[name=name]').val(),
                'Form shown with correct name.');
            var form = el.find('form');
            fill_in_form(form, invalid_form_values);
            $(testPanel).bind('show', validationError);
            el.find('form').submit();
        }
        
        var edited_form_values;
        
        var validationError = function(){
            $(testPanel).unbind('show', validationError);
            var el = testPanel.getEl();
            ok(el.find('.errorlist').length > 0, 
                'Should show user validation errors.');
            edited_form_values = jQuery.extend(true, {}, form_values);
            edited_form_values.name = 'Edited '+edited_form_values.name;
            var form = el.find('form');
            fill_in_form(form, edited_form_values);
            el.find('form').submit();
        }
                
        earthAsyncTest('update - part 1 '+model, function(ge, gex){
            $(testPanel).bind('show', updateFormShown);
            client.update(kmlResource, {
                success: function(location){
                    equals(resourceConfig.location, location, 
                        'Should pass the function a location.');
                    ok(testPanel.closed, 'Panel should now be closed.');
                    start();
                },
                error: function(title, msg){
                    ok(false, 'Update failed');
                    start();
                }
            });
        });
        
        earthAsyncTest('update - part 2 '+model, 2, function(ge, gex){
            $.ajax({
                cache: false,
                dataType: "text",
                error: function(request, status, error){
                    ok(false, 'Could not fetch document: '+
                        document_url+' , ' + status);
                },
                success: function(text, status){
                    if(status !== 'success'){
                        ok(false, 'Could not fetch document: '+
                            document_url+' , ' + status);
                    }else{
                        var resource = client.findResourceInString(
                            created_object_location, text);
                        ok(resource, 'Object found within listing document');
                        equals(edited_form_values.name, 
                            resource.find('name').text(), 'Correctly named.');
                        start();
                    }                
                },
                type: 'GET',
                url: document_url
            });
        });
        
        earthAsyncTest('delete - part 1 '+model, function(ge, gex){
            client.destroy(kmlResource, {
                confirm: false,
                success: function(location){
                    equals(resourceConfig.location, location,
                        'Location provided to success function.');
                    start();
                },
                error: function(){
                    ok(false, 'Error occured.');
                    start();
                },
                cancel: function(){
                    ok(false, 'error: `cancel` should not be called.');                    
                    start();
                }
            });
        });
        
        earthAsyncTest('delete - part 2 '+model, 1, function(ge, gex){
            $.ajax({
                cache: false,
                url: resourceConfig.location,
                type: 'GET',
                complete: function(response, status){
                    equals(404, response.status, 
                        'Resource should no longer exist.');
                    start();
                }
            });
        });
        
        earthAsyncTest('delete - part 3 '+model, function(ge, gex){
            $.ajax({
                cache: false,
                dataType: "text",
                error: function(request, status, error){
                    ok(false, 'Could not fetch document: '+
                        document_url+' , ' + status);
                },
                success: function(text, status){
                    if(status !== 'success'){
                        ok(false, 'Could not fetch document: '+
                            document_url+' , ' + status);
                    }else{
                        var resource = client.findResourceInString(
                            created_object_location, text);
                        equals(resource, false, 
                            'Should no longer find in kml listing service.');
                        start();
                    }
                },
                type: 'GET',
                url: document_url
            });
        });
    }
};