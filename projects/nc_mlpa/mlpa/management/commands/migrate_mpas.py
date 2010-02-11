from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to a json file containing Mpa information from marinemap v1."),
    )
    help = """Migrate new and modified Mpas from MarineMap v1

    Use the following command on the mm1 server to get the json file:
    NOTE:   the following command would not run on my personal machine, even after I updated my code from the repository and restored my db from a recent (2 day old) production level backup
            it threw the following Error: Unable to serialize database: column x_mpas_allowed_uses.domainalloweduse_id does not exist
            the command does however run on the production server, which I guess is all that really counts in the end anyway
        
        python manage.py dumpdata mmapp.Mpas > mpas.json
        
        the -v 2 option/argument can also be appended to the above command to generate additional output
        
    NOTE:  This command will not update mpas that have a more recent date_modified timestamp in mm2 than in mm1
    
    """
    args = '[json]'
    
    def handle(self, json_path, **options):
        from DataMigration import Migrator
        migrator = Migrator()
        try:
            migrator.migrate_mpas(json_path, options['verbosity'])
        except:
            print 'The migrate_mpas command has terminated.'