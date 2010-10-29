from django.conf.urls.defaults import *
from lingcod.common.utils import get_logger
from lingcod.common.utils import get_class

logger = get_logger()

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
                       
    # can't do this validation due to circular reference between form and 
    # model
    # # try:
    # form_class = get_class(model.Rest.form)
    # # except:
    # #     raise FeatureConfigurationError(
    # #         """Feature class %s is not configured with a valid form class. 
    # #         Could not import %s."""
    # #          % (model.__name__, model.Rest.form)
    return True
    

class FeatureConfig:
    """Represents properties of Feature Classes derived from both defaults and
    developer-specified options within the Rest inner-class. These properties
    drive the features of the spatial content managment system, such as 
    CRUD operations, copy, sharing, etc.
    """
    def __init__(self, model, config):
        if not config:
            raise FeatureConfigurationError(
                'Have not defined Rest inner-class on registered feature \
                class %s' % (model.__name__,))

        if not hasattr(config, 'form'):
            raise FeatureConfigurationError(
                "Feature class %s is not configured with a form class. \
                To specify, add a `form` property to its Rest inner-class."
                 % (model.__name__))

        self.form = config.form