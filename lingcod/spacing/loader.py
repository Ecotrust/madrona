from django.contrib.gis.utils import LayerMapping
from lingcod.spacing.models import *

def load_land(file_name, verbose=True):
    mapping = {
        'geometry' : 'POLYGON',
    }
    lm = prep_layer_mapping(file_name, Land, mapping)
    lm.save(strict=True, verbose=verbose)

def prep_layer_mapping(shpfile_name, model, mapping):
    shpfile = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', shpfile_name))
    lm = LayerMapping(model, shpfile, mapping, transform=False, encoding='iso-8859-1')
    return lm