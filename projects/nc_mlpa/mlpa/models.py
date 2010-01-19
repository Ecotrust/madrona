from django.contrib.gis.db import models
from lingcod.mpa.models import Mpa
from lingcod.manipulators.manipulators import *
from manipulators import *
from lingcod.array.models import MpaArray as BaseArray
from lingcod.studyregion.models import StudyRegion
import lingcod.intersection.models as int_models
from django.contrib.gis import geos
from django.contrib.gis.measure import A, D

#THE FOLLOWING ESTUARIES RELATED CLASSES ARE INCOMPLETE AND HAVE BEEN ADDED HERE FOR TESTING PURPOSES!!!
class EstuariesManager(models.GeoManager):
    def current(self):
        return self.all()
    
    @property    
    def geometry_collection(self):
        """return a geometry collection containing all of the estuary geometries.  NOTE: This is NOT clipped to the study region
        so the area of this collection will be much larger than the actual estuarine area."""
        gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        for est in self.all():
            gc.append(est.geometry)
        return gc
        
    @property
    def multipolygon_clipped(self):
        """return a multipolygon that has been clipped to the study region."""
        unclipped_estuaries = self.geometry_collection
        sr = StudyRegion.objects.current()
        return unclipped_estuaries.intersection(sr.geometry)
        
    @property
    def total_area_sq_mi(self):
        """return the total area of estuary within the study region in square miles"""
        return A(sq_m=self.multipolygon_clipped.area).sq_mi
        
    def contains_centroid(self, geom):
        """return true if the centroid of the supplied geometry falls inside the unclipped estuaries or false if it does not.
        This method can be used to determine if an mpa is estuarine."""
        return self.geometry_collection.contains(geom.centroid)
        
class Estuaries(models.Model):
    """Model used for representing Estuaries

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================

        ``name``                Name of the Estuary
                                
        ``geometry``            PolygonField representing the Estuary boundary
                                
        ======================  ==============================================
    """   
    name = models.CharField(max_length=255,default='unknown',verbose_name="Estuary Name")
    geometry = models.PolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Estuary boundary")
    objects = EstuariesManager()
    
    def __unicode__(self):
        return self.name

class MpaArray(BaseArray):
    description = models.TextField(blank=True)
    proposed = models.BooleanField(help_text="Submit as a Proposal to the I-Team", default=False)
    public_proposal = models.BooleanField(help_text="Mark this MPA as a public proposal (can be viewed without an account)", default=False)
    
    @property
    def opencoast_mpa_set(self):
        """return a query set that includes the MPAs within the array that are not estuarine."""
        return self.mpa_set.filter(is_estuary=False)
        
    @property
    def estuarine_mpa_set(self):
        """return a query set that includes the MPAs within the array that are not estuarine."""
        return self.mpa_set.filter(is_estuary=True)
        
    @property
    def opencoast_geometry_collection(self):
        """return a geometry collection of all non-estuarine MPAs in the array"""
        gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        for mpa in self.opencoast_mpa_set:
            gc.append(mpa.geometry_final)
        return gc
        
    @property
    def estuarine_geometry_collection(self):
        """return a geometry collection of all estuarine MPAs in the array"""
        gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        for mpa in self.estuarine_mpa_set:
            gc.append(mpa.geometry_final)
        return gc
    
class Lop(models.Model):
    name = models.CharField(max_length=255, verbose_name='level of protection')
    value = models.IntegerField()
    run = models.BooleanField()
        
    def __unicode__(self):
        return self.name
        
