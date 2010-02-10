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
            help="Path to a json file containing User information from marinemap v1."),
    )
    help = """Migrate new and modified allowed uses from marinemap v1

    Use the following command on the northcoast tool to get the json file:
    NOTE:   the following command would not run on my personal machine, even after I updated my code from the repository and restored my db from a recent (2 day old) production level backup
            it threw the following Error: Unable to serialize database: column x_mpas_allowed_uses.domainalloweduse_id does not exist
            the command does however run on the production server, which I guess is all that really counts in the end anyway
        
        python manage.py dumpdata mmapp.Arrays > arrays.json
        
    NOTE:  This command will not update mpas that have a more recent date_modified timestamp in mm2 than in mm1
    
    """
    args = '[json]'
    
    def handle(self, json_path, **options):
        transaction.enter_transaction_management()
        transaction.managed(True)
        f = open(json_path)
        data = json.load(f)
        arrays = list()
        try:
            for item in data:
                f = item['fields']
                if item['model'] == 'mmapp.arrays':
                    #create Array object
                    array = MpaArray( pk=item['pk'], name=f['name'], date_created=f['date_created'], date_modified=f['date_modified'], description=f['description'] )
                    #add User
                    user = User.objects.filter(id=f['user']) 
                    if len(user) != 0:
                        array.user = user[0]
                    else:
                        print 'User: %s was not found.' % f['user']
                        print 'array %s will not be migrated to mm2!' % array.id
                        continue
                    #add Sharing Groups
                    for group_id in f['sharing_groups']:
                        group = Group.objects.filter( id=group_id )
                        if len(group) != 0:
                            array.sharing_groups.add( group[0] )
                        else:
                            print 'Sharing Group: %s was not found.' % group_id
                            print 'Array %s will have to be manually adjusted to include this group.' % array.id
                    #add Public Group when Public Proposal is True
                    if f['public_proposal'] == True:
                        group = Group.objects.get( id=999999 )
                        array.sharing_groups.add( group )
                    #check to see if this array already exists in the mm2 db
                    mm2_array = None
                    mm2_lookUp = MpaArray.objects.filter(id=array.pk)
                    if len( mm2_lookUp ) != 0: #there is already an array with this id in the mm2 db
                        mm2_array = mm2_lookUp[0]
                        from datetime import datetime
                        mm1_date_modified = datetime.strptime(array.date_modified, "%Y-%m-%d %H:%M:%S")
                    #only update array if it is not already in the database
                    #or if the last_modified timestamp is more recent in mm1 than mm2
                    if mm2_array is None or mm1_date_modified > mm2_array.date_modified: 
                        arrays.append( array )
                    
            for item in arrays:
                print "saving array %s to db" % item.id
                item.save()
            transaction.commit()
            print "Found %s new or modified arrays." % (len(arrays), )
        except Exception, e:
            print "There was an exception: %s. No database operations were committed." % e.message
            transaction.rollback()
        
        transaction.leave_transaction_management()