from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.auth.models import Group
from lingcod.common.utils import enable_sharing 


class Command(BaseCommand):
    help = "Configures the permissions to allow sharing between groups"
    args = '[Group names to grant sharing permissions to ...]'

    option_list = BaseCommand.option_list + (
        make_option('-a', '--all', action='store_true', dest='all',
            help="Enable sharing for ALL current groups"),
        )
    

    def handle(self, *groupnames, **options):
        self.all = options.get('all', False)

        if self.all:
            print "Enabling sharing for all groups..."
            enable_sharing()
            gs = Group.objects.all()
            for g in gs:
                enable_sharing(g)
                print " [DONE]", g.name
            return

        if len(groupnames) > 0:
            print "Enabling sharing for %s groups.." % len(groupnames)
            enable_sharing()
            for gname in groupnames:
                try:
                    g = Group.objects.get(name=gname)
                    enable_sharing(g)
                    print " [DONE]", gname
                except Exception as e:
                    print " [FAILED]", gname
                    print "  ",e
            return 

        enable_sharing()
        print """
The site is now configured to allow sharing. 
For a group to share features, you must grant this permission explictly to group:

    $ python manage.py enable_sharing GroupName "Group Name with Spaces"

OR to grant sharing permissions to all groups:

    $ python manage.py enable_sharing --all
"""
