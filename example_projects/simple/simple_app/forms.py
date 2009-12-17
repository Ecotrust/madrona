from lingcod.array.forms import ArrayForm
from simple_app.models import MpaArray
from simple_app.models import Mpa
from lingcod.mpa.forms import MpaForm

class SimpleArrayForm(ArrayForm):
    class Meta(MpaArray.Meta):
        model = MpaArray


class SimpleMpaForm(MpaForm):
    class Meta:
        model = Mpa
        fields = ('user', 'name', 'geometry_orig', 'geometry_final')
        