class AllowedMethod(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return self.name #':'.join([self.name, self.description])

class AllowedPurpose(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return self.name

class AllowedTarget(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return self.name #': '.join([self.name, self.description])

class LopRule(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.description.split('\n')[0])

class AllowedUse(models.Model):
    target = models.ForeignKey(AllowedTarget)
    method = models.ForeignKey(AllowedMethod)
    lop = models.ForeignKey(Lop, null=True, blank=True)
    purpose = models.ForeignKey(AllowedPurpose)
    rule = models.ForeignKey(LopRule, null=True, blank=True)

    class Meta:
        ordering = ['target']

    def save(self):
        if self.lop==None and self.rule==None:
            raise Exception, "You must specify an LOP or a Rule.  Both can not be blank."
        elif self.lop!=None and self.rule!=None:
            raise Exception, "You can specify an LOP or a Rule.  You may not specify both."
        else:
            super(AllowedUse, self).save()

    def __unicode__(self):
        return ': '.join([self.target.name, self.method.name, self.purpose.name])

    def flat_attr(self):
        return ':'.join([self.target.name, self.method.name, self.purpose.name])


from lingcod.mpa.models import MpaDesignation


# Maps the relationship between MPA designations and what allowedpurposes can
# be permitted there
class DesignationsPurposes(models.Model):
    designation = models.ForeignKey(MpaDesignation, unique=True)
    purpose = models.ManyToManyField(AllowedPurpose, help_text='Which allowed use purposes are available for this designation', blank=True)

    def __unicode__(self):
        return self.designation.name #':'.join([self.name, self.description]) 
        
class GoalCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return self.name #':'.join([self.name, self.description]) 


class GoalObjective(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    goal_category = models.ForeignKey(GoalCategory)

    class Meta:
        ordering = ['goal_category', 'name', ]

    def __unicode__(self):
        return self.name

    def flat_attr(self):
        return self.goal_category.name + ':' + self.name

class MlpaMpa(Mpa):
    """Model used for representing marine protected areas as part of the MLPA initiative

        ======================          ==============================================
        Attribute                       Description
        ======================          ==============================================
        ``array``                       ``MlpaArray`` group that the ``Mpa`` belongs 
                                        to

        ``goal_objectives``             Goals and regional objectives for this Mpa.

        ``designation``                 Your choice of designation affects what 
                                        allowed uses you can assign to your MPA.
                                        For more information, see <a 
                                        target="_blank" 
                                        href="http://www.dfg.ca.gov/mlpa/defs.asp" 
                                        />the Department of Fish and Game 
                                        website</a>

        ``sharing_groups``              One or more ``Group``'s that this Mpa is 
                                        shared in

        ``allowed_uses``                User-defined set of apecies that are 
                                        allowed to be target within this MPA

        ``is_estuary``                  Whether or not this Mpa is located in an 
                                        estuary

        ``cluster_id``                  ??

        ``boundary_description``        Written description of the MPA boundaries

        ``specific_objective``          In one or two sentences, please describe 
                                        how this MPA contributes to meeting the 
                                        goals of your planning process. This 
                                        section should describe the main reason 
                                        that an MPA is proposed in this location.        

        ``design_considerations``       Please list below any additional 
                                        considerations that have been taken into 
                                        account in the design of this MPA. 
                                        Potential information to describe here 
                                        might include socioeconomic or feasibility 
                                        considerations.

        ``comments``                    User comments on this Mpa

        ``group_before_edits``          ?? Used for existing MPAs

        ``evolution``                   Staff MPA Evolution notes

        ``dfg_feasibility_guidance``    Feasibility Guidance

        ``sat_explanation``             SAT Explanation

        ``other_regulated_activities``  Proposed regulations that apply to activities 
                                        other than extractive use. For instance, 
                                        proposed regulations that prohibit anchoring, 
                                        wading, etc may be included here.

        ``other_allowed_uses``          Proposed regulations that apply to 
                                        extractive use activities NOT listed in the 
                                        drop down menu above. These regulations should 
                                        be listed here in the form of proposed allowed 
                                        uses.                                               
        ======================          ==============================================
    """       
    #array = models.ForeignKey(Arrays, null=True, blank=True, verbose_name="Array", help_text="""Here you can choose an Array to add this MPA to. If your list of Arrays is empty, you'll need to create one by choosing "Create Array" from the MPA menu.""")
    #goal_objectives = ManyToManyFieldWithCustomColumns(DomainGoalObjective,db_table='x_mpas_goal_objectives',db_column='goal_objective_id',null=True, blank=True, verbose_name="Goals and Regional Objectives")
    #designation = models.ForeignKey(DomainMpaDesignation, verbose_name="MPA Designation", help_text="""Your choice of designation affects what allowed uses you can assign to your MPA.For more information, see <a target="_blank" href="http://www.dfg.ca.gov/mlpa/defs.asp" />the Department of Fish and Game website</a>.""", blank=True, null=True)
    #sharing_groups = models.ManyToManyField(Group, blank=True)
    #allowed_uses = ManyToManyFieldWithCustomColumns(DomainAllowedUse,db_table='x_mpas_allowed_uses',db_column='allowed_uses_id',null=True, blank=True, verbose_name="Allowed Uses")

    allowed_uses = models.ManyToManyField(AllowedUse,null=True, blank=True, verbose_name="Allowed Uses", help_text="useful help text.")
    is_estuary = models.BooleanField(verbose_name="Is Estuary?")
    cluster_id = models.IntegerField(null=True, blank=True)
    boundary_description = models.TextField(null=True, blank=True, verbose_name="Boundary Description", help_text="Written description of the MPA boundaries.")
    specific_objective = models.TextField(verbose_name='Site Specific Rationale', null=True, blank=True, help_text="""In one or two sentences, please describe how this MPA contributes to meeting the goals of your planning process. This section should describe the main reason that an MPA is proposed in this location.""")
    design_considerations = models.TextField(null=True, blank=True, verbose_name="Other considerations for MPA design", help_text="""Please list below any additional considerations that have been taken into account in the design of this MPA. Potential information to describe here might include socioeconomic or feasibility considerations.""")
    comments = models.TextField(null=True, blank=True)
    group_before_edits = models.CharField(max_length=255, null=True, blank=True) # for existing mpas
    evolution = models.TextField(null=True, blank=True, verbose_name='Staff MPA Evolution Notes')    
    dfg_feasability_guidance = models.TextField(null=True, blank=True, verbose_name="Feasability Guidance")
    sat_explanation = models.TextField(null=True, blank=True, verbose_name="SAT Explanation")
    other_regulated_activities = models.TextField(null=True, blank=True, verbose_name='Other Regulated Activities', help_text="""List here any proposed regulations that apply to activities other than extractive use. For instance, proposed regulations that prohibit anchoring, wading, etc may be included here.""")
    other_allowed_uses = models.TextField(null=True, blank=True, verbose_name="Additional Proposed Allowed Uses", help_text="""List here proposed regulations that apply to extractive use activities NOT listed in the drop down menu above. These regulations should be listed here in the form of proposed allowed uses. Please note that the allowed uses listed above have been reviewed by the MLPA Science Advisory Team (SAT) and assigned a level of protection that is used in several MarineMap reporting functions. Any additional allowed uses listed below can not be assigned a level of protection until they are reviewed by the SAT. Thus, including any allowed uses below will disable reporting functions in MarineMap that use levels of protection. """)
    goal_objectives = models.ManyToManyField(GoalObjective,null=True, blank=True, verbose_name="Goals and Regional Objectives")

    class Meta:
        # db_table = u'mlpa_mpa' <- don't need this!
        permissions = (
            ("can_share_mpas", "Can Share Mpas"),
        )

    class Options:
        manipulators = [ ClipToStudyRegionManipulator, ClipToEstuariesManipulator, ]

    def __str__(self):
        return self.name
        
    def save(self):
        self.delete_cached_lop()
        self.is_estuary = self.in_estuary()
        super(MlpaMpa,self).save()
        self.lop # calling this will calculate and store the LOP
        
    @property
    def lop(self):
        try:
            mpa_lop = MpaLop.objects.get(mpa=self)
        except MpaLop.DoesNotExist:
            mpa_lop = MpaLop()
            mpa_lop.mpa = self
            mpa_lop.lop, mpa_lop.reason = self.calculate_lop()
            mpa_lop.save()
        return mpa_lop.lop

    @property
    def lop_reason(self):
        try:
            mpa_lop = MpaLop.objects.get(mpa=self)
        except MpaLop.DoesNotExist:
            self.lop
            mpa_lop = MpaLop.objects.get(mpa=self)
        return mpa_lop.reason
        
    def delete_cached_lop(self):
        MpaLop.objects.filter(mpa=self).delete()
        
    def in_estuary(self):
        """docstring for in_estuary"""
        return Estuaries.objects.contains_centroid(self.geometry_final)
        
    def calculate_lop(self):
        reasons = {
            1: 'MPA has no assigned designation',
            2: 'SMRs are always assigned a very high LOP',
            3: 'derived from allowed uses',
            4: 'text in other allowed uses field'
        }
        if self.designation == None:
            return None, reasons[1]
        elif self.designation.acronym.lower() == 'smr': 
            return Lop.objects.get(value=10), reasons[2]
        else:
            if self.other_allowed_uses:
                return None, reasons[4]
            else:
                # set this variable to the highest value LOP to initialize it and then track the lowest encountered
                lowest_lop = Lop.objects.all().order_by('-value')[0]
                for au in self.allowed_uses.all():
                    if au.lop: # if this is null it means it's a rule and needs to be evaluated
                        if au.lop.value < lowest_lop.value:
                            lowest_lop = au.lop
                    elif au.rule:
                        # The naming convention is that 'Rule 1' will correspond to MlpaMpa method lop_rule_1.  'Rule 2' -> lop_rule_2, etc.
                        method_name = 'lop_' + au.rule.name.lower().replace(' ','_')
                        rule_lop = self.__getattribute__(method_name)()
                        if rule_lop.value < lowest_lop.value:
                            lowest_lop = rule_lop
                return lowest_lop, reasons[3]
                        
    def lop_rule_1(self):
        """If there is more than 0.2 sq miles in the 0 - 50m depth range, LOP = 6.  Else, LOP = 8"""
        osc = int_models.OrganizationScheme.objects.get(name='lessthan50m')
        results = osc.transformed_results(self.geometry_final)
        shallow_area = results[results.keys()[0]]['result']
        if shallow_area > 0.2:
            lop_value = 6
        else:
            lop_value = 8
        return Lop.objects.get(value=lop_value)

class MpaLop(models.Model):
    """(MpaLop description)"""
    mpa = models.ForeignKey(MlpaMpa)
    lop = models.ForeignKey(Lop,blank=True,null=True)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = []
        verbose_name, verbose_name_plural = "", "s"

    def __unicode__(self):
        return '%s - %s' % (mpa.name,lop.name)

    