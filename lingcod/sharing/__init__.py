from lingcod.common.utils import get_logger
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from lingcod.sharing.models import ShareableContent

logger = get_logger()

class SharingError(Exception):
    pass

def enable_sharing(model):
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
