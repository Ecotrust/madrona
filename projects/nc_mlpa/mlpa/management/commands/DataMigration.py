from mlpa.models import AllowedUse, AllowedPurpose, AllowedMethod, AllowedTarget, Lop, LopRule, MlpaMpa, MpaArray, AllowedUse
from lingcod.mpa.models import MpaDesignation
from django.contrib.auth.models import User, Group, Permission

#import json
from django.utils import simplejson as json
from django.db import transaction

class Migrator:

    def migrate_allowed_uses(self, json_path):
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
                    rules.append( LopRule(pk=item['pk'], name=f['name'], description=f['description']) )
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
            
            #Q: would the following fail if 'uses' were listed first? (uses is dependent on many of the previously listed tables)
            #A: db operations failed when 'uses' was placed first in the list
            for l in targets, purposes, methods, lop, rules, uses:
                for item in l:
                    item.save()
            transaction.commit()
            print "Found %s allowed uses." % (len(uses), )
            print "Found %s lop rules." % (len(rules), )
            print "Found %s levels of protection." % (len(lop), )
            print "Found %s allowed methods." % (len(methods), )
            print "Found %s allowed purposes." % (len(purposes), )
            print "Found %s allowed targets." % (len(targets), )
        except Exception, e:
            print "There was an exception in the migrate_allowed_uses script: %s" % e.message
            print "No Allowed Uses were committed to MM2." 
            transaction.rollback()
            raise 
        
        transaction.leave_transaction_management()
        
    def migrate_groups(self, json_path):
        #The following permissions are those that are expected to be present for the migration
        #This permission mapping is necessary as the ids are all that are provided by the mm1 fixture
        #and the ids are different from mm1 to mm2
        mm1_permissions_mapping = { 1364: 'add_group', 1436: 'can_share_arrays', 1447: 'can_share_mpas', 1601: 'view_ecotrustlayerlist' }
        transaction.enter_transaction_management()
        transaction.managed(True)
        f = open(json_path)
        data = json.load(f)
        groups = list()
        try:
            for item in data:
                f = item['fields']
                if item['model'] == 'auth.group':
                    #create group object
                    group = Group(pk=item['pk'], name=f['name'])
                    #add permissions
                    for mm1_permission_id in f['permissions']:
                        if mm1_permission_id in mm1_permissions_mapping:
                            mm2_permission_codename = mm1_permissions_mapping[mm1_permission_id]
                            permission = Permission.objects.filter(codename=mm2_permission_codename)
                            if len(permission) != 0:
                                group.permissions.add( permission[0] )
                        else:
                            print 'This migrating script is not prepared to handle permission %s (this id is from mm1, not mm2)' % mm1_permission_id
                            print 'Group %s will not be given permission %s' % (group.id, mm1_permission_id)
                            if mm1_permission_id == 1437:
                                print 'Note: Permission 1437 (Can See Proposal Submissions) is not yet a permission in mm2, so you can probably just ignore.'
                            else:
                                print 'You will likely want to add that permission to the group manually (via the admin).'
                    #add group to the list
                    groups.append( group )
                    
            for item in groups:
                item.save()
            transaction.commit()
            print "Found %s groups." % (len(groups), )
        except Exception, e:
            print "There was an exception in the migrate_groups script: %s" % e.message
            print "No Groups were committed to MM2."
            transaction.rollback()
            raise 
        
        transaction.leave_transaction_management()
        
    def migrate_users(self, json_path):
        mm1_permissions_mapping = { 1364: 'add_group', 1436: 'can_share_arrays', 1447: 'can_share_mpas', 1601: 'view_ecotrustlayerlist' }
        transaction.enter_transaction_management()
        transaction.managed(True)
        f = open(json_path)
        data = json.load(f)
        users = list()
        try:
            for item in data:
                absent_permissions = list()
                f = item['fields']
                if item['model'] == 'auth.user':
                    #create User object
                    mm1_user = User(pk=item['pk'], username=f['username'], first_name=f['first_name'], last_name=f['last_name'], email=f['email'], password=f['password'], is_staff=f['is_staff'], is_active=f['is_active'], is_superuser=f['is_superuser'], last_login=f['last_login'], date_joined=f['date_joined'])
                    #add Groups
                    for group_id in f['groups']:
                        mm1_user.groups.add( Group.objects.get(id=group_id) )
                    #add permissions
                    for mm1_permission_id in f['user_permissions']:
                        if mm1_permission_id in mm1_permissions_mapping:
                            mm2_permission_codename = mm1_permissions_mapping[mm1_permission_id]
                            permission = Permission.objects.filter(codename=mm2_permission_codename)
                            if len(permission) != 0:
                                mm1_user.user_permissions.add( permission[0] )
                        else:
                            absent_permissions.append( mm1_permission_id )
                            #print 'This migrating script is not prepared to handle permission %s (this id is from mm1, not mm2)' % mm1_permission_id
                            #print 'User %s will not be given permission %s' % (mm1_user.id, mm1_permission_id)
                            #print 'That permission will have to be added to the user manually'
                    #check to see if this user already exists in the mm2 db
                    mm2_user = None
                    mm2_lookUp = User.objects.filter(id=mm1_user.pk)
                    if len(mm2_lookUp) != 0: #there is already a user with this id in the mm2 db
                        mm2_user = mm2_lookUp[0]
                    if mm2_user is not None and mm2_user.username != mm1_user.username:
                        print "HOUSTON WE HAVE A PROBLEM"
                        print "Users ('%s' from mm1 and '%s' from mm2) have identical IDs (id==%s)." % (mm1_user.username, mm2_user.username, mm2_user.id)
                        print "This should not happen."
                        raise Exception
                    from datetime import datetime
                    mm1_last_login = datetime.strptime(mm1_user.last_login, "%Y-%m-%d %H:%M:%S")
                    #only update user if they are not already in the database
                    #or if they have logged in more recently to mm1 than to mm2
                    if mm2_user is None or mm1_last_login > mm2_user.last_login: 
                        for permission in absent_permissions:
                            print 'This migrating script is not prepared to handle permission %s (this id is from mm1, not mm2)' % permission
                            print 'User %s will not be given permission %s' % (mm1_user.id, permission)
                            print 'You will likely want to add that permission to the user manually (via the admin).'
                        users.append( mm1_user )
                    
            for item in users:
                item.save()
            transaction.commit()
            print "Found %s new or modified users." % (len(users), )
        except Exception, e:
            print "There was an exception in the migrate_users script: %s" % e.message
            print "No Users were committed to MM2."
            transaction.rollback()
            raise 
        
        transaction.leave_transaction_management()
        
    def migrate_mpas(self, json_path, verbosity):
        transaction.enter_transaction_management()
        transaction.managed(True)
        f = open(json_path)
        data = json.load(f)
        num_mpas = 0
        for item in data:
            absent_designations = list()
            absent_uses = list()
            absent_groups = list()
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
                        absent_designations.append( f['designation'] )
                        #print 'Designation: %s was not found.' % f['designation']
                        #print 'Mpa %s will have to be manually adjusted to include this designation.' % mpa.id
                    #add Allowed Uses
                    for use_id in f['allowed_uses']:
                        use = AllowedUse.objects.filter(id=use_id)
                        if len(use) != 0: 
                            mpa.allowed_uses.add( use[0] )
                        else:
                            absent_uses.append( use_id )
                            #print 'Allowed Use: %s was not found.' % use_id
                            #print 'Mpa %s will have to be manually adjusted to include this use.' % mpa.id
                    #add Sharing Groups
                    for group_id in f['sharing_groups']:
                        group = Group.objects.filter(id=group_id)
                        if len(group) != 0:
                            mpa.sharing_groups.add( group[0] )
                        else:
                            absent_groups.append( group_id )
                            #print 'Sharing Group: %s was not found.' % group_id
                            #print 'Mpa %s will have to be manually adjusted to include this group.' % mpa.id
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
                            for designation in absent_designations:
                                print 'Designation: %s was not found in mm2.' % designation 
                                print 'Mpa %s will have to be manually adjusted to include this designation.' % mpa.id
                            for use in absent_uses:
                                print 'Allowed Use: %s was not found in mm2.' % use 
                                print 'Mpa %s will have to be manually adjusted to include this use.' % mpa.id
                            for group in absent_groups:
                                print 'Sharing Group: %s was not found in mm2.' % group 
                                print 'Mpa %s will have to be manually adjusted to include this group.' % mpa.id
                            if verbosity == '2':
                                print 'Adding Mpa %s to MM2' % mpa.id
                            mpa.save()
                            transaction.commit()
                            num_mpas += 1
                        except Exception, e:
                            print "There was an exception while saving Mpa %s to the database:" %s
                            print e.message
                            transaction.rollback()
                            raise
            except:
                print "There was an exception in the migrate_mpas script. Mpa %s was not added to MM2." % mpa.id
                continue
                
        print "Found %s new or modified mpas." % (num_mpas, )
        transaction.leave_transaction_management()
        
    def migrate_arrays(self, json_path, verbosity):
        transaction.enter_transaction_management()
        transaction.managed(True)
        f = open(json_path)
        data = json.load(f)
        arrays = list()
        try:
            for item in data:
                absent_groups = list()
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
                        print 'Array %s will not be migrated to mm2!' % array.id
                        continue
                    #add Sharing Groups
                    for group_id in f['sharing_groups']:
                        group = Group.objects.filter( id=group_id )
                        if len(group) != 0:
                            array.sharing_groups.add( group[0] )
                        else:
                            absent_groups.append( group_id )
                            #print 'Sharing Group: %s was not found.' % group_id
                            #print 'Array %s will have to be manually adjusted to include this group.' % array.id
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
                        for group in absent_groups:
                            print 'Sharing Group: %s was not found in mm2.' % group 
                            print 'Array %s will have to be manually adjusted to include this group.' % array.id
                        arrays.append( array )
                    
            for item in arrays:
                if verbosity == '2':
                    print "Adding Array %s to MM2" % item.id
                item.save()
            transaction.commit()
            print "Found %s new or modified arrays." % (len(arrays), )
        except Exception, e:
            print "There was an exception in the migrate_mpas script: %s" % e.message 
            print "No Arrays were committed to MM2."
            transaction.rollback()
            raise 
        
        transaction.leave_transaction_management()
        
        