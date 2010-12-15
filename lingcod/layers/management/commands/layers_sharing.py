from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option

from lingcod.sharing.models import * 
from lingcod.sharing.utils import * 
from lingcod.layers.models import PrivateLayerList, PrivateSuperOverlay
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.conf import settings


class Command(BaseCommand):
    help = "Configures the sharing framework for private layers"

    def register_as_shareable(self, obj):
        #First register the layers as shareable content types
        ct = ContentType.objects.get_for_model(obj)

        if len(ShareableContent.objects.filter(shared_content_type=ct)) == 0:
            share = ShareableContent.objects.create(shared_content_type=ct)
        else:
            print "Content Type %r already added as SharedContent" % ct

        # Default groups
        try:
            to_public_groups = []
            to_staff_groups = []
            for g in settings.SHARING_TO_PUBLIC_GROUPS:
                grp, created = Group.objects.get_or_create(name=g)
                if created:
                    print "Created group '%s'" % grp.name
                else:
                    print "Groups '%s' already present" % grp.name
                to_public_groups.append(grp)
            for g in settings.SHARING_TO_STAFF_GROUPS:
                grp, created = Group.objects.get_or_create(name=g)
                if created:
                    print "Created group '%s'" % grp.name
                else:
                    print "Groups '%s' already present" % grp.name
                to_staff_groups.append(grp)
        except:
            print "Sharing groups defined in settings were not configured properly."
            return
        
        # Then set the permissions on the default groups
        shareables = get_shareables()
        for to_pub_group in to_public_groups:
            to_pub_group.permissions.add(shareables[ct.natural_key()[1]][1])
        for to_staff_group in to_staff_groups:
            to_staff_group.permissions.add(shareables[ct.natural_key()[1]][1])
    
    def handle(self, **options):
        self.register_as_shareable(PrivateLayerList)
        self.register_as_shareable(PrivateSuperOverlay)

        out = """
        MarineMap is now configured for sharing private layers and superoverlays. You can...

         * create new groups
         * add the can_share_privatelayerlist permission to group
         * add users to group

        And the users can share Private Layers. Also, the sharing groups defined in settings 
        (SHARING_TO_PUBLIC_GROUPS and SHARING_TO_STAFF_GROUPS) are ready to use.
        """

        print out
        
