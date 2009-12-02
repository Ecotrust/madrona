from lingcod.array.forms import ArrayForm
from simple_app.models import MpaArray

class SimpleArrayForm(ArrayForm):
    class Meta(MpaArray.Meta):
        model = MpaArray