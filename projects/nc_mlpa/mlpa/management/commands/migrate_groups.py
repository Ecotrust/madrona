from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to a json file containing Group information from marinemap v1."),
    )
    help = """Migrate new and modified Groups from MarineMap v1

    Use the following command on the mm1 server to get the json file:
    
        python manage.py dumpdata auth.group > groups.json
           
    """
    args = '[json]'
    
    def handle(self, json_path, **options):
        from DataMigration import Migrator
        migrator = Migrator()
        try:
            migrator.migrate_groups(json_path)
        except:
            print 'The migrate_groups command has terminated.'