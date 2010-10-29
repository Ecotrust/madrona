from django.conf.urls.defaults import *
from lingcod.common.utils import get_logger

logger = get_logger()
registered_models = []

def register(*args):
    for model in args:
        model.get_config()
        logger.debug('registering %s' % (model.__name__,) )
        if model not in registered_models:
            registered_models.append(model)