from django.conf.urls.defaults import *
from madrona.common.utils import get_logger, get_class, enable_sharing
from django.template.defaultfilters import slugify
from django.template import loader, TemplateDoesNotExist
from madrona.features.forms import FeatureForm
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, class_prepared
from django.dispatch import receiver
from django.contrib.auth.models import Permission, Group
from django.conf import settings
from django.db.utils import DatabaseError
import json

registered_models = []
registered_model_options = {}
registered_links = []
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
        from madrona.features.models import Feature, FeatureCollection    

        # call this here to ensure that permsissions get created
        #enable_sharing()

        if not issubclass(model, Feature):
            raise FeatureConfigurationError('Is not a subclass of \
madrona.features.models.Feature')

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
        """
        Path to FeatureForm used to edit this class.
        """

        self.slug = slugify(name)
        """
        Name used in the url path to this feature as well as part of 
        the Feature's uid
        """

        self.verbose_name = getattr(self._options, 'verbose_name', name)
        """
        Name specified or derived from the feature class name used 
        in the user interface for representing this feature class.
        """

        self.form_template = getattr(self._options, 'form_template', 
            'features/form.html')
        """
        Location of the template that should be used to render forms
        when editing or creating new instances of this feature class.
        """

        self.form_context = getattr(self._options, 'form_context', {})
        """
        Context to merge with default context items when rendering
        templates to create or modify features of this class.
        """

        self.show_context = getattr(self._options, 'show_context', {})
        """
        Context to merge with default context items when rendering
        templates to view information about instances of this feature class.
        """

        self.icon_url = getattr(self._options, 'icon_url', None)
        """
        Optional; URL to 16x16 icon to use in kmltree
        Use full URL or relative to MEDIA_URL
        """

        self.links = []
        """
        Links associated with this class.
        """

        opts_links = getattr(self._options, 'links', False)
        if opts_links:
            self.links.extend(opts_links)

        self.enable_copy = getattr(self._options, 'disable_copy', True)
        """
        Enable copying features. Uses the feature class' copy() method. 
        Defaults to True.
        """

        # Add a copy method unless disabled
        if self.enable_copy:
            self.links.insert(0, edit('Copy', 
                'madrona.features.views.copy', 
                select='multiple single',
                edits_original=False))

        confirm = "Are you sure you want to delete this feature and it's contents?"

        # Add a multi-share generic link
        # TODO when the share_form view takes multiple instances
        #  we can make sharing a generic link 
        #self.links.insert(0, edit('Share', 
        #    'madrona.features.views.share_form', 
        #    select='multiple single',
        #    method='POST',
        #    edits_original=True,
        #))

        # Add a multi-delete generic link
        self.links.insert(0, edit('Delete', 
            'madrona.features.views.multi_delete', 
            select='multiple single',
            method='DELETE',
            edits_original=True,
            confirm=confirm,
        ))

        # Add a staticmap generic link
        export_png = getattr(self._options, 'export_png', True)
        if export_png:
            self.links.insert(0, alternate('PNG Image', 
                'madrona.staticmap.views.staticmap_link', 
                select='multiple single',
                method='GET',
            ))

        # Add a geojson generic link
        export_geojson = getattr(self._options, 'export_geojson', True)
        if export_geojson:
            self.links.insert(0, alternate('GeoJSON', 
                'madrona.features.views.geojson_link', 
                select='multiple single',
                method='GET',
            ))

        self.valid_children = getattr(self._options, 'valid_children', None)
        """
        valid child classes for the feature container
        """
        if self.valid_children and not issubclass(self._model, FeatureCollection):
            raise FeatureConfigurationError("valid_children Option only \
                    for FeatureCollection classes" % m)

        self.manipulators = [] 
        """
        Required manipulators applied to user input geometries
        """
        manipulators = getattr(self._options, 'manipulators', []) 
        for m in manipulators:
            try:
                manip = get_class(m)
            except:
                raise FeatureConfigurationError("Error trying to import module %s" % m)

            # Test that manipulator is compatible with this Feature Class
            geom_field = self._model.geometry_final._field.__class__.__name__ 
            if geom_field not in manip.Options.supported_geom_fields:
                raise FeatureConfigurationError("%s does not support %s geometry types (only %r)" %
                        (m, geom_field, manip.Options.supported_geom_fields))

            #logger.debug("Added required manipulator %s" % m)
            self.manipulators.append(manip)

        self.optional_manipulators = []
        """
        Optional manipulators that may be applied to user input geometries
        """
        optional_manipulators = getattr(self._options, 'optional_manipulators', [])
        for m in optional_manipulators:
            try:
                manip = get_class(m)
            except:
                raise FeatureConfigurationError("Error trying to import module %s" % m)

            # Test that manipulator is compatible with this Feature Class
            geom_field = self._model.geometry_final._field.__class__.__name__ 
            try:
                if geom_field not in manip.Options.supported_geom_fields:
                    raise FeatureConfigurationError("%s does not support %s geometry types (only %r)" %
                        (m, geom_field, manip.Options.supported_geom_fields))
            except AttributeError:
                raise FeatureConfigurationError("%s is not set up properly; must have "
                        "Options.supported_geom_fields list." % m)

            #logger.debug("Added optional manipulator %s" % m)
            self.optional_manipulators.append(manip)

        self.enable_kml = True
        """
        Enable kml visualization of features.  Defaults to True.
        """
        # Add a kml link by default
        if self.enable_kml:
            self.links.insert(0,alternate('KML',
                'madrona.features.views.kml',
                select='multiple single'))
            self.links.insert(0,alternate('KMZ',
                'madrona.features.views.kmz',
                select='multiple single'))

        for link in self.links:
            if self._model not in link.models:
                link.models.append(self._model)

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

    def get_link(self,linkname):
        """
        Returns the FeatureLink with the specified name
        """
        try:
            link = [x for x in self.links if x.title == linkname][0]
            return link
        except:
            raise Exception("%r has no link named %s" % (self._model, linkname))

    def get_valid_children(self):
        if not self.valid_children:
            raise FeatureConfigurationError(
                "%r is not a properly configured FeatureCollection" % (self._model))

        valid_child_classes = []
        for vc in self.valid_children:
            try:
                vc_class = get_class(vc)
            except:
                raise FeatureConfigurationError(
                        "Error trying to import module %s" % vc) 

            from madrona.features.models import Feature
            if not issubclass(vc_class, Feature):
                raise FeatureConfigurationError(
                        "%r is not a Feature; can't be a child" % vc) 

            valid_child_classes.append(vc_class)

        return valid_child_classes

    def get_potential_parents(self):
        """
        It's not sufficient to look if this model is a valid_child of another
        FeatureCollection; that collection could contain other collections 
        that contain this model. 

        Ex: Folder (only valid child is Array)
            Array (only valid child is MPA)
            Therefore, Folder is also a potential_parent of MPA
        """
        potential_parents = []
        direct_parents = []
        collection_models = get_collection_models()
        for model in collection_models: 
            opts = model.get_options()
            valid_children = opts.get_valid_children()

            if self._model in valid_children:
                direct_parents.append(model)
                potential_parents.append(model)

        for direct_parent in direct_parents:
            if direct_parent != self._model: 
                potential_parents.extend(direct_parent.get_options().get_potential_parents())

        return potential_parents 

    def get_form_class(self):
        """
        Returns the form class for this Feature Class.
        """
        try:
            klass = get_class(self.form)
        except Exception, e:
            raise FeatureConfigurationError(
                "Feature class %s is not configured with a valid form class. \
Could not import %s.\n%s" % (self._model.__name__, self.form, e))

        if not issubclass(klass, FeatureForm):
            raise FeatureConfigurationError(
                "Feature class %s's form is not a subclass of \
madrona.features.forms.FeatureForm." % (self._model.__name__, ))

        return klass

    def dict(self,user,is_owner):
        """
        Returns a json representation of this feature class configuration
        that can be used to specify client behavior
        """
        placeholder = "%s_%d" % (self._model.model_uid(), 14)
        link_rels = {
            'id': self._model.model_uid(),
            'title': self.verbose_name,
            'link-relations': {
                'self': {
                    'uri-template': reverse("%s_resource" % (self.slug, ), 
                        args=[placeholder]).replace(placeholder, '{uid}'),
                    'title': settings.TITLES['self'],
                },
            }
        }

        if is_owner:
            lr = link_rels['link-relations']
            lr['create'] = {
                    'uri-template': reverse("%s_create_form" % (self.slug, ))
            }

            lr['edit'] = [
                    {'title': 'Edit',
                      'uri-template': reverse("%s_update_form" % (self.slug, ), 
                        args=[placeholder]).replace(placeholder, '{uid}')
                    },
                    {'title': 'Share',
                      'uri-template': reverse("%s_share_form" % (self.slug, ), 
                        args=[placeholder]).replace(placeholder, '{uid}')
                    }]

        for link in self.links:
            if not link.generic and link.can_user_view(user, is_owner):
                if link.rel not in link_rels['link-relations'].keys():
                    if not (user.is_anonymous() and link.rel == 'edit'):
                        link_rels['link-relations'][link.rel] = []
                link_rels['link-relations'][link.rel].append(link.dict(user,is_owner))

        if self._model in get_collection_models() and is_owner:
            link_rels['collection'] = {
                'classes': [x.model_uid() for x in self.get_valid_children()],
                'remove': {
                    'uri-template': reverse("%s_remove_features" % (self.slug, ), 
                        kwargs={'collection_uid':14,'uids':'xx'}).replace('14', '{collection_uid}').replace('xx','{uid+}')
                },
                'add': {
                    'uri-template': reverse("%s_add_features" % (self.slug, ), 
                        kwargs={'collection_uid':14,'uids':'xx'}).replace('14', '{collection_uid}').replace('xx','{uid+}')
                }

            }
        return link_rels

    def json(self):
        return json.dumps(self.dict())

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
        return reverse('%s_update_form' % (self.slug, ), args=['%s_%d' % (self._model.model_uid(), pk)])

    def get_share_form(self, pk):
        """
        Given a primary key, returns path to a form for sharing a Feature inst
        """
        return reverse('%s_share_form' % (self.slug, ), args=['%s_%d' % (self._model.model_uid(), pk)])

    def get_resource(self, pk):
        """
        Returns the primary url for a feature. This url supports GET, POST, 
        and DELETE operations.
        """
        return reverse('%s_resource' % (self.slug, ), args=['%s_%d' % (self._model.model_uid(), pk)])

