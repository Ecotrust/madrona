from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from mlpa.models import MlpaMpa, AllowedUse
from lingcod.mpa.models import MpaDesignation
from django.contrib.auth.models import User, Group
#import json
from django.utils import simplejson as json
from django.db import transaction


class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--json', action='store', dest='json_path', default=False,
            help="Path to a json file containing User information from marinemap v1."),
        make_option('--verb', action='store', dest='verbose', default=False,
            help="If activated then "),
    )
    help = """Migrate new and modified allowed uses from marinemap v1

    Use the following command on the northcoast tool to get the json file:
    NOTE:   the following command would not run on my personal machine, even after I updated my code from the repository and restored my db from a recent (2 day old) production level backup
            it threw the following Error: Unable to serialize database: column x_mpas_allowed_uses.domainalloweduse_id does not exist
            the command does however run on the production server, which I guess is all that really counts in the end anyway
        
        python manage.py dumpdata mmapp.Mpas > mpas.json
        
    NOTE:  This command will not update mpas that have a more recent date_modified timestamp in mm2 than in mm1
    
    """
    args = '[json]'
    
    def handle(self, json_path, **options):
        transaction.enter_transaction_management()
        transaction.managed(True)
        f = open(json_path)
        data = json.load(f)
        num_mpas = 0
        for item in data:
            try:
                f = item['fields']
                if item['model'] == 'mmapp.mpas':
                    #the following use lop rules (had allowed uses in [582, 583, 587, 588]):  [73163, 73165, 73167, 73178, 73179, 73180, 73182, 73183, 73184, 73185, 73186, 73203, 73207, 73217, 73222, 73223, 73225, 73226, 73252, 73261, 73266, 73267, 73269, 73277, 73279, 73301, 73305, 73441, 73524, 73525, 73545, 73575, 73577, 73579, 73582, 73583, 73586, 73599, 73600, 73605, 73613, 73683, 73711, 73844, 73865, 73899, 73900, 73901, 73902, 73903, 73904, 73905, 73910, 73912, 73938, 73980]:
                    #not sure why the following had issues [73925, 73928]:
                    #create Mpa object
                    mpa = MlpaMpa(pk=item['pk'], name=f['name'], date_created=f['date_created'], date_modified=f['date_modified'], is_estuary=f['is_estuary'], cluster_id=f['cluster_id'], boundary_description=f['boundary_description'], specific_objective=f['specific_objective'], design_considerations=f['design_considerations'], comments=f['comments'], group_before_edits=f['group_before_edits'], evolution=f['evolution'], dfg_feasability_guidance=f['dfg_feasability_guidance'], sat_explanation=f['sat_explanation'], other_regulated_activities=f['other_regulated_activities'], other_allowed_uses=f['other_allowed_uses'], geometry_orig=f['geometry'], geometry_final=f['geometry_clipped'])
                    #add User
                    user = User.objects.filter(id=f['user']) 
                    if len(user) != 0:
                        mpa.user = user[0]
                    else:
                        print 'User: %s was not found.' % f['user']
                        print 'Mpa %s will not be migrated to mm2!' % mpa.id
                        continue
                    #add Designation
                    designation = MpaDesignation.objects.filter(id=f['designation']) 
                    if len(designation) != 0:
                        mpa.designation = designation[0]
                    elif f['designation'] is not None:
                        print 'Designation: %s was not found.' % f['designation']
                        print 'Mpa %s will have to be manually adjusted to include this designation.' % mpa.id
                    #add Allowed Uses
                    for use_id in f['allowed_uses']:
                        use = AllowedUse.objects.filter(id=use_id)
                        if len(use) != 0: 
                            mpa.allowed_uses.add( use[0] )
                        else:
                            print 'Allowed Use: %s was not found.' % use_id
                            print 'Mpa %s will have to be manually adjusted to include this use.' % mpa.id
                    #add Sharing Groups
                    for group_id in f['sharing_groups']:
                        group = Group.objects.filter(id=group_id)
                        if len(group) != 0:
                            mpa.sharing_groups.add( group[0] )
                        else:
                            print 'Sharing Group: %s was not found.' % group_id
                            print 'Mpa %s will have to be manually adjusted to include this group.' % mpa.id
                    #check to see if this mpa already exists in the mm2 db
                    mm2_mpa = None
                    mm2_lookUp = MlpaMpa.objects.filter(id=mpa.pk)
                    if len(mm2_lookUp) != 0: #there is already an mpa with this id in the mm2 db
                        mm2_mpa = mm2_lookUp[0]
                        from datetime import datetime
                        mm1_date_modified = datetime.strptime(mpa.date_modified, "%Y-%m-%d %H:%M:%S")
                    #only update mpa if it is not already in the database
                    #or if the last_modified timestamp is more recent in mm1 than mm2
                    if mm2_mpa is None or mm1_date_modified > mm2_mpa.date_modified: 
                        try:
                            if options['verbosity'] == '2':
                                print 'adding %s to db' % mpa.id
                            mpa.save()
                            transaction.commit()
                            num_mpas += 1
                        except Exception, e:
                            print "There was an exception while saving Mpa %s to the database:" %s
                            print e.message
                            transaction.rollback()
                            raise
            except:
                print "There was an exception. Mpa %s was not added to the db." % mpa.id
                continue
        print "Found %s new or modified mpas." % (num_mpas, )
        transaction.leave_transaction_management()