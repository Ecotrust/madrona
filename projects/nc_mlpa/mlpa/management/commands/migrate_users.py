from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to a json file containing User information from marinemap v1."),
    )
    help = """Migrate new and modified Users from MarineMap v1

    Use the following command on the mm1 server to get the json file:
    
        python manage.py dumpdata auth.user > users.json
        
    NOTE:  This command will not update users that have a more recent last_login timestamp in mm2 than in mm1
    
    """
    args = '[json]'
    
    def handle(self, json_path, **options):
        from DataMigration import Migrator
        migrator = Migrator()
        try:
            migrator.migrate_users(json_path)
        except:
            print 'The migrate_users command has terminated.'