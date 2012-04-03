from madrona.features.forms import FeatureForm, SpatialFeatureForm

################ EXAMPLE ##########################################
from _app.models import AOI, Folder

class AOIForm(SpatialFeatureForm):
    class Meta(SpatialFeatureForm.Meta):
        model = AOI

class FolderForm(FeatureForm):
    class Meta(FeatureForm.Meta):
        model = Folder
################ END EXAMPLE ######################################
