from django.contrib.gis.db import models
from lingcod.mpa.models import Mpa
from lingcod.manipulators.manipulators import *
from manipulators import *

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
    
    is_estuary = models.NullBooleanField(null=True, blank=True, verbose_name="Is Estuary?")
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
    
    class Meta:
        db_table = u'mlpa_mpa'
        permissions = (
            ("can_share_mpas", "Can Share Mpas"),
        )
        
    class Options:
        manipulators = [ ClipToStudyRegionManipulator, ClipToEstuariesManipulator, ]
        #manipulators = [ ClipToEstuariesManipulator ]
        #manipulators = [ ClipToShapeManipulator ]
        #manipulators = [ ClipToGraticuleManipulator ]
        
    def __str__(self):
        return self.name

#THE FOLLOWING ESTUARIES RELATED CLASSES ARE INCOMPLETE AND HAVE BEEN ADDED HERE FOR TESTING PURPOSES!!!
class EstuariesManager(models.GeoManager):
    def current(self):
        return self.all()
        
class Estuaries(models.Model):
    """Model used for representing Estuaries

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================

        ``name``                Name of the Estuary
                                
        ``geometry``            PolygonField representing the Estuary boundary
                                
        ======================  ==============================================
    """   
    name = models.TextField(verbose_name="Estuary Name")
    
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Estuary boundary")
       
    objects = EstuariesManager()
    
    class Meta:
        db_table = u'mm_estuaries' 