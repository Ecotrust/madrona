from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from mlpa.models import AllowedUse, AllowedPurpose, AllowedMethod, AllowedTarget, Lop, LopRule
import json
from django.db import transaction


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to a json file containing DomainLopRule, Lop, DomainAllowedUse, DomainAllowedTarget, DomainAllowedPurpose, and DomainAllowedMethod information from marinemap v1."),
    )
    help = """Migrate new and modified allowed uses from marinemap v1

    Use the following command on the northcoast tool to get the json file:
    
        python manage.py dumpdata mmapp.DomainAllowedMethod mmapp.DomainAllowedTarget mmapp.DomainAllowedUse mmapp.DomainAllowedPurpose mmapp.Lop mmapp.DomainLopRule > allowed_uses.json
    
    """
    args = '[json]'
    
    def handle(self, json_path, **options):
        transaction.enter_transaction_management()
        transaction.managed(True)
        f = open(json_path)
        data = json.load(f)
        uses = list()
        targets = list()
        purposes = list()
        methods = list()
        lop = list()
        rules = list()
        try:
            for item in data:
                f = item['fields']
                if item['model'] == 'mmapp.domainloprule':
                    lop.append( LopRule(pk=item['pk'], name=f['name'], description=f['description']) )
                if item['model'] == 'mmapp.lop':
                    lop.append( Lop(pk=item['pk'], name=f['name'], value=f['value'], run=f['run']) )
                if item['model'] == 'mmapp.domainalloweduse':
                    uses.append(AllowedUse(pk=item['pk'], target_id=f['target'], method_id=f['method'], purpose_id=f['purpose'], lop_id=f['lop'], rule_id=f['rule']))
                if item['model'] == 'mmapp.domainallowedpurpose':
                    purposes.append( AllowedPurpose(pk=item['pk'], name=f['name'], description=f['description']) )
                if item['model'] == 'mmapp.domainallowedtarget':
                    targets.append( AllowedTarget(pk=item['pk'], name=f['name'], description=f['description']) )
                if item['model'] == 'mmapp.domainallowedmethod':
                    methods.append( AllowedMethod(pk=item['pk'], name=f['name'], description=f['description']) )
        
            for l in targets, purposes, methods, lop, rules, uses:
                for item in l:
                    item.save()
            transaction.commit()
        except:
            print "There was an exception. No database operations were committed."
            transaction.rollback()

        print "Found %s allowed uses." % (len(uses), )
        print "Found %s lop rules." % (len(rules), )
        print "Found %s levels of protection." % (len(lop), )
        print "Found %s allowed methods." % (len(methods), )
        print "Found %s allowed purposes." % (len(purposes), )
        print "Found %s allowed targets." % (len(targets), )
        transaction.leave_transaction_management()