class Link:
    def __init__(self, rel, title, view, method='GET', select='single', 
        type=None, slug=None, generic=False, models=None, extra_kwargs={}, 
        confirm=False, edits_original=None, must_own=False, 
        limit_to_groups=None):

        self.rel = rel
        """Type of link - alternate, related, edit, or edit_form.
        """

        try:
            self.view = get_class(view)
            """
            View function handling requests to this link.
            """
        except Exception as err:
            msg = 'Link "%s" configured with invalid path to view %s' % (title, view)
            msg += '\n%s\n' % str(err)
            if "cannot import" in str(err):
                msg += "(Possible cause: importing Features at the top level in views.py can cause"
                msg += " circular dependencies; Try to import Features within the view function)"

            raise FeatureConfigurationError(msg)

        self.title = title
        """
        Human-readable title for the link to be shown in the user interface.
        """

        self.method = method
        """
        For rel=edit links, identifies whether a form should be requested or 
        that url should just be POST'ed to.
        """

        self.type = type
        """
        MIME type of this link, useful for alternate links. May in the future
        be used to automatically assign an icon in the dropdown Export menu.
        """

        self.slug = slug
        """
        Part of this link's path.
        """

        self.select = select
        """
        Determines whether this link accepts requests with single or multiple
        instances of a feature class. Valid values are "single", "multiple",
        "single multiple", and "multiple single". 
        """

        self.extra_kwargs = extra_kwargs
        """
        Extra keyword arguments to pass to the view.
        """

        self.generic = generic
        """
        Whether this view can be applied to multiple feature classes.
        """

        self.models = models
        """
        List of feature classes that a this view can be applied to, if it is 
        generic.
        """

        self.confirm = confirm
        """
        Confirmation message to show the user before POSTing to rel=edit link
        """

        self.edits_original = edits_original
        """
        Set to false for editing links that create a copy of the original. 
        This will allow users who do not own the instance(s) but can view them
        perform the action.
        """

        self.must_own = must_own
        if self.edits_original:
            self.must_own = True
        """
        Whether this link should be accessible to non-owners.
        Default link behavior is False; i.e. Link can be used for shared features
        as well as for user-owned features. 
        If edits_original is true, this implies must_own = True as well.
        """

        self.limit_to_groups = limit_to_groups
        """
        Allows you to specify groups (a list of group names) 
        that should have access to the link.
        Default is None; i.e. All users have link access regardless of group membership
        """

        if self.models is None:
            self.models = []

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

    def can_user_view(self, user, is_owner):
        """
        Returns True/False depending on whether user can view the link. 
        """
        if self.limit_to_groups:
            # We rely on the auth Group model ensuring unique group names
            user_groupnames = [x.name for x in user.groups.all()]
            match = False
            for groupname in self.limit_to_groups:
                if groupname in user_groupnames:
                    match = True
                    break
            if not match:
                return False

        if self.must_own and not is_owner:
            return False

        return True

    @property
    def url_name(self):
        """
        Links are registered with named-urls. This function will return 
        that name so that it can be used in calls to reverse().
        """
        return "%s-%s" % (self.parent_slug, self.slug)

    @property
    def parent_slug(self):
        """
        Returns either the slug of the only model this view applies to, or 
        'generic'
        """
        if len(self.models) == 1:
            return self.models[0].get_options().slug
        else:
            return 'generic-links'

    def reverse(self, instances):
        """Can be used to get the url for this link. 

        In the case of select=single links, just pass in a single instance. In
        the case of select=multiple links, pass in an array.
        """
        if not isinstance(instances,tuple) and not isinstance(instances,list):
            instances = [instances]
        uids = ','.join([instance.uid for instance in instances])
        return reverse(self.url_name, kwargs={'uids': uids})

    def __str__(self):
        return self.title

    def __unicode__(self):
        return str(self)

    def dict(self,user,is_owner):
        d = {
            'rel': self.rel,
            'title': self.title,
            'select': self.select,
            'uri-template': reverse(self.url_name, 
                kwargs={'uids': 'idplaceholder'}).replace(
                    'idplaceholder', '{uid+}')
        }
        if self.rel == 'edit':
            d['method'] = self.method
        if len(self.models) > 1:
            d['models'] = [m.model_uid() for m in self.models]
        if self.confirm:
            d['confirm'] = self.confirm
        return d

    def json(self):
        return json.dumps(self.dict())

