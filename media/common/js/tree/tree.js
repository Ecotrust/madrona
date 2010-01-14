lingcod.Tree = function(options){
    
    var defaults = {
        scrollEl: false,
        //matches google earth desktop behavior if set to false
        animate: false,
        selectToggles: false
    }
    
    this.options = $.extend({}, defaults, options);
    
    if(!this.options.element){
        throw('lingcod.Tree must be instanciated with an element option');
    }
    
    this.element = $(this.options.element);
    
    this.element.addClass('marinemap-tree');
    
    // Setup event listeners
    
    var self = this;
    var el = this.element; // shorthand form
    
    el.find('span.collapsible').live('click', function(event){
        event.preventDefault();
        // alert('collapsible click');
        var li = $(this).parent();
        var list = li.find('>ul');
        if(list.find('li').length == 0){
            list.html('<p class="no-items">No items.</p>');
        }else{
            list.find('p.no-items').remove();
        }
        li.toggleClass('open');
        var img = $(this).find('img');
        if($(this).find('img[src*=/media/common/images/arrow-right.png]').length != 0){
            img.attr('src', "/media/common/images/arrow-right.png");
        }else{
            img.attr('src', "/media/common/images/arrow-right.png");
        }
        return false;
    });
    
    el.find('li.marinemap-tree-item a').live('dblclick', function(event){
        if($(event.target).parent().hasClass('doubleclick')){
            $(self).trigger('itemDoubleClick', [$(event.target).parent(), event]);
        }
        event.preventDefault();
        return false;
    });
    
    // el.find('li a').live('contextmenu', function(event){
    //     var item = $(event.target).parent();
    //     if(item.hasClass('context')){
    //         $(self).trigger('itemContext', [event, item]);
    //     }
    //     event.preventDefault();
    //     return false;
    // });
    
    el.find('li.marinemap-tree-item a').live('click', function(event){
        if(event.button == 2){
            
        }else{
            var parent = $(event.target).parent();
            $(self).trigger('itemClick', [parent, event]);
            if(parent.hasClass('select')){
                var e = jQuery.Event("itemSelect");
                $(self).trigger(e, [parent]);
                if(!e.isDefaultPrevented()){
                    self.selectItem(parent);
                }
            }else{
                var e = jQuery.Event("itemSelect");
                $(self).trigger(e, [null, parent]);
                if(!e.isDefaultPrevented()){
                    self.clearSelection();
                }
            }
            event.preventDefault();
            return false;
        }
    });
    
    el.find('li span.collapsible, li span.collapsible a').live('contextmenu', function(event){
        event.preventDefault();
        return false;
    });
    
    el.find('li.marinemap-tree-item input[type=checkbox]').live('click', function(e){
        var element = $(this);
        var checked = element.attr('checked');
        var parent = element.parent();
        if(parent.hasClass('selected')){
            var e = jQuery.Event('itemSelect');
            $(self).trigger(e, [null, null]);
            if(!e.isDefaultPrevented()){
                self.clearSelection();
            }
        }
        var clickedData = [parent];
        var list = parent.find('>ul');
        if(list.length > 0){
            var clickedData = self._toggleCheckboxes(list, checked, clickedData);
        }
        
        parent.parents('li.toggle').each(function(){
            var element = $(this);
            if(checked == true){
                element.find(' > input[type=checkbox]').attr('checked', true);
                clickedData.push(element);
            }else{
                // if you cant find any child elements turned on
                if(element.find('> ul input[type=checkbox][checked=true]').length == 0){
                    element.find('> input[type=checkbox]').attr('checked', false);
                    clickedData.push(element);
                }
                if(element.hasClass('selected')){
                    self.clearSelection();
                    $(self).trigger('itemSelect', [null, null]);
                }
            }
        });
        $(self).trigger('itemToggle', [clickedData, checked]);
        if(checked == false){
            if(parent.find('li.selected').length > 0){
                parent.find('li.selected').removeClass('selected');
                var e = jQuery.Event("itemSelect");
                $(self).trigger(e, [null, null]);
            }
        }
    });
    
    return this;

};

lingcod.Tree.prototype.defaults = {
    classname: '',
    id: '',
    context: false,
    select: false,
    doubleclick: false,
    collapsible: false,
    toggle: false,
    icon: false,
    data: {},
    children: false,
    extra: '',
    snippet: false,
    checked: false,
    open: false,
    description: false
}

lingcod.Tree.prototype._template = tmpl([
    '<li class="',
    '<%= (context ? "context " : "") %>',
    '<%= (toggle ? "toggle " : "") %>',
    '<%= (select ? "select " : "unselectable ") %>',
    '<%= (doubleclick ? "doubleclick " : "") %>',
    '<%= (open ? "open " : "") %>',
    '<%= (toggle ? "toggle " : "") %>',
    '<%= (description ? "description " : "") %>',
    '<%= classname %> <%= id %> marinemap-tree-item',
    '">',
        '<% if(collapsible) { %>',
            '<span class="collapsible"><img src="/media/common/images/arrow-right.png" width="9" height="9" /></span>',
        '<% } %>',
        '<% if(toggle) { %>',
            '<input type="checkbox" <% if(checked){ %>CHECKED<%}%>></input>',
        '<% } %>',
        '<% if(icon) { %>',
            '<img class="icon" src="<%= icon %>" width="16" height="16" />',
        '<% } %>',
        '<a href="#js"><%= name %></a>',
        '<span class="badges"><%= extra %></span>',
        '<% if(snippet){ %>',
            '<p class="snippet"><%= snippet %></p>',
        '<% } %>',
        '<% if(children) { %>',
        '<% if(collapsible) { %>',
        '<ul><%= children %></ul>',
        '<% }else{ %>',
        '<ul><%= children %></ul>',
        '<% } %>',
        '<% } else if(collapsible) { %>',
            '<ul></ul>',
        '<% } %>',
    '</li>'
].join(''));

