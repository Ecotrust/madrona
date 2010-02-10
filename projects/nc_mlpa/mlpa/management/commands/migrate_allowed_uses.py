from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from mlpa.models import AllowedUse, AllowedPurpose, AllowedMethod, AllowedTarget, Lop, LopRule
#import json
from django.utils import simplejson as json
from django.db import transaction


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to a json file containing DomainLopRule, Lop, DomainAllowedUse, DomainAllowedTarget, DomainAllowedPurpose, and DomainAllowedMethod information from marinemap v1."),
    )
    help = """Migrate new and modified allowed uses from marinemap v1

    Use the following command on the mm1 server to get the json file:
    
        python manage.py dumpdata mmapp.DomainAllowedMethod mmapp.DomainAllowedTarget mmapp.DomainAllowedUse mmapp.DomainAllowedPurpose mmapp.Lop mmapp.DomainLopRule > allowed_uses.json
    
    """
    args = '[json]'
    
    def handle(self, json_path, **options):
        from DataMigration import Migrator
        migrator = Migrator()
        try:
            migrator.migrate_allowed_uses(json_path)
        except:
            print 'The migrate_allowed_uses command has terminated.'