def create_link(rel, *args, **kwargs):
    nargs = [rel]
    nargs.extend(args)
    link = Link(*nargs, **kwargs)
    must_match = ('rel', 'title', 'view', 'extra_kwargs', 'method', 'slug', 
        'select', 'must_own')
    for registered_link in registered_links:
        matches = True
        for key in must_match:
            if getattr(link, key) != getattr(registered_link, key):
                matches = False
                break
        if matches:
            registered_link.generic = True
            return registered_link
    registered_links.append(link)
    return link

def alternate(*args, **kwargs):
    return create_link('alternate', *args, **kwargs)

def related(*args, **kwargs):
    return create_link('related', *args, **kwargs)

def edit(*args, **kwargs):
    if 'method' not in kwargs.keys():
        kwargs['method'] = 'POST'
    return create_link('edit', *args, **kwargs)

def edit_form(*args, **kwargs):
    if 'method' not in kwargs.keys():
        kwargs['method'] = 'GET'
    return create_link('edit', *args, **kwargs)

def register(model):
    options = FeatureOptions(model)
    logger.debug('registering Feature %s' % (model.__name__,))
    if model not in registered_models:
        registered_models.append(model)
        registered_model_options[model.__name__] = options
        for link in options.links:
            if link not in registered_links:
                registered_links.append(link)
    return model

