from lingcod.array.forms import ArrayForm as BaseArrayForm
from mlpa.models import MpaArray
from mlpa.models import MlpaMpa
from lingcod.mpa.forms import MpaForm as BaseMpaForm
from lingcod.array.forms import ArrayForm as BaseArrayForm

class ArrayForm(BaseArrayForm):
    class Meta(BaseArrayForm.Meta):
        model = MpaArray


class MpaForm(BaseMpaForm):
    class Meta:
        model = MlpaMpa
        # fields = ('user', 'name', 'geometry_orig', 'geometry_final')
        exclude = ('content_type', 'object_id', 'cluster_id', 'is_estuary', 'group_before_edits', )