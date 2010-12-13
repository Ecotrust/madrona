from lingcod.common.utils import get_logger
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from lingcod.sharing.models import ShareableContent, get_shareables, SharingError

logger = get_logger()

def validate_sharing(model):
    logger.debug('Validated sharing setup for %s' % (model.__name__,) )

    # Test for fields: user, sharing_groups
    fkfields = [m.name for m in model._meta.fields if m.__class__.__name__ == 'ForeignKey']
    if not 'user' in fkfields:
        raise SharingError("Feature does not contain a 'user' ForeignKey field")

    m2mfields = [m.name for m in model._meta.many_to_many]
    if not 'sharing_groups' in m2mfields:
        raise SharingError("Feature does not contain a 'sharing_groups' ManyToMany field")

    # Test for manager with shared_with_user() method
    if not hasattr(model.objects, 'shared_with_user'):
        raise SharingError("Model's object manager does not have a shared_with_user() method.")

    return True

def sharing_disable(mc, ct):
    # Make sure Feature does NOT have can_share_* permission;
    codename = "can_share_%s" % mc._meta.module_name
    try:
        p = Permission.objects.get(codename=codename)
        logger.debug("Drop can_share Permissions for %r" % ct)
        p.delete()
    except Permission.DoesNotExist:
        pass
    # Make sure Feature does NOT have ShareableContent ct
    try:
        sc = ShareableContent.objects.get(shared_content_type=ct)
        logger.debug("Drop ShareableContent for %r" % ct)
        sc.delete()
    except ShareableContent.DoesNotExist:
        pass
    # Confirm NOT in get_shareables
    if get_shareables().has_key(mc.__name__.lower()):
        raise SharingError("%s is not a shared feature but somehow snuck into get_shareables()" % mc.__name__)
            
def sharing_enable(mc, ct):
    logger.debug("Insert can_share Permissions and ShareableContent for %r" % ct)
    # Make sure ShareableContent instance exists
    # TODO FeatureContainers and arrays
    try:
        sc = ShareableContent.objects.get(shared_content_type=ct)
        logger.debug("  ShareableContent already exists for %r - do nothing" % ct)
    except ShareableContent.DoesNotExist:
        logger.debug("  Creating shareableContent for %r" % ct)
        sc = ShareableContent.objects.create(shared_content_type=ct) #container_content_type=array_ct, container_set_property='mpa_set')
        sc.save()
    # Make sure Feature has can_share_* permission;
    codename = "can_share_%s" % mc._meta.module_name
    try:
        p = Permission.objects.get(codename=codename)
        logger.debug("  can_share Permission already exists for %r - do nothing" % mc)
    except Permission.DoesNotExist:
        logger.debug("  Creating permissions for %s and ct # %s (%r)" % (codename, ct.id, ct))
        p = Permission.objects.create(codename=codename,name=codename.replace('_',' '),content_type_id=ct.id)
        p.save()
    # Confirm in get_shareables
    if not get_shareables().has_key(mc.__name__.lower()):
        raise SharingError("%s uses ShareableGeoManager but is not in get_shareables()" % mc.__name__)
