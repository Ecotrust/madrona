from django.conf.urls.defaults import *
from lingcod.common.utils import get_logger
from lingcod.features import validate_feature_config

logger = get_logger()
registered_models = []

def register(*args):
    for model in args:
        validate_feature_config(model)
        logger.debug('registering %s' % (model.__name__,) )
        if model not in registered_models:
            registered_models.append(model)