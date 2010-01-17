mlpa.prepareForm = function(panel){
    var native_select = $('#id_designation');
    native_select.hide();
    var select = new goog.ui.Select();
    
    var uses = mlpa.uses({
        panel: panel
    });

    native_select.parent().append('<p class="help_text">Your choice of designation affects what allowed uses you can assign to your MPA. For more information, see the <a href="http://www.dfg.ca.gov/mlpa/defs.asp#system">Department of Fish and Game website</a>.</p>');

    // Add all the options from the form widget to the goog select widget.
    var designation_set = false;
    native_select.find('option').each(function(){
        var option = new goog.ui.Option($(this).text());
        option.id_value = $(this).val();
        select.addItem(option);
        // If the form already has a selected value use it.
        if($(this).attr('selected')){
            select.setValue($(this).text());
            if(option.id_value === ''){
                option.id_value = null;
            }
            uses.setDesignation(option.id_value);
            designation_set = option.id_value;
        }
    });
    
    select.render(native_select.parent()[0]);
    native_select.parent().append('<p class="help_text designation_allowed_uses_note"></p>')    
    uses.setUsesAllowedText(designation_set);

    // Fired whenever the selected value of the goog widget is changed.
    goog.events.listen(select, goog.ui.Component.EventType.ACTION, function(e) {
        // select the item chosen in the hidden native form element.
        var designation_id = e.target.getSelectedItem().id_value;
        if(!designation_id){
            native_select.val(designation_id);
            uses.setDesignation(null);            
        }else{
            var incompatible = uses.getIncompatibleWithDesignation(designation_id);
            if(incompatible.length !== 0){
                if(!confirm('Some of your allowed uses must be removed to change to this designation. Are you sure you would like to change the designation?')){
                    return;
                }
            }            
            native_select.val(designation_id);
            uses.setDesignation(designation_id, incompatible);
        }
    });
        
    var cleanup = function(){
        uses.destroy();
        select.dispose();
        $(panel).unbind('panelclose', cleanup);
        $(panel).unbind('panelhide', cleanup);
    };
    
    $(panel).bind('panelclose', cleanup);
    $(panel).bind('panelhide', cleanup);
}

