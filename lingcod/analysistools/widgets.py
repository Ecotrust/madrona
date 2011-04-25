from django import forms
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.conf import settings

class SliderWidget(forms.TextInput):
    """
    http://pastebin.com/f34f0c71d
    """

    def __init__(self, min=None, max=None, step=None, image=None, attrs=None):
        super(SliderWidget, self).__init__(attrs)
        self.max = 100
        self.min = 0
        self.step = None
        self.image = None

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

        field = super(SliderWidget, self).render(name, value, attrs)
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
            // Create the sliderbar
            $('#%(slider_id)s').slider({
                range: 'min',
                min : %(min)s, 
                max : %(max)s,
                %(step)s
                change : function(event, ui) {
                    // When the slider changes, set the value of the field
                    $('#%(field_id)s').val($('#%(slider_id)s').slider('value'));
                }
            });
           
            // Initialize the slider bar to the current value
            $('#%(slider_id)s').slider("value", $('#%(field_id)s').val() ); 

            // If the field changes, change the slider bar
            $('#%(field_id)s').change( function (){
                $('#%(slider_id)s').slider("value", $('#%(field_id)s').val())
            }); 
        });
        </script>
        """ % { 'slider_id' : slider_id, 
                'field_id' : "id_%s" % name, 
                'min' : self.min, 
                'max' : self.max, 
                'step' : self.get_step()}
        
        return mark_safe(image_html+field+slider)


