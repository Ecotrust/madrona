from django import forms
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.conf import settings
from django.contrib.gis.geos import fromstr


class BookmarkWidget(forms.TextInput):
    def __init__(self, title='Point', attrs=None):
        super(BookmarkWidget, self).__init__(attrs)
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