mlpa.uses = function(options){
    var that = {};
            
    // PUBLIC METHODS
    
    var getSelected = function(){
        var selected = [];
        native_select.find('option:selected').each(function(){
            var id = $(this).val();
            selected.push(data.allowed_uses[id]);
        });
        return selected;
    };
    
    that.getSelected = getSelected;
    
    var disableMenus = function(){
        forEachMenu(function(menu){
            menu.setEnabled(false);
        });
    }
        
    var getChoices = function(){
        var choices = {};
        for(var i=0; i<select_menus.length; i++){
            var menu = select_menus[i];
            var selected = menu.getSelectedItem();
            if(selected.choice_data){
                choices[menu.attr_id] = selected.choice_data.pk;
            }else{
                choices[menu.attr_id] = null;
            }
        }
        return choices;
    }
    
    that.getChoices = getChoices;
    
    var getIncompatibleWithDesignation = function(designation_id){
        var selected = getSelected();
        var purposes = getAllPurposes(designation_id);
        var disallowed = getDisallowedPurposes(designation_id);
        if(purposes.length === 0){
            return selected;
        }else{
            var notvalid = [];
            for(var i = 0; i<selected.length; i++){
                var item = selected[i];
                for(var j=0;j<disallowed.length;j++){
                    var purpose = disallowed[j];
                    if(purpose.pk === item['purpose']){
                        notvalid.push(item);
                    }
                }
            }
            return notvalid;
        }
    }
    
    that.getIncompatibleWithDesignation = getIncompatibleWithDesignation;
    
    var clearMenus = function(){
        forEachMenu(function(menu){
            menu.setSelectedIndex(0);
            forEachOption(menu, function(option){
                option.setEnabled(true);
            });
        });
        if(that.designation_id){
            setAllowedPurposes(getAllowedPurposes(that.designation_id));
        }
    }

    that.clearMenus = clearMenus;
    
    var find = function(attributes){
        // remove keys with blank values
        for(var key in attributes){
            if(attributes[key] === false || attributes[key] === null){
                delete attributes[key];
            }
        }
        var found = [];
        for(var attr in data.allowed_uses){
            var item = data.allowed_uses[attr];
            if(match(item, attributes)){
                found.push(item);
            }
        }
        return found;
    }
    
    that.find = find;
    
    var destroy = function(){
        forEachMenu(function(menu){
            menu.dispose();
        });   
    };
    
    that.destroy = destroy;
    
    var setDesignation = function(designation_id, incompatible_uses){
        incompatible_uses = incompatible_uses || [];
        that.designation_id = designation_id;
        if(that.designation_id === null){
            setAllowedPurposes(getAllPurposes());
            setUsesAllowedText(false);
        }else{
            // remove incompatible uses
            for(var i=0; i<incompatible_uses.length;i++){
                deselect(incompatible_uses[i].pk);
            }
            
            var allowed = getAllowedPurposes(that.designation_id);
            setAllowedPurposes(allowed);
            setUsesAllowedText(that.designation_id);            
        }
    }
    
    var setUsesAllowedText = function(designation_id){
        if(designation_id){
            var allowed = getAllowedPurposes(designation_id);
            var purposes = getAllPurposes();
            if(allowed.length === 0){
                $('.designation_allowed_uses_note').html('Allowed uses cannot be added to an MPA of this designation type.');
            }else if(allowed.length === purposes.length){
                $('.designation_allowed_uses_note').html('Any type of allowed use can be added to an MPA of this designation.');
            }else if(allowed.length === 1){
                $('.designation_allowed_uses_note').html('MPAs with this designation can only have '+allowed[0].name+' allowed uses.');
            }else{
                // NOT SUPPORTED YET!!!!!!!!!
            }            
        }else{
            $('.designation_allowed_uses_note').html('');            
        }
    }
    
    that.setUsesAllowedText = setUsesAllowedText;
    
    that.setDesignation = setDesignation
    
    // PRIVATE METHODS
    
    var buildSelect = function(container, options, name){
        var select = new goog.ui.Select();
        var option = new goog.ui.Option('choose a '+name);
        select.attr_id = name;
        option.choice_data = false;
        select.addItem(option);
        for(var k in options){
            var choice = options[k];
            var option = new goog.ui.Option(choice.name);
            option.choice_data = choice;
            choice.option = option;
            select.addItem(option);
        }
        select.setSelectedIndex(0);
        select.setScrollOnOverflow(true);
        select.render(container);
        return select;
    }
    
    // Given a menu, it will disable any menu options that aren't compatible
    // with choices specified in each other menu.
    var updateDisabledOptions = function(menu, choices){
        var newChoices = jQuery.extend(true, {}, choices);
        // remove the menu's own choice from the field. Otherwise, if option A
        // is chosen and you want to change it to option B, that won't be 
        // possible because it is incompatible with option A in that same menu
        delete newChoices[menu.attr_id];
        var uses = find(newChoices);
        // disable all options except the one selected
        forEachOption(menu, function(option){
            if(option.choice_data){ // not a header, ie "choose a target"
                option.setEnabled(
                    shouldEnableOption(option, menu.attr_id, uses)
                );
            }            
        });
    }
    
    // given a list of valid uses, return whether the option value is in 
    // those uses.
    var shouldEnableOption = function(option, attribute, uses){
        for(var k=0;k<uses.length;k++){
            if(uses[k][attribute] === option.choice_data.pk){
                return true;
            }
        }
        return false;
    }
    
    var onSelectChange = function(e){
        var choices = getChoices();
        var select = e.target;
        for(var i=0; i<select_menus.length; i++){
            // don't update the menu that was just acted on
            if(select !== select_menus[i]){
                updateDisabledOptions(select_menus[i], choices);
            }
        }
    }
    
    var setAllowedPurposes = function(allowed_purposes){
        var allPurposes = getAllPurposes();
        if(allowed_purposes.length === allPurposes.length){
            enableAllOptions(purpose_select);
            selectIndexAndTrigger(purpose_select, 0);
            enableMenus();            
        }else if(allowed_purposes.length === 0){
            // no valid purposes, so no allowed uses applicable
            disableMenus();            
        }else if(allowed_purposes.length === 1){
            // only one allowed purpose. Select the only valid choice and
            // disable the dropdown.
            enableMenus();
            selectItemAndTrigger(purpose_select, allowed_purposes[0].option);
            purpose_select.setEnabled(false);            
        }else if(allowed_purposes.length < allPurposes.length){
            // THIS BLOCK HASN'T BEEN TESTED YET BECAUSE SO FOR THE MLPA
            // ONLY HAS TWO ALLOWED PURPOSES SO IT ISN'T NEEDED!!!!!!!!!!!
            
            // deactivate all invalid purposes
            enableMenus();
            forEachOption(purpose_select, function(option){
                var enable = false;
                if(option.choice_data === false){
                    // is the 'choose one...' option
                    enable = true;
                }else{
                    for(var i=0;i<allowed_purposes.length; i++){
                        var purpose = allowed_purposes[i];
                        if(option.choice_data.pk === purpose.pk){
                            enable = true;
                        }
                    }                        
                }
                option.setEnabled(enable);
            });
            selectIndexAndTrigger(purpose_select, 0);            
        }else{
            // all purposes allowed.
            enableMenus();
            enableAllOptions(purpose_select);
            selectIndexAndTrigger(purpose_select, 0);            
        }
    }
    
    var selectIndexAndTrigger = function(menu, index){
        menu.setSelectedIndex(index);
        onSelectChange({target: menu});
    }
    
    var selectItemAndTrigger = function(menu, item){
        menu.setSelectedItem(item);
        onSelectChange({target: menu});
    }
    
    var enableAllOptions = function(menu){
        forEachOption(menu, function(option){
            option.setEnabled(true);
        });
    }
    
    var getAllPurposes = function(){
        var purposes = [];
        for(var key in data['purposes']){
            purposes.push(data['purposes'][key]);
        }
        return purposes;
    }
    
    var forEachMenu = function(callback){
        for(var i=0; i<select_menus.length;i++){
            callback(select_menus[i]);
        }
    }
    
    var forEachOption = function(menu, callback){
        var count = menu.getItemCount();
        for(var i=0;i<count;i++){
            callback(menu.getItemAt(i));
        }
    }
    
    var enableMenus = function(){
        forEachMenu(function(menu){
            menu.setEnabled(true);
        });
    }
    
    var getDisallowedPurposes = function(designation_id){
        var all = getAllPurposes();
        allowed = getAllowedPurposes(designation_id);
        var disallowed = [];
        for(var i=0;i<all.length;i++){
            var add = true;
            var purpose = all[i];
            for(var j=0;j<allowed.length;j++){
                if(purpose === allowed[j]){
                    add = false;
                }
            }
            if(add){
                disallowed.push(purpose);
            }
        }
        return disallowed;
    }
    
    var getAllowedPurposes = function(designation_id){
        var keys = data['designations-purposes'][designation_id];
        var purposes = [];
        if(keys){
            for(var i=0;i<keys.length;i++){
                purposes.push(data['purposes'][keys[i]]);
            }            
        }
        return purposes;
    }
            
    // select the use in the native form field
    var select = function(id){
        var option = native_select.find('option[value='+id+']');
        option.attr('selected', 'selected');
        addSelectedRow(id);
    }
    
    // add to ui
    var addSelectedRow = function(id){
        var non_showing = table.find('.none:visible');
        if(non_showing){
            non_showing.hide();
        }
        var use = data.allowed_uses[id];
        var row = $('<tr style="display:none;" class="use use_'+id+'"><td>'+
            data.targets[use.target].name+'</td><td>'+
            data.methods[use.method].name+'</td><td>'+
            data.purposes[use.purpose].name+
            '</td><td class="remove"><a href="#"><img src="'+
            lingcod.options.media_url+
            'common/images/silk/delete.png" width="16" height="16" /></a>'+
            '</td></tr>');
            
        row.data('use_id', id);
        table.find('tbody').append(row);
        row.fadeIn(500);
        row.find('.remove a').click(onRemoveClick);
    }
    
    // deselect the use in the native form field
    var deselect = function(id){
        var option = native_select.find('option[value='+id+']');
        option.attr('selected', false);
        removeSelectedRow(id);
    }
    
    // remove from ui
    var removeSelectedRow = function(id){
        var row = table.find('.use_'+id);
        row.fadeOut(500, function(){
            $(this).remove();
        });
        if(table.find('.use').length === 0){
            table.find('.none').show();
        }
    }
    
    var deselectAll = function(){
        var selected = getSelected();
        for(var i=0;i<selected.length;i++){
            var use = selected[i];
            deselect(use.pk);
        }
    }
    
    var match = function(item, attributes){
        for(var key in attributes){
            if(item[key] !== attributes[key]){
                return false;
            }
        }
        return item;
    }
    
    var onRemoveClick = function(){
        var id = $(this).parent().parent().data('use_id');
        deselect(id);
        return false;         
    }

    var data = JSON.parse($('#allowed_uses_json').text());

    var native_select = options.panel.getEl().find('#id_allowed_uses');
    native_select.hide();
    var table = native_select.parent().find('table.allowed_uses');
    
    var target_select = buildSelect(table.find('th.target')[0], 
        data['targets'], 'target');
    var method_select = buildSelect(table.find('th.method')[0], 
        data['methods'], 'method');
    var purpose_select = buildSelect(table.find('th.purpose')[0], 
        data['purposes'], 'purpose');
        
    var select_menus = [target_select, method_select, purpose_select];
    for(var i =0;i<select_menus.length;i++){
        goog.events.listen(select_menus[i], 
            goog.ui.Component.EventType.ACTION, onSelectChange);
    }
    
    table.find('.add a').click(function(){
        var uses = find(getChoices());
        if(uses.length > 1){
            alert('You must choose a target, method, and purpose to add a new allowed use. Use the dropdown menus to the left of the add button.');
            return;
        }
        var selected = getSelected();
        var use = uses[0];
        for(var i=0; i<selected.length; i++){
            if(selected[i].pk === use.pk){
                alert('You have already selected this allowed use.');
                return;
            }
        }
        select(use.pk);
        clearMenus();
        return false;
    });
    
    native_select.find('option:selected').each(function(){
        addSelectedRow($(this).val());
    });
    
    return that;
}