from django import forms
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.conf import settings
from django.contrib.gis.geos import fromstr

class SliderWidget(forms.TextInput):
    """
    http://pastebin.com/f34f0c71d
    """

    def __init__(self, min=None, max=None, step=None, image=None, attrs=None, show_number=True):
        super(SliderWidget, self).__init__(attrs)
        self.max = 100
        self.min = 0
        self.step = None
        self.image = None
        self.show_number = True

        if max:
            self.max = max
        if min:
            self.min = min
        if step:
            self.step = step
        if image:
            self.image = image
        self.show_number = show_number
    
    def get_step(self):
        if self.step:
            return "step : %s," % self.step
        else:
            return ''

    def render(self, name, value, attrs=None):
        attrs['class'] = 'slidervalue'
        final_attrs = self.build_attrs(attrs, name=name)
        slider_id = 'slider-'+name

        field = super(SliderWidget, self).render(name, value, attrs)
        hide_js = ""
        if not self.show_number:
            hide_js = "field.hide();"

        image_html = ""
        if self.image:
            url = self.image
            if not url.startswith("/") and not self.image.startswith("http://"):
                url = settings.MEDIA_URL + url
            image_html = """<span class="form-image"><img src="%s" /></span>""" % url
        slider = """
        <div class="slider" id="%(slider_id)s"></div>
        <script type="text/javascript">
        lingcod.onShow( function() {
            var field = $('#%(field_id)s');
            %(hide_js)s // hide field?
            var slidy = $('#%(slider_id)s');
            // Create the sliderbar
            slidy.slider({
                range: 'min',
                min : %(min)s, 
                max : %(max)s,
                %(step)s
                change : function(event, ui) {
                    // When the slider changes, set the value of the field
                    field.val(slidy.slider('value'));
                },
                slide : function(event, ui) {
                    // When the slider slides, set the value of the field
                    field.val(slidy.slider('value'));
                }
            });
           
            // Initialize the slider bar to the current value
            slidy.slider("value", field.val() ); 

            // If the field changes, change the slider bar
            field.change( function (){
                slidy.slider("value", field.val())
            }); 
        });
        </script>
        """ % { 'slider_id' : slider_id, 
                'field_id' : "id_%s" % name, 
                'min' : self.min, 
                'max' : self.max, 
                'hide_js': hide_js,
                'step' : self.get_step()}
        
        return mark_safe(image_html+field+slider)


class SimplePoint(forms.TextInput):

    def __init__(self, title='Point', attrs=None):
        super(SimplePoint, self).__init__(attrs)
        self.title = title

    def render(self, name, value, attrs=None):
        output = super(SimplePoint, self).render(name, value, attrs)
        set_text = "Set"
        new_text = "New"
        if value:
            geo = fromstr(value)
            set_text = "Reset"
            new_text = "Reset"
        return mark_safe("""
        <div>
            <a id="do_grabpoint" class="button" href="#">
                <span>Click to %s Starting Point</span>
            </a>
            <span style="display:none"> 
            %s 
            </span>
        </div>
        <br/><br/>
        <script type="text/javascript">
        var shape;

        lingcod.beforeDestroy( function() {
            if(shape && shape.getParentNode()){
                gex.dom.removeObject(shape);
            }
        });

        lingcod.onShow( function() {
            function shape_to_wkt(shape) {
                var lat = shape.getGeometry().getLatitude();
                var lon = shape.getGeometry().getLongitude();
                var wkt = "SRID=4326;POINT(" + lon + " " + lat + ")";
                return wkt;
            }

            $('#do_grabpoint').click( function () {
                if(!$(this).hasClass('disabled')){
                    if(shape && shape.getParentNode()){
                        gex.dom.removeObject(shape);
                    }
                    $(this).addClass('disabled');
                    var button = $(this);
                    button.html('<span>Click map to set placemark</span>');

                    var popts = {
                        visibility: true,
                        name: '%s %s',
                        style: { icon: { color: '#FF0' } }            
                    }
                    popts['point'] = [0,0]; 
                    shape = gex.dom.addPlacemark(popts);
                    gex.edit.place(shape, {
                        bounce: false,
                        dropCallback: function(){
                            $('#id_%s').val(shape_to_wkt(shape));
                            button.html('<span>Drag Placemark to Reset</span>');
                            gex.edit.makeDraggable(shape, {
                                bounce: false, 
                                dropCallback: function () {
                                    $('#id_%s').val(shape_to_wkt(shape));
                                }
                            });
                        }
                    });
                }
            });
        });
        </script>
        """ % (set_text,output,new_text,self.title,name,name))

class DualSliderWidget(forms.TextInput):

    def __init__(self, min_field, max_field, min=None, max=None, step=None, image=None, attrs=None):
        super(DualSliderWidget, self).__init__(attrs)
        self.max = 100
        self.min = 0
        self.step = None
        self.image = None
        self.min_field = min_field
        self.max_field = max_field

        if max:
            self.max = max
        if min:
            self.min = min
        if step:
            self.step = step
        if image:
            self.image = image
    
    def get_step(self):
        if self.step:
            return "step : %s," % self.step
        else:
            return ''

    def render(self, name, value, attrs=None):
        attrs['class'] = 'slidervalue'
        final_attrs = self.build_attrs(attrs, name=name)
        slider_id = 'slider-'+name

        #field = super(DualSliderWidget, self).render(name, value, attrs)
        
        field = """<input style="display:none;" type="text" name="%(name)s" value="0" id="id_%(name)s" />""" % {'name':name}

        image_html = ""
        if self.image:
            url = self.image
            if not url.startswith("/") and not self.image.startswith("http://"):
                url = settings.MEDIA_URL + url
            image_html = """<span class="form-image"><img src="%s" /></span>""" % url
        slider = """
        <div class="slider" id="%(slider_id)s"></div>
        <script type="text/javascript">
        lingcod.onShow( function() {
            var low_field = $('#%(low_field_id)s');
            var high_field = $('#%(high_field_id)s');
            var slidy = $('#%(slider_id)s');
            // Create the sliderbar
            slidy.slider({
                range: true,
                min : %(min)s, 
                max : %(max)s,
                values: [%(min)s, %(max)s],
                %(step)s
                change : function(event, ui) {
                    // When the slider changes, set the value of the field
                    low_field.val(ui.values[0]);
                    high_field.val(ui.values[1]);
                },
                slide : function(event, ui) {
                    // When the slider slides, set the value of the field
                    low_field.val(ui.values[0]);
                    high_field.val(ui.values[1]);
                }
            });

            // initialize
            slidy.slider("values", [low_field.val(),high_field.val()])

            // If the field changes, change the slider bar
            low_field.change( function (){
                slidy.slider("values", [low_field.val(),high_field.val()])
            }); 
            high_field.change( function (){
                slidy.slider("values", [low_field.val(),high_field.val()])
            }); 
        });
        </script>
        """ % { 'slider_id' : slider_id, 
                'low_field_id' : "id_%s" % self.min_field, 
                'high_field_id' : "id_%s" % self.max_field, 
                'min' : self.min, 
                'max' : self.max, 
                'step' : self.get_step()}
        
        return mark_safe(image_html+field+slider)