lingcod.Tree.prototype.selectItem = function(item, scrollTo){
    var wasHidden = false;
    if(typeof item == 'string'){
        item = this.element.find(item);
        wasHidden = this._expandAndToggleRecursive(item);
    }else{
        item = $(item);
    }
    var input = item.find('>input');
    var wasChecked = input.attr('checked');
    if(!wasChecked){
        input.click();
    }
    
    var list = item.find('>ul');
    var checked = [];
    if(list.length > 0){
        this._toggleCheckboxes(list, true, checked);
    }
    if(!wasChecked || checked.length){
        $(this).trigger('itemToggle', [checked, true]);
    }
    
    var data = [];
    this.clearSelection();
    this._toggleCheckboxes(item, true, data);
    item.addClass('selected');
    
    if(scrollTo){
        var s = (this.options.scrollEl) ? $(this.options.scrollEl) : $(this.element).parent();
        var parent = s.parent();
        var ph = parent.height();
        var st = s.scrollTop();
        var visibleBounds = [st, st + ph - 20];
        var position = $(item).position().top + st;
        if(position > visibleBounds[0] && position < visibleBounds[1]){
            // already visible
        }else{
            s.scrollTop(position - (ph / 2) + 20);
        }
    }
}

lingcod.Tree.prototype.clearSelection = function(){
    $(".marinemap-tree li.selected").removeClass('selected');
}

lingcod.Tree.prototype.add = function(options){
    var element = $(this._rTemplate(options));
    // add metadata
    for(var k in options.data){
        element.data(k, options.data[k]);
    }
    var parent;
    if(typeof options.parent == 'string'){
        parent = this.element.find(options.parent);
    }else if(typeof options.parent == 'undefined' || options.parent == null || options.parent == false){
        parent = this.element;
    }else{
        parent = options.parent;
    }
    if(parent == this.element){
        var ul = parent;
    }else{
        var ul = parent.find('>ul');
        if(ul.size() == 0){
            parent.append('<ul></ul>');
            var ul = parent.find('>ul');
        }
    }
    if(ul.find('li').length == 0){
        ul.html('');
    }
    ul.append(element);
    // Here the parent needs to have something set on it
    // if(options.checked && options.parent){
    //     $(options.parent).find('> input[type="checkbox"]').attr('checked', true);
    // }
    // var element = ul.find('.'+options['id']);
    options = null;
    return element;
}

lingcod.Tree.prototype.renderTemplate = function(options){
    if(jQuery.isArray(options)){
        var strings = [];
        for(var i=0;i<options.length;i++){
            strings.push(this._rTemplate(options[i]));
        }
        return strings.join('');
    }else{
        var string = this._rTemplate(options);
        return string;
    }
}

lingcod.Tree.prototype.nodeExists = function(selector){
    if(this.element.find(selector).length > 0){
        return true;
    }else{
        return false;
    }
}

lingcod.Tree.prototype.destroy = function(){
    this.element.find('span.collapsible').die('click');
    this.element.find('li.marinemap-tree-item a').die('dblclick');
    this.element.find('li a').die('contextmenu');
    this.element.find('li.marinemap-tree-item input[type=checkbox]').die('click');
}

lingcod.Tree.prototype._rTemplate = function(options){
    return this._template(
        jQuery.extend({}, this.defaults, options)
    );
}

lingcod.Tree.prototype._toggleCheckboxes = function(el, state, data){
    var self = this;
    el.find('>li.toggle').each(function(){
        var input = $(this).find('>input');
        // this code might not work for deeply nested trees, needs
        // testing for use cases other than array->mpa
        if(input.attr('checked') != state){
            input.attr('checked', state);
            data.push($(this));
        }
        var ul = $(this).find('>ul');
        if(ul.length > 0){
            data = self._toggleCheckboxes(ul, state, data);
        }
    });
    return data;
}

lingcod.Tree.prototype._expandAndToggleRecursive = function(item, wasHidden){
    if(!(wasHidden === true || wasHidden === false)){
        wasHidden = false;
    }
    var parent = item.parent().parent();
    if(parent.hasClass('marinemap-tree-item')){
        if(parent.find('>ul:visible').length == 0){
            wasHidden = true;
            parent.find('>span.collapsible').click();
        }
        var input = parent.find('>input');
        if(input){
            input.attr('checked', true);
        }
        return this._expandAndToggleRecursive(parent, wasHidden);
    }else{
        return wasHidden;
    }
}
