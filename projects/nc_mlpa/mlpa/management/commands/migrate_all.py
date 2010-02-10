from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
import os
from os.path import join
#import json
from django.utils import simplejson as json


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to json files containing Allowed Uses, Group, User, Mpa, and Array data from marinemap v1."),
    )
    help = """Migrate data from fixtures to marinemap v2 

    Use the following command on the northcoast tool to generate the json fixtures:
    
        python manage.py create_mm1_migration_fixtures --dest <path where json fixtures should be stored>
    
    """
    help = """Migrate fixture data to marinemap v2 database tables"""
    
    args = '[json]'
    
    def handle(self, json_path, **options):
        try:
            uses_path = os.path.join( json_path, 'allowed_uses.json' )
            uses_command = "python manage.py migrate_allowed_uses --json %s" % uses_path
            print 'Migrating data from Allowed Uses fixture: %s' % uses_path
            os.system( uses_command )
            
            groups_path = os.path.join( json_path, 'groups.json' )
            groups_command = "python manage.py migrate_groups --json %s" % groups_path
            print 'Migrating data from Groups fixture: %s' % groups_path
            os.system( groups_command )
            
            users_path = os.path.join( json_path, 'users.json' )
            users_command = "python manage.py migrate_users --json %s" % users_path
            print 'Migrating data from Users fixture: %s' % users_path
            os.system( users_command )
            
            mpas_path = os.path.join( json_path, 'mpas.json' )
            mpas_command = "python manage.py migrate_mpas --json %s" % mpas_path
            print 'Migrating data from Mpas fixture: %s' % mpas_path
            os.system( mpas_command )
            
            arrays_path = os.path.join( json_path, 'arrays.json' )
            arrays_command = "python manage.py migrate_arrays --json %s" % arrays_path
            print 'Migrating data from Arrays fixture: %s' % arrays_path
            os.system( arrays_command )
            
        except Exception, e:
            print "There was an exception: %s. Some fixtures were not generated." % e.message
        