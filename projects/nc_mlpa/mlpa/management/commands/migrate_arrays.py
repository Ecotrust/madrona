from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from mlpa.models import MlpaMpa, MpaArray
from django.contrib.auth.models import User, Group
#import json
from django.utils import simplejson as json
from django.db import transaction


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to a json file containing Array information from marinemap v1."),
    )
    help = """Migrate new and modified Arrays from marinemap v1

    Use the following command on the mm1 server to get the json file:
        
        python manage.py dumpdata mmapp.Arrays > arrays.json
        
    NOTE:  This command will not update arrays that have a more recent date_modified timestamp in mm2 than in mm1
    
    """
    args = '[json]'

    def handle(self, json_path, **options):
        from DataMigration import Migrator
        migrator = Migrator()
        try:
            migrator.migrate_arrays(json_path, options['verbosity'])
        except:
            print 'The migrate_arrays command has terminated.'