def get_model_options(model_name):
    return registered_model_options[model_name]

def workspace_json(user, is_owner, models=None):
    workspace = {
        'feature-classes': [],
        'generic-links': []
    }
    if not models:
        # Workspace doc gets ALL feature classes and registered links
        for model in registered_models:
            workspace['feature-classes'].append(model.get_options().dict(user, is_owner))
        for link in registered_links:
            if link.generic and link.can_user_view(user, is_owner) \
                    and not (user.is_anonymous() and link.rel == 'edit'):
                workspace['generic-links'].append(link.dict(user, is_owner))
    else:
        # Workspace doc only reflects specified feature class models
        for model in models:
            workspace['feature-classes'].append(model.get_options().dict(user, is_owner))
        for link in registered_links:
            # See if the generic links are relavent to this list
            if link.generic and \
               [i for i in args if i in link.models] and \
               link.can_user_view(user, is_owner) and \
               not (user.is_anonymous() and link.rel == 'edit'):
                    workspace['generic-links'].append(link.dict(user, is_owner))
    return json.dumps(workspace, indent=2)

def get_collection_models():
    """
    Utility function returning models for 
    registered and valid FeatureCollections
    """
    from madrona.features.models import FeatureCollection    
    registered_collections = []
    for model in registered_models:
        if issubclass(model,FeatureCollection):
            opts = model.get_options()
            try:
                assert len(opts.get_valid_children()) > 0
                registered_collections.append(model)
            except:
                pass
    return registered_collections

