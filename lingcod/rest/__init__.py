from django.conf.urls.defaults import *
from lingcod.common.utils import get_logger

logger = get_logger()
registered_models = []

class FeatureConfigurationError(Exception):
    pass

def validate_feature_config(model):
    """This function validates that each registered feature class has a Rest 
    inner-class and that it has the required properties. 
    
    Because models of each app are loaded once the application is booted up, 
    validation exceptions will conveniently be raised when starting the dev 
    server if there are any mistakes.
    """
    # check for the Rest inner-class
    if not hasattr(model, 'Rest'):
        raise FeatureConfigurationError(
            'Have not defined Rest inner-class on registered feature class %s' 
                % (model.__name__,))
    # check that an associated form has been specified
    if not hasattr(model.Rest, 'form'):
        raise FeatureConfigurationError(
            """Feature class %s is not configured with a form class. 
            To specify, add a `form` property to its Rest inner-class."""
             % (model.__name__))
    return True

def register(*args):
    for model in args:
        validate_feature_config(model)
        logger.debug('registering %s' % (model.__name__,) )        
        registered_models.append(model)