from lingcod.mpa.forms import MpaForm as BaseMpaForm
from lingcod.array.forms import ArrayForm as BaseArrayForm
from models import Mpa, MpaArray

class ArrayForm(BaseArrayForm):
    class Meta(BaseArrayForm.Meta):
        model = MpaArray
        exclude = ('sharing_groups',)

class MpaForm(BaseMpaForm):
    class Meta:
        model = Mpa
        exclude = ('sharing_groups','content_type','object_id',)