def get_feature_models():
    """
    Utility function returning models for 
    registered and valid Features excluding Collections
    """
    from madrona.features.models import Feature, FeatureCollection
    registered_features = []
    for model in registered_models:
        if issubclass(model,Feature) and not issubclass(model,FeatureCollection):
            registered_features.append(model)
    return registered_features

def user_sharing_groups(user):
    """
    Returns a list of groups that user is member of and 
    and group must have sharing permissions
    """
    try:
        p = Permission.objects.get(codename='can_share_features')
    except Permission.DoesNotExist:
        return None

    groups = user.groups.filter(permissions=p).distinct()
    return groups

def groups_users_sharing_with(user, include_public=False):
    """
    Get a dict of groups and users that are currently sharing items with a given user
    If spatial_only is True, only models which inherit from the Feature class will be reflected here
    returns something like {'our_group': {'group': <Group our_group>, 'users': [<user1>, <user2>,...]}, ... }
    """
    groups_sharing = {}

    for model_class in registered_models:
        shared_objects = model_class.objects.shared_with_user(user)
        for group in user.groups.all():
            # Unless overridden, public shares don't show up here
            if group.name in settings.SHARING_TO_PUBLIC_GROUPS and not include_public:
                continue
            # User has to be staff to see these
            if group.name in settings.SHARING_TO_STAFF_GROUPS and not user.is_staff:
                continue
            group_objects = shared_objects.filter(sharing_groups=group)
            user_list = []
            for gobj in group_objects:
                if gobj.user not in user_list and gobj.user != user:
                    user_list.append(gobj.user)

            if len(user_list) > 0:
                if group.name in groups_sharing.keys():
                    for user in user_list:
                        if user not in groups_sharing[group.name]['users']:
                            groups_sharing[group.name]['users'].append(user)
                else:
                    groups_sharing[group.name] = {'group':group, 'users': user_list}
    if len(groups_sharing.keys()) > 0:
        return groups_sharing
    else:
        return None

def get_model_by_uid(muid):
    for model in registered_models:
        if model.model_uid() == muid:
            return model
    raise Exception("No model with model_uid == `%s`" % muid)

def get_feature_by_uid(uid):
    applabel, modelname, id = uid.split('_')
    id = int(id)
    model = get_model_by_uid("%s_%s" % (applabel,modelname))
    instance = model.objects.get(pk=int(id))
    return instance
