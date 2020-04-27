//knockout-sortable | (c) 2012 Ryan Niemeyer | http://www.opensource.org/licenses/mit-license
(function(ko, $, undefined) {
var ITEMKEY = "ko_sortItem",
    LISTKEY = "ko_sortList",
    PARENTKEY = "ko_parentList";

//internal afterRender that adds meta-data to children
var addMetaDataAfterRender = function(elements, data) {
    ko.utils.arrayForEach(elements, function(element) {
        if (element.nodeType === 1) {
            ko.utils.domData.set(element, ITEMKEY, data);
            ko.utils.domData.set(element, PARENTKEY, ko.utils.domData.get(element.parentNode, LISTKEY));
        }
    });
};

//prepare the proper options for the template binding
var prepareTemplateOptions = function(valueAccessor) {
    var result = {},
        options = ko.utils.unwrapObservable(valueAccessor()),
        actualAfterRender;

    //build our options to pass to the template engine
    if (options.data) {
        result.foreach = options.data;
        result.name = options.template;
    } else {
        result.foreach = valueAccessor();
    }

    ko.utils.arrayForEach(["afterAdd", "afterRender", "beforeRemove", "includeDestroyed", "templateEngine", "templateOptions"], function (option) {
        result[option] = options[option] || ko.bindingHandlers.sortable[option];
    });

    //use an afterRender function to add meta-data
    if (result.afterRender) {
        //wrap the existing function, if it was passed
        actualAfterRender = result.afterRender;
        result.afterRender = function(element, data) {
            addMetaDataAfterRender.call(data, element, data);
            actualAfterRender.call(data, element, data);
        };
    } else {
        result.afterRender = addMetaDataAfterRender;
    }

    //return options to pass to the template binding
    return result;
};

ko.bindingHandlers.jqSlider = {
    init: function(element, valueAccessor, allBindingsAccessor) {
        //initialize the control
        var options = allBindingsAccessor().jqOptions || {};
        $(element).slider(options);

        //handle the value changing in the UI
        ko.utils.registerEventHandler(element, "slide", function() {
            //would need to do some more work here, if you want to bind against non-observables
            var observable = valueAccessor();
            observable($(element).slider("value"));
        });

    },
    //handle the model value changing
    update: function(element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor());
        $(element).slider("value", value);   

    }
};

// set up protected observables
ko.protectedObservable = function(initialValue) {
    //private variables
    var _actualValue = ko.observable(initialValue),
        _tempValue = initialValue;

    //computed observable that we will return
    var result = ko.computed({
        //always return the actual value
        read: function() {
           return _actualValue();
        },
        //stored in a temporary spot until commit
        write: function(newValue) {
             _tempValue = newValue;
        }
    });

    //if different, commit temp value
    result.commit = function() {
        if (_tempValue !== _actualValue()) {
             _actualValue(_tempValue);
        }
    };

    //force subscribers to take original
    result.reset = function() {
        _actualValue.valueHasMutated();
        _tempValue = _actualValue();   //reset temp value
    };
    return result;
};


//connect items with observableArrays
ko.bindingHandlers.sortable = {
    init: function(element, valueAccessor, allBindingsAccessor, data, context) {
        var $element = $(element),
            value = ko.utils.unwrapObservable(valueAccessor()) || {},
            templateOptions = prepareTemplateOptions(valueAccessor),
            sortable = {},
            startActual, updateActual;

        //remove leading/trailing text nodes from anonymous templates
        ko.utils.arrayForEach(element.childNodes, function(node) {
            if (node && node.nodeType === 3) {
                node.parentNode.removeChild(node);
            }
        });

        //build a new object that has the global options with overrides from the binding
        $.extend(true, sortable, ko.bindingHandlers.sortable);
        if (value.options && sortable.options) {
            ko.utils.extend(sortable.options, value.options);
            delete value.options;
        }
        ko.utils.extend(sortable, value);

        //if allowDrop is an observable or a function, then execute it in a computed observable
        if (sortable.connectClass && (ko.isObservable(sortable.allowDrop) || typeof sortable.allowDrop == "function")) {
            ko.computed({
               read: function() {
                   var value = ko.utils.unwrapObservable(sortable.allowDrop),
                       shouldAdd = typeof value == "function" ? value.call(this, templateOptions.foreach) : value;
                   ko.utils.toggleDomNodeCssClass(element, sortable.connectClass, shouldAdd);
               },
               disposeWhenNodeIsRemoved: element
            }, this);
        } else {
            ko.utils.toggleDomNodeCssClass(element, sortable.connectClass, sortable.allowDrop);
        }

        //wrap the template binding
        ko.bindingHandlers.template.init(element, function() { return templateOptions; }, allBindingsAccessor, data, context);

        //keep a reference to start/update functions that might have been passed in
        startActual = sortable.options.start;
        updateActual = sortable.options.update;

        //initialize sortable binding after template binding has rendered in update function
        setTimeout(function() {
            $element.sortable(ko.utils.extend(sortable.options, {
                start: function(event, ui) {
                    //make sure that fields have a chance to update model
                    ui.item.find("input:focus").change();
                    if (startActual) {
                        startActual.apply(this, arguments);
                    }
                },
                update: function(event, ui) {
                    var sourceParent, targetParent, targetIndex, arg,
                        el = ui.item[0],
                        item = ko.utils.domData.get(el, ITEMKEY);

                    if (item) {
                        //identify parents
                        sourceParent = ko.utils.domData.get(el, PARENTKEY);
                        targetParent = ko.utils.domData.get(el.parentNode, LISTKEY);
                        targetIndex = ko.utils.arrayIndexOf(ui.item.parent().children(), el);

                        if (sortable.beforeMove || sortable.afterMove) {
                            arg = {
                                item: item,
                                sourceParent: sourceParent,
                                sourceParentNode: el.parentNode,
                                sourceIndex: sourceParent.indexOf(item),
                                targetParent: targetParent,
                                targetIndex: targetIndex,
                                cancelDrop: false
                            };
                        }

                        if (sortable.beforeMove) {
                            sortable.beforeMove.call(this, arg, event, ui);
                            if (arg.cancelDrop) {
                                $(arg.sourceParent === arg.targetParent ? this : ui.sender).sortable('cancel');
                                return;
                            }
                        }

                        if (targetIndex >= 0) {
                            sourceParent.remove(item);
                            targetParent.splice(targetIndex, 0, item);
                        }

                        //rendering is handled by manipulating the observableArray; ignore dropped element
                        ko.utils.domData.set(el, ITEMKEY, null);
                        ui.item.remove();

                        //allow binding to accept a function to execute after moving the item
                        if (sortable.afterMove) {
                           sortable.afterMove.call(this, arg, event, ui);
                        }
                    }

                    if (updateActual) {
                        updateActual.apply(this, arguments);
                    }
                },
                connectWith: sortable.connectClass ? "." + sortable.connectClass : false
            }));

            //handle enabling/disabling sorting
            if (sortable.isEnabled !== undefined) {
                ko.computed({
                    read: function() {
                        $element.sortable(ko.utils.unwrapObservable(sortable.isEnabled) ? "enable" : "disable");
                    },
                    disposeWhenNodeIsRemoved: element
                });
            }
        }, 0);

        //handle disposal
        ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            $element.sortable("destroy");
        });

        return { 'controlsDescendantBindings': true };
    },
    update: function(element, valueAccessor, allBindingsAccessor, data, context) {
        var templateOptions = prepareTemplateOptions(valueAccessor);

        //attach meta-data
        ko.utils.domData.set(element, LISTKEY, templateOptions.foreach);

        //call template binding's update with correct options
        ko.bindingHandlers.template.update(element, function() { return templateOptions; }, allBindingsAccessor, data, context);
    },
    connectClass: 'ko_container',
    allowDrop: true,
    afterMove: null,
    beforeMove: null,
    options: {}
};
})(ko, jQuery);