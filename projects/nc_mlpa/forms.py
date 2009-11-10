from lingcod.mpa.forms import *
from mlpa.models import *

class MLPASaveForm(MpaForm):
    
    class Meta(MpaForm.Meta):
        model = MlpaMpa
        fields = ('user', 'name', 'geometry_orig', 'geometry_final')
    
    
class MLPALoadForm(LoadForm):
   
    class Meta(LoadForm.Meta):
        model = MlpaMpa
        fields = ('user', 'name')