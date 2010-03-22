from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option

from lingcod.sharing.models import * 
from lingcod.common.utils import get_mpa_class, get_array_class
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.conf import settings


class Command(BaseCommand):
    help = "Configures the sharing framework for default MPA and Array behavior"

    def handle(self, **options):
        try:
            mpaclass = get_mpa_class()
            arrayclass = get_array_class()
        except:
            print "MPA_CLASS or ARRAY_CLASS is undefined"
            return

        # First register the mpas and arrays as shareable content types
        try:
            mpa_ct = ContentType.objects.get_for_model(mpaclass)
            array_ct = ContentType.objects.get_for_model(arrayclass)

            if len(ShareableContent.objects.filter(shared_content_type=mpa_ct)) == 0:
                share_mpa = ShareableContent.objects.create(shared_content_type=mpa_ct, 
                                                        container_content_type=array_ct,
                                                        container_set_property='mpa_set')
            else:
                print "MPA already added as SharedContent"

            if len(ShareableContent.objects.filter(shared_content_type=array_ct)) == 0:
                share_array = ShareableContent.objects.create(shared_content_type=array_ct)
            else:
                print "Array already added as SharedContent"
        except:
            print "Could not register your mpa and/or array class as shareable content types"
            return

        # Default groups
        try:
            to_public_groups = Group.objects.filter(name__in=settings.SHARING_TO_PUBLIC_GROUPS)
            to_staff_groups = Group.objects.filter(name__in=settings.SHARING_TO_STAFF_GROUPS)
        except:
            print "Sharing groups defined in settings don't exist"
            return
        
        # Then set the permissions on the default groups
        shareables = get_shareables()
        for to_pub_group in to_public_groups:
            to_pub_group.permissions.add(shareables[array_ct.natural_key()[1]][1])
        for to_staff_group in to_staff_groups:
            to_staff_group.permissions.add(shareables[array_ct.natural_key()[1]][1])
            to_staff_group.permissions.add(shareables[mpa_ct.natural_key()[1]][1])
    
        out = """
        MarineMap is now configured for default MPA and Array sharing. You can...

         * create new groups
         * add the can_share_mpa and can_share_array permissions to group
         * add users to group

        And the users can share MPAs and Arrays. Also, the sharing groups defined in settings 
        (SHARING_TO_PUBLIC_GROUPS and SHARING_TO_STAFF_GROUPS) are ready to use.
        """

        print out
