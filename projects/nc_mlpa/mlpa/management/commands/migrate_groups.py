from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.auth.models import Group, Permission
#import json
from django.utils import simplejson as json
from django.db import transaction


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to a json file containing Group information from marinemap v1."),
    )
    help = """Migrate new and modified groups from marinemap v1

    Use the following command on the mm1 server to get the json file:
    
        python manage.py dumpdata auth.group > groups.json
           
    """
    args = '[json]'
    
    def handle(self, json_path, **options):
        #The following permissions are those that are expected to be present for the migration
        #This permission mapping is necessary as the ids are all that are provided by the mm1 fixture
        #and the ids are different from mm1 to mm2
        mm1_permissions_mapping = { 1364: 'add_group', 1436: 'can_share_arrays', 1447: 'can_share_mpas', 1601: 'view_ecotrustlayerlist' }
        transaction.enter_transaction_management()
        transaction.managed(True)
        f = open(json_path)
        data = json.load(f)
        groups = list()
        try:
            for item in data:
                f = item['fields']
                if item['model'] == 'auth.group':
                    #create group object
                    group = Group(pk=item['pk'], name=f['name'])
                    #add permissions
                    for mm1_permission_id in f['permissions']:
                        if mm1_permission_id in mm1_permissions_mapping:
                            mm2_permission_codename = mm1_permissions_mapping[mm1_permission_id]
                            permission = Permission.objects.filter(codename=mm2_permission_codename)
                            if len(permission) != 0:
                                group.permissions.add( permission[0] )
                        else:
                            print 'This migrating script is not prepared to handle permission %s (this id is from mm1, not mm2)' % mm1_permission_id
                            print 'Group %s will not be given permission %s' % (group.id, mm1_permission_id)
                            if mm1_permission_id == 1437:
                                print 'Note: Permission 1437 (Can See Proposal Submissions) is not yet a permission in mm2, so you can probably just ignore.'
                            else:
                                print 'You will likely want to add that permission to the group manually (via the admin).'
                    #add group to the list
                    groups.append( group )
                    
            for item in groups:
                item.save()
            transaction.commit()
            print "Found %s groups." % (len(groups), )
        except Exception, e:
            print "There was an exception in the migrate_groups script: %s" % e.message
            print "No Groups were committed to MM2."
            transaction.rollback()
        
        transaction.leave_transaction_management()