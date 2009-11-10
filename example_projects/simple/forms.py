from lingcod.mpa.forms import *
from simple_app.models import *

class SimpleSaveForm(MpaForm):
    
    class Meta(MpaForm.Meta):
        model = Mpa
        fields = ('user', 'name', 'geometry_orig', 'geometry_final')
    
    
class SimpleLoadForm(LoadForm):
   
    class Meta(LoadForm.Meta):
        model = Mpa
        fields = ('user', 'name')