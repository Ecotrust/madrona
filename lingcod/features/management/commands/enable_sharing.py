from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from lingcod.common.utils import enable_sharing 


class Command(BaseCommand):
    help = "Configures the permissions to allow sharing between groups"

    def handle(self, **options):
        enable_sharing()
        print """
The site is now configured to allow sharing. To grant this permission to any groups, go to the shell and type:

    from lingcod.common.utils import enable_sharing
    from django.contrib.auth.models import Group
    g = Groups.objects.get(name="My Group")
    enable_sharing(g)

"""
