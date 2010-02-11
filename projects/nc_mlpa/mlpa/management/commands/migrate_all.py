from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
import os, sys
from os.path import join


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to json files containing Allowed Uses, Group, User, Mpa, and Array data from marinemap v1."),
    )
    help = """Migrate data from MarineMap v1 fixtures to MarineMap v2 Database

    Use the following command on the mm1 server to generate the json fixtures:
    
        python manage.py create_mm1_migration_fixtures --dest <path where json fixtures should be stored>
    
    Move the resulting fixtures over to the mm2 server and then execute this command via the following:
        
        python manage.py migrate_all --json <path to fixtures>/
        
        the -v 2 option/argument can also be appended to the above command to get more output from the mpa and array migrations
    """
    help = """Migrate fixture data to marinemap v2 database tables"""
    
    args = '[json]'
    
    def handle(self, json_path, **options):
        from DataMigration import Migrator
        migrator = Migrator()
        
        try:
            uses_path = os.path.join( json_path, 'allowed_uses.json' )
            print 'Migrating data from Allowed Uses fixture: %s' % uses_path
            migrator.migrate_allowed_uses(uses_path)
        except:
            print("An exception was raised during the migrate_allowed_uses script.")
            print("Data Migration has halted.")
            sys.exit()
             
        try:
            groups_path = os.path.join( json_path, 'groups.json' )
            print 'Migrating data from Groups fixture: %s' % groups_path
            migrator.migrate_groups(groups_path)
        except:
            print("An exception was raised during the migrate_groups script.")
            print("Data Migration has halted.")
            sys.exit()
            
        try:
            users_path = os.path.join( json_path, 'users.json' )
            print 'Migrating data from Users fixture: %s' % users_path
            migrator.migrate_users(users_path)
        except:
            print("An exception was raised during the migrate_users script.")
            print("Data Migration has halted.")
            sys.exit()
            
        try:
            mpas_path = os.path.join( json_path, 'mpas.json' )
            print 'Migrating data from Mpas fixture: %s' % mpas_path
            migrator.migrate_mpas(mpas_path, options['verbosity'])
        except:
            print("An exception was raised during the migrate_mpas script.")
            print("Data Migration has halted.")
            sys.exit()
            
        try:
            arrays_path = os.path.join( json_path, 'arrays.json' )
            print 'Migrating data from Arrays fixture: %s' % arrays_path
            migrator.migrate_arrays(arrays_path, options['verbosity'])
        except:
            print("An exception was raised during the migrate_arrays script.")
            print("Data Migration has halted.")
            sys.exit()
        