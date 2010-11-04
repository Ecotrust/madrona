from django.conf.urls.defaults import *
from lingcod.common.utils import get_logger
from lingcod.common.utils import get_class
from django.template.defaultfilters import slugify
from django.template import loader, TemplateDoesNotExist
from lingcod.features.forms import FeatureForm
from django.core.urlresolvers import reverse

registered_models = []
logger = get_logger()

class FeatureConfigurationError(Exception):
    pass

class FeatureOptions:
    """
    Represents properties of Feature Classes derived from both defaults and
    developer-specified options within the Options inner-class. These 
    properties drive the features of the spatial content managment system, 
    such as CRUD operations, copy, sharing, etc.
    """
    def __init__(self, model):
        
        # Import down here to avoid circular reference
        from lingcod.features.models import Feature        
        
        if not issubclass(model, Feature):
            raise FeatureConfigurationError('Is not a subclass of \
lingcod.features.models.Feature')
        
        self._model = model
        name = model.__name__
        
        if not getattr(model, 'Options', False):
            raise FeatureConfigurationError(
                'Have not defined Options inner-class on registered feature \
class %s' % (name, ))
        
        self._options = model.Options
    
        if not hasattr(self._options, 'form'):
            raise FeatureConfigurationError(
                "Feature class %s is not configured with a form class. \
To specify, add a `form` property to its Options inner-class." % (name,))
    
        if not isinstance(self._options.form, str):
            raise FeatureConfigurationError(
                "Feature class %s is configured with a form property that is \
not a string path." % (name,))
                
        self.form = self._options.form
        self.slug = slugify(name)
        self.verbose_name = getattr(self._options, 'verbose_name', name)
        self.form_template = getattr(self._options, 'form_template', 
            'features/form.html')
        self.form_context = getattr(self._options, 'form_context', {})
        self.show_context = getattr(self._options, 'show_context', {})
        self.links = getattr(self._options, 'links', [])
        for link in self.links:
            link.options = self
    
    def get_show_template(self):
        """
        Returns the template used to render this Feature Class' attributes
        """
        # Grab a template specified in the Options object, or use the default
        template = getattr(self._options, 'show_template', 
            '%s/show.html' % (self.slug, ))
        try:
            t = loader.get_template(template)
        except TemplateDoesNotExist:
            # If a template has not been created, use a stub that displays
            # some documentation on how to override the default template
            t = loader.get_template('features/show.html')
        return t
    
    def get_form_class(self):
        """
        Returns the form class for this Feature Class.
        """
        try:
            klass = get_class(self.form)
        except:
            raise FeatureConfigurationError(
                "Feature class %s is not configured with a valid form class. \
Could not import %s." % (self._model.__name__, self.form))

        if not issubclass(klass, FeatureForm):
            raise FeatureConfigurationError(
                "Feature class %s's form is not a subclass of \
lingcod.features.forms.FeatureForm." % (self._model.__name__, ))

        return klass
    
    def json(self):
        """
        Returns a json representation of this feature class configuration
        that can be used to specify client behavior
        """
        pass
        
    def get_create_form(self):
        """
        Returns the path to a form for creating new instances of this model
        """
        return reverse('%s_create_form' % (self.slug, ))
    
    def get_update_form(self, pk):
        """
        Given a primary key, returns the path to a form for updating a Feature
        Class
        """
        return reverse('%s_update_form' % (self.slug, ), args=[pk])
    
    def get_resource(self, pk):
        """
        Returns the primary url for a feature. This url supports GET, POST, 
        and DELETE operations.
        """
        return reverse('%s_resource' % (self.slug, ), args=[pk])
        
class Link:
    def __init__(self, rel, title, view, method='post', select='single', 
        type=None, slug=None, generic=False, extra_kwargs=None):
        self.rel = rel
        try:
            self.view = get_class(view)
        except:
            raise FeatureConfigurationError('Link "%s" configured with \
invalid path to view %s' % (title, view))
        self.options = None
        self.title = title
        self.method = method
        self.type = type
        self.generic = generic
        self.slug = slug
        self.select = select
        # Make sure title isn't empty
        if self.title is '':
            raise FeatureConfigurationError('Link title is empty')
        valid_options = ('single', 'multiple', 'single multiple', 
            'multiple single')
        # Check for valid 'select' kwarg
        if self.select not in valid_options:
            raise FeatureConfigurationError(
                'Link specified with invalid select option "%s"' % (
                    self.select, ))
        # Create slug from the title unless a custom slug is specified
        if self.slug is None:
            self.slug = slugify(title)
        # Make sure the view has the right signature
        self._validate_view(self.view)
    
    def _validate_view(self, view):
        """
        Ensures view has a compatible signature to be able to hook into the 
        features app url registration facilities
        
        For single-select views
            must accept a second argument named instance
        For multiple-select views
            must accept a second argument named instances

        Must also ensure that if the extra_kwargs option is specified, the 
        view can handle them
        """
        # Check for instance or instances arguments
        if self.select is 'single':
            args = view.__code__.co_varnames
            if len(args) < 2 or args[1] != 'instance':
                raise FeatureConfigurationError('Link "%s" not configured \
with a valid view. View must take a second argument named instance.' % (
self.title, ))
        else:
            # select="multiple" or "multiple single" or "single multiple"
            args = view.__code__.co_varnames
            if len(args) < 2 or args[1] != 'instances':
                raise FeatureConfigurationError('Link "%s" not configured \
with a valid view. View must take a second argument named instances.' % (
self.title, ))

        # TODO: Check that extra_kwargs can be passed to the view
    
    def url_name(self):
        # Can only be called if a Link is retrieved via 
        # Feature.get_options().links
        return "%s_%s" % (self.options.slug, self.slug)
        
    def reverse(self, instances):
        """
        Can be used to get the url for this link. 
        
        In the case of select=single links, just pass in a single instance. In
        the case of select=multiple links, pass in an array.
        """
        if not isinstance(instances,tuple) and not isinstance(instances,list):
            instances = [instances]
        ids = ','.join([instance.uid for instance in instances])
        return reverse(self.url_name(), kwargs={'ids': ids})
    
    def __str__(self):
        return self.title
    
    def __unicode__(self):
        return str(self)
    
    def json(self):
        return ''

def create_link(rel, *args, **kwargs):
    nargs = [rel]
    nargs.extend(args)
    return Link(*nargs, **kwargs)

def alternate(*args, **kwargs):
    return create_link('alternate', *args, **kwargs)

def related(*args, **kwargs):
    return create_link('related', *args, **kwargs)

def edit(*args, **kwargs):
    return create_link('edit', *args, **kwargs)

def edit_form(*args, **kwargs):
    kwargs['method'] = 'form'
    return create_link('edit', *args, **kwargs)


def register(*args):
    for model in args:
        model.get_options()
        logger.debug('registering %s' % (model.__name__,) )
        if model not in registered_models:
            registered_models.append(model)