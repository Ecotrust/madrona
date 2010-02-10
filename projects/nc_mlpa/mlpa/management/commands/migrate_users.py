from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.auth.models import User, Group, Permission
#import json
from django.utils import simplejson as json
from django.db import transaction


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to a json file containing User information from marinemap v1."),
    )
    help = """Migrate new and modified Users from marinemap v1

    Use the following command on the mm1 server to get the json file:
    
        python manage.py dumpdata auth.user > users.json
        
    NOTE:  This command will not update users that have a more recent last_login timestamp in mm2 than in mm1
    
    """
    args = '[json]'
    
    def handle(self, json_path, **options):
        mm1_permissions_mapping = { 1364: 'add_group', 1436: 'can_share_arrays', 1447: 'can_share_mpas', 1601: 'view_ecotrustlayerlist' }
        transaction.enter_transaction_management()
        transaction.managed(True)
        f = open(json_path)
        data = json.load(f)
        users = list()
        try:
            for item in data:
                absent_permissions = list()
                f = item['fields']
                if item['model'] == 'auth.user':
                    #create User object
                    mm1_user = User(pk=item['pk'], username=f['username'], first_name=f['first_name'], last_name=f['last_name'], email=f['email'], password=f['password'], is_staff=f['is_staff'], is_active=f['is_active'], is_superuser=f['is_superuser'], last_login=f['last_login'], date_joined=f['date_joined'])
                    #add Groups
                    for group_id in f['groups']:
                        mm1_user.groups.add( Group.objects.get(id=group_id) )
                    #add permissions
                    for mm1_permission_id in f['user_permissions']:
                        if mm1_permission_id in mm1_permissions_mapping:
                            mm2_permission_codename = mm1_permissions_mapping[mm1_permission_id]
                            permission = Permission.objects.filter(codename=mm2_permission_codename)
                            if len(permission) != 0:
                                mm1_user.user_permissions.add( permission[0] )
                        else:
                            absent_permissions.append( mm1_permission_id )
                    #check to see if this user already exists in the mm2 db
                    mm2_user = None
                    mm2_lookUp = User.objects.filter(id=mm1_user.pk)
                    if len(mm2_lookUp) != 0: #there is already a user with this id in the mm2 db
                        mm2_user = mm2_lookUp[0]
                    if mm2_user is not None and mm2_user.username != mm1_user.username:
                        print "HOUSTON WE HAVE A PROBLEM"
                        print "Users ('%s' from mm1 and '%s' from mm2) have identical IDs (id==%s)." % (mm1_user.username, mm2_user.username, mm2_user.id)
                        print "This should not happen."
                        raise Exception
                    from datetime import datetime
                    mm1_last_login = datetime.strptime(mm1_user.last_login, "%Y-%m-%d %H:%M:%S")
                    #only update user if they are not already in the database
                    #or if they have logged in more recently to mm1 than to mm2
                    if mm2_user is None or mm1_last_login > mm2_user.last_login: 
                        for permission in absent_permissions:
                            print 'This migrating script is not prepared to handle permission %s (this id is from mm1, not mm2)' % permission
                            print 'User %s will not be given permission %s' % (mm1_user.id, permission)
                            print 'You will likely want to add that permission to the user manually (via the admin).'
                        users.append( mm1_user )
                    
            for item in users:
                item.save()
            transaction.commit()
            print "Found %s new or modified users." % (len(users), )
        except Exception, e:
            print "There was an exception in the migrate_users script: %s" % e.message
            print "No Users were committed to MM2."
            transaction.rollback()
        
        transaction.leave_transaction_management()