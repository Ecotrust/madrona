# make sure any new manipulators get added to lingcod.manipulators' additionalManipulators
from mlpa.manipulators import *
from django.contrib.gis.db import models
from lingcod.mpa.models import Mpa
from lingcod.manipulators.manipulators import *
from lingcod.array.models import MpaArray as BaseArray
from lingcod.studyregion.models import StudyRegion
from lingcod.intersection import models as int_models
from lingcod.replication import models as rep_models
from lingcod.depth_range.models import depth_range as depth_range_calc
from django.contrib.gis import geos
from django.contrib.gis.measure import A, D
from django.db import transaction
from django.template.defaultfilters import dictsort


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
    short_name = models.CharField(blank=True, null=True, max_length=8, help_text='This name will be used as the file name for exported items like shapefiles, spreadsheets, etc. Eight characters, max.')
    
    @property
    def opencoast_mpa_set(self):
        """return a query set that includes the MPAs within the array that are not estuarine."""
        return self.mpa_set.filter(is_estuary=False)
        
    @property
    def estuarine_mpa_set(self):
        """return a query set that includes the MPAs within the array that are not estuarine."""
        return self.mpa_set.filter(is_estuary=True)
        
    @property
    def unassigned_lop_opencoast_mpas(self):
        """Return a query set of open coast mpas with unassigned LOP or an empty query set if all have LOPs."""
        pk_list = []
        for m in self.opencoast_mpa_set:
            if m.lop==None:
                pk_list.append(m.pk)
        return self.mpa_set.filter(pk__in=pk_list)
        
    @property
    def unassigned_lop_mpas(self):
        """Return a query set of all mpas with unassigned LOP or an empty query set if all have LOPs."""
        pk_list = []
        for m in self.mpa_set.all():
            if m.lop==None:
                pk_list.append(m.pk)
        return self.mpa_set.filter(pk__in=pk_list)
        
    @property
    def clusterable_mpa_set(self):
        pk_list = []
        for mpa in self.opencoast_mpa_set:
            if mpa.can_be_clustered:
                pk_list.append(mpa.pk)
        return self.opencoast_mpa_set.filter(pk__in=pk_list)
            
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
        
    @property
    @transaction.commit_on_success
    def clusters(self):
        """
        Use this method to get clusters used in replication analysis (those with an LOP set to run).
        If clusters exist and they have a newer date modified than the array, retrieve them.
        If they do exist but are older, regenerate them.
        If they don't exist, generate them.
        Don't do anything about the habitat reports attached to the clusters (in other words
        if those reports have already been generated, they'll be there otherwise, they won't)
        """
        from report.models import Cluster
        lops = Lop.objects.filter(run=True)
        qs = self.cluster_set.filter(date_modified__gt=self.date_modified,lop__in=lops)
        if not qs:
            qs = Cluster.objects.build_clusters_for_array(self,with_hab=False)
        return qs
        
    @property
    @transaction.commit_on_success
    def clusters_at_lowest_lop(self):
        from report.models import Cluster
        lop = Lop.objects.all().order_by('value')[0]
        qs = self.cluster_set.filter(date_modified__gt=self.date_modified,lop=lop)
        if not qs:
            qs = Cluster.objects.build_clusters_for_array_by_lop(self,lop,with_hab=False)
        return qs
        
    @property
    @transaction.commit_on_success
    def clusters_with_habitat(self):
        """
        If don't exist, generate them with habitat info.  If clusters exist but are out of date,
        regenerated them with habitat info.  If clusters exist and are new enough, check the 
        habitat info.  If the hab_info is in date return the whole slough.  If hab_info is out of
        date, regenerate it for the existing clusters and send it all back.

        ...well, really we're just returning the clusters but the hab info will be available as 
        cluster.clusterhabitatinfo_set.all()
        """
        from report.models import Cluster, ClusterHabitatInfo
        qs = self.cluster_set.filter(date_modified__gt=self.date_modified)
        if not qs: # there were no up to date clusters for this array
            qs = Cluster.objects.build_clusters_for_array(self,with_hab=True)
        else:  # check if habitat calculations are up to date
            habinfo = ClusterHabitatInfo.objects.filter(cluster__in=qs)
            rs = rep_models.ReplicationSetup.objects.get(org_scheme__name=settings.SAT_OPEN_COAST_REPLICATION)
            #print "habinfo: ",
            #print habinfo.count()
            #print "blah: ",
            #print rs.habitatthreshold_set.count() * qs.count()
            if habinfo.count() != (rs.habitatthreshold_set.count() * qs.count()):
                habinfo.delete()
                for cl in qs:
                    cl.calculate_habitat_info()
            elif True in [ self.date_modified > h.date_modified for h in habinfo ]: # see if array was modified more recently than hab results
                for cl in qs:
                    cl.calculate_habitat_info()
        return qs.order_by('lop__value')
        
    @property
    def summary_by_designation(self):
        sr_area = StudyRegion.objects.current().area_sq_mi
        by_desig = {}
        desig_list = list(MpaDesignation.objects.all())
        if self.mpa_set.filter(designation=None):
            desig_list.append(None)
        for desig in desig_list:
            if desig:
                acronym = desig.acronym
                sort_num = desig.sort
            else:
                acronym = None
                sort_num = 250
            mpas = self.mpa_set.filter(designation=desig)
            by_desig[sort_num] = {
                'designation': acronym,
                'count': mpas.count(),
                'area': mpas.summed_area_sq_mi,
                'percent_of_sr': 100 * ( mpas.summed_area_sq_mi / sr_area )
            }
        # add in totals for all designations
        by_desig[255] = {
            'designation': 'All MPAs',
            'count': self.mpa_set.count(),
            'area': self.mpa_set.summed_area_sq_mi,
            'percent_of_sr': 100 * ( self.mpa_set.summed_area_sq_mi / sr_area )
        }
        return by_desig
        
    @property
    def summary_by_lop(self):
        sr_area = StudyRegion.objects.current().area_sq_mi
        by_lop = []
        lop_list = list( Lop.objects.filter(value__gt=2) )
        if None in [ m.lop for m in self.mpa_set ]:
            lop_list.append(None)
        for lop in lop_list:
            if lop:
                disp_name = lop.name
                key_num = lop.value * -1
            else:
                disp_name = 'N/A'
                key_num = -1
            mpas = self.mpa_set.filter(lop_table__lop=lop)
            # use the additive inverse of the lop value so the dict will be sorted correctly in the template
            sub_dict = {
                'sort': key_num,
                'lop': disp_name,
                'count': mpas.count(),
                'area': mpas.summed_area_sq_mi,
                'percent_of_sr': 100 * ( mpas.summed_area_sq_mi / sr_area )
            }
            by_lop.append(sub_dict)
        # for some PITA reason we have to bin together lops with a value of 2 or less
        low_mpas = self.mpa_set.filter(lop_table__lop__value__lte=2)
        sub_dict = {
            'sort': -2,
            'lop': 'Moderate-low or Low',
            'count': low_mpas.count(),
            'area': low_mpas.summed_area_sq_mi,
            'percent_of_sr': 100 * ( low_mpas.summed_area_sq_mi / sr_area )
        }
        by_lop.append(sub_dict)
        # add in totals for all lops
        mpas = self.mpa_set.all()
        sub_dict = {
            'sort': 0,
            'lop': 'All Mpas',
            'count': mpas.count(),
            'area': mpas.summed_area_sq_mi,
            'percent_of_sr': 100 * ( mpas.summed_area_sq_mi / sr_area )
        }
        by_lop.append(sub_dict)
        return dictsort(by_lop,'sort')
        
    @property
    def shapefile_export_query_set(self):
        from report.models import MpaShapefile
        for mpa in self.mpa_set.all():
            mpa.export_version # update these records
        qs = MpaShapefile.objects.filter(array=self)
        return qs
        
    # @property
    # def replication_report(self):
    #     lops = Lop.objects.filter(run=True)
    #     results = {}
    #     for lop in lops:
    #         results[lop.value] = self.replication_report_by_lop(lop)
    #     return results
    # 
    # def replication_report_by_lop(self,lop):
    #     from lingcod.replication.models import ReplicationSetup
    #     rs = ReplicationSetup.objects.get(org_scheme__name=settings.SAT_OPEN_COAST)
    #     input_dict = self.cluster_habitat_input_by_lop(lop)
    #     return rs.analyze(input_dict)
    #     
    # def clusters_by_lop(self, lop):
    #     from report.models import Cluster
    #     qs = Cluster.objects.build_clusters_for_array_by_lop(self, lop)
    #     return qs
    #     
    # def cluster_habitat_input_by_lop(self, lop, regenerate_clusters=True):
    #     if regenerate_clusters:
    #         clusters = self.clusters_by_lop(lop)
    #     else:
    #         clusters = self.cluster_set.filter(lop=lop)
    #     input_dict = {}
    #     for cluster in clusters:
    #         input_dict[cluster.pk] = cluster.geometry_collection
    #     return input_dict
    
class Lop(models.Model):
    name = models.CharField(max_length=255, verbose_name='level of protection')
    value = models.IntegerField()
    run = models.BooleanField()
        
    class Meta:
        ordering = ['-value']
        
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
    draft = models.BooleanField(default=False, help_text='If the LOP or rule for this allowed use has not been approved by the SAT, then it should be marked as draft.')

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

default_boundary_description = """North Boundary:  [please describe, e.g. "north latitude 36 21.0 to the extent of state waters"]
West Boundary:  [please describe, e.g. "the state water boundary"]
South Boundary: [please describe, e.g. "line due west of the northern tip of Sammy's Rock: at ~33 21.029"]
East Boundary:   [please describe, e.g. "mean high tide line"]"""

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
    boundary_description = models.TextField(null=True, blank=True, default = default_boundary_description,
            verbose_name="Boundary Description", help_text="Written description of the MPA boundaries.")
    specific_objective = models.TextField(verbose_name='Site-Specific Rationale', null=True, blank=True, help_text="""In one or two sentences, please describe how this MPA contributes to meeting the goals of the Marine Life Protection Act. This section should describe the main reason that an MPA is proposed in this location.""")
    design_considerations = models.TextField(null=True, blank=True, verbose_name="Other considerations for MPA design", help_text="""Please list below any additional considerations that have been taken into account in the design of this MPA. Potential information to describe here might include more details on the design, designation, and may reference socioeconomic, feasibility issues, or other specific considerations that were taken into account.""")
    comments = models.TextField(null=True, blank=True)
    group_before_edits = models.CharField(max_length=255, null=True, blank=True) # for existing mpas
    evolution = models.TextField(null=True, blank=True, verbose_name='Staff MPA Evolution Notes')    
    dfg_feasability_guidance = models.TextField(null=True, blank=True, verbose_name="Feasability Guidance")
    sat_explanation = models.TextField(null=True, blank=True, verbose_name="SAT Explanation")
    other_regulated_activities = models.TextField(null=True, blank=True, verbose_name='Other Regulated Activities', help_text="""List here any proposed regulations that apply to activities other than extractive use. For instance, proposed regulations that prohibit anchoring, wading, etc may be included here.""")
    other_allowed_uses = models.TextField(null=True, blank=True, verbose_name="Additional Proposed Allowed Uses", help_text="""List here proposed regulations that apply to extractive use activities NOT listed in the drop down menu above. These regulations should be listed here in the form of proposed allowed uses. Please note that the allowed uses listed above have been reviewed by the MLPA Science Advisory Team (SAT) and assigned a level of protection that is used in several MarineMap reporting functions. Any additional allowed uses listed below can not be assigned a level of protection until they are reviewed by the SAT. Thus, including any allowed uses below will disable reporting functions in MarineMap that use levels of protection. """)
    goal_objectives = models.ManyToManyField(GoalObjective,null=True, blank=True, verbose_name="Goals and Regional Objectives")

    class Meta(Mpa.Meta):
        # db_table = u'mlpa_mpa' <- don't need this!
        ordering = ['-geo_sort__number']

    class Options:
        manipulators = [ ClipToStudyRegionManipulator, ClipToEstuariesManipulator, ]

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        from report.models import Cluster
        self.delete_cached_lop()
        self.apply_manipulators()
        self.is_estuary = self.in_estuary()
        if self.array:
            Cluster.objects.filter(array=self.array).delete()
            self.array.save() # We have to do this so the modification date on the array is updated
        super(MlpaMpa,self).save(*args, **kwargs)
        mgs, created = MpaGeoSort.objects.get_or_create(mpa=self)
        mgs.save()
        self.lop # calling this will calculate and store the LOP
        
    def delete(self, *args, **kwargs):
        if self.array:
            self.array.save() # Change modification date on array to make caching work
        super(MlpaMpa,self).delete(*args, **kwargs)
        
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
        
    @property
    def can_be_clustered(self):
        if self.is_estuary:
            return False
        else:
            return True
            
            ## LOP filtering occurs elsewhere so it's redundant to do it here
            ## plus we need to cluster at lower LOPs for array level geographic reporting
            # run_lops = Lop.objects.filter(run=True)
            #             if self.lop in run_lops:
            #                 return True
            #             else:
            #                 return False
            
    @property
    def bioregion(self):
        from lingcod.bioregions.models import Bioregion
        return Bioregion.objects.which_bioregion(self.geometry_final)
        
    @property
    def depth_range(self):
        min_depth, max_depth = depth_range_calc(self.geometry_final)
        return {'min':min_depth,'max':max_depth}
        
    @property
    def sort_num(self):
        if self.geo_sort:
            return self.geo_sort.number
        else:
            return 0
            
    @property
    def area_sq_mi(self):
        return A(sq_m=self.geometry_final.area).sq_mi
        
    @property
    def export_version(self):
        """
        Port the MPAs attributes over to the MpaShapefile model so we can export the shapefile.
        geometry = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,blank=True,null=True)
        name = models.CharField(max_length=255)
        name_short = models.CharField(blank=True, max_length=255,null=True)
        desig_name = models.CharField(blank=True, max_length=80, null=True)
        desig_acro = models.CharField(blank=True, max_length=80, null=True)
        lop = models.CharField(blank=True, max_length=80, null=True)
        lop_numeric = models.IntegerField(blank=True, null=True)
        mpa = models.OneToOneField(MlpaMpa, related_name="mpa")
        array = models.ForeignKey(MpaArray, null=True, blank=True)
        array_name = models.CharField(blank=True, max_length=255, null=True)
        allowed_uses = models.TextField(blank=True, null=True)
        other_allowed_uses = models.TextField(blank=True, null=True)
        other_regulated_activities = models.TextField(blank=True, null=True)
        author = models.CharField(blank=True, max_length=255,null=True)
        area_sq_mi = models.FloatField(blank=True,null=True)
        mpa_modification_date = models.DateTimeField(blank=True, null=True)
        date_modified = models.DateTimeField(blank=True, null=True, auto_now_add=True)
        """
        from report.models import MpaShapefile
        msf, created = MpaShapefile.objects.get_or_create(mpa=self)
        if created or msf.date_modified < self.date_modified:
            msf.name = self.name
            msf.mpa_id_num = self.pk
            msf.geometry = self.geometry_final
            desig_list = [ des.acronym for des in MpaDesignation.objects.all() ]
            desig_list.extend( [ d.lower() for d in desig_list ]) # add in lower case versions just in case
            short_name = self.name
            for acr in desig_list:
                short_name = short_name.replace(acr,'').strip()
            msf.name_short = short_name
            if self.designation:
                msf.desig_name = self.designation.name
                msf.desig_acro = self.designation.acronym
            if self.lop:
                msf.lop = self.lop.name
                msf.lop_numeric = self.lop.value
            if self.array:
                msf.array = self.array
                msf.array_name = self.array.name
            msf.allowed_uses = self.get_allowed_uses_text()
            msf.other_allowed_uses = self.other_allowed_uses
            msf.other_regulated_activities = self.other_regulated_activities
            msf.author = self.user.username
            msf.area_sq_mi = self.area_sq_mi
            msf.mpa_modification_date = self.date_modified
            msf.save()
        return msf
        
    @property
    def export_query_set(self):
        from report.models import MpaShapefile
        # This is a round about way of gettting a queryset with just this one MPA
        return MpaShapefile.objects.filter(pk=self.export_version.pk)
        
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
            4: 'text in other allowed uses field',
            5: 'there are no LOPs entered in the system',
            6: 'LOP taken from LopOverride table'
        }
        # Look for an entry in the LopOverride table.  If there's a value there it trumps all other considerations
        try:
            lop = LopOverride.objects.get(mpa=self).lop
            return lop, reasons[6]
        except LopOverride.DoesNotExist:
            pass
        
        # set this variable to the highest value LOP to initialize it and then track the lowest encountered
        try:
            lowest_lop = Lop.objects.all().order_by('-value')[0]
        except IndexError:
            return None, reasons[5]
            
        if self.designation == None:
            return None, reasons[1]
        elif self.designation.acronym.lower() == 'smr': 
            return Lop.objects.get(value=10), reasons[2]
        else:
            if self.other_allowed_uses:
                return None, reasons[4]
            else:    
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
                        
    def shallow_area(self):
        osc = int_models.OrganizationScheme.objects.get(name='lessthan50m')
        results = osc.transformed_results(self.geometry_final)
        return results[results.keys()[0]]['result']
        
    def lop_rule_1(self):
        """If there is more than 0.2 sq miles in the 0 - 50m depth range, LOP = 4.  Else, LOP = 8"""
        if self.shallow_area() > 0.2:
            lop_value = 4
        else:
            lop_value = 8
        return Lop.objects.get(value=lop_value)
        
    def lop_rule_2(self):
        if self.in_estuary():
            lop = Lop.objects.get(value=6)
        else:
            lop = Lop.objects.get(value=2)
        return lop
        
    def lop_rule_3(self):
        """If there is more than 0.2 sq miles in the 0 - 50m depth range, LOP = 6.  Else, LOP = 8"""
        if self.shallow_area() > 0.2:
            lop = Lop.objects.get(value=6)
        else:
            lop = Lop.objects.get(value=8)
        return lop
    
    def short_g_o_str(self, really_short=False):
        gostr = ''
        qset = self.goal_objectives.get_query_set()
        qset_goal_ids = [q['goal_category_id'] for q in qset.values('goal_category_id')]
        gids_unique = []
        for q in qset_goal_ids:
            if q not in gids_unique:
                gids_unique.append(q)
                cat = GoalCategory.objects.get(pk=q)
                gostr = gostr + cat.name + ": ("
                qset_f = qset.filter(goal_category=cat).values('name')
                for q in qset_f:
                    gostr = gostr + str( q['name'] )
                    #if not the last one
                    if q != qset_f[qset_f.count() - 1]:
                        gostr = gostr + ","
                        if not really_short:
                            gostr = gostr + ' '
                gostr = gostr + ") "
        if really_short:
            gostr = gostr.replace('oal ','')
            gostr = gostr.replace('bjective ','-')
        return gostr
        
    def get_allowed_uses_text(self):
        if self.designation == MpaDesignation.objects.get(acronym='SMR'):
            return 'Take of all living marine resources is prohibited.'
        else:
            a = ''
            qset = self.allowed_uses.get_query_set()
            comm = qset.filter(purpose__name='commercial')
            rec = qset.filter(purpose__name='recreational')
            if not qset: # no allowed uses specified
                return 'No allowed uses were specified in MarineMap drop down menu.'
            elif (comm and not rec) or (rec and not comm): # only commercial uses or only recreational uses
                if comm:
                    take_type = 'commercial'
                    qs = comm
                elif rec:
                    take_type = 'recreational'
                    qs = rec
                a = 'The take of all living marine resources is prohibited except the %s take of ' % take_type
                cnt = qs.count()
                for q in qs:
                    a += q.target.name + ' by ' + q.method.name
                    cnt -= 1
                    if cnt > 1:
                        a += '; '
                    elif cnt:
                        a += '; and '
                    else:
                        a += '.'
                return a
            else: # There are both commercial and recreational allowed uses
                a = 'The take of all living marine resources is prohibited except:\n'
                i = 1
                for qs in [rec,comm]:
                    a += '%i. The %s take of ' % (i, qs[0].purpose.name)
                    i += 1
                    cnt = qs.count()
                    for q in qs:
                        a += q.target.name + ' by ' + q.method.name
                        cnt -= 1
                        if cnt > 1:
                            a += '; '
                        elif cnt:
                            a += '; and '
                        else:
                            a += '.\n'
                return a

class MpaLop(models.Model):
    """(MpaLop description)"""
    mpa = models.OneToOneField(MlpaMpa, related_name="lop_table")
    #mpa = models.ForeignKey(MlpaMpa)
    lop = models.ForeignKey(Lop,blank=True,null=True)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-lop__value']
        verbose_name, verbose_name_plural = "", "s"

    def __unicode__(self):
        if self.lop:
            lop_name = self.lop.name
        else:
            lop_name = 'undetermined'
        return '%s - %s' % (self.mpa.name,lop_name)
        
class LopOverride(models.Model):
    """
    This model is here so that we can manually specify lops for analysis purposes when they can't be automatically
    assigned becuse the allowed uses have not yet been evaluated by the SAT.  If there is an entry in this model for
    a given mpa, the lop will be taken from this table.  In all other cases it will be evaluated according to the 
    allowed uses assigned or left Null if other_allowed_uses are specified.
    
    NOTE: LopOverrides are NOT deleted automatically.  Once entered, they persist until they are manually deleted so you
    should be careful with them.  def them.  They should only be used on MPAs that are not going to change anymore because
    once there is an override, changes to the MPA's allowed uses will NOT cause a change in assigned LOP.
    """
    mpa = models.OneToOneField(MlpaMpa, primary_key=True)
    lop = models.ForeignKey(Lop, null=True, blank=True, verbose_name="Level of Protection")
    
    def __unicode__(self):
        return '%s (id=%i): %s' % (self.mpa.name,self.mpa.pk,self.lop.name)
        
    def save(self, *args, **kwargs):
        super(LopOverride,self).save(*args, **kwargs)
        self.mpa.delete_cached_lop()
        self.lop # will cause the lop to be recalculated using the new override

def load_LopOverride_from_file(file_path, recalculate=True):
    fileReader = csv.reader(open(file_path), delimiter=',')
    for row in fileReader:
        print 'getting mpa: %i' % int(row[0])
        mpa = Mpas.objects.get(pk=int(row[0]))
        lop = Lop.objects.get(value=int(row[1]))
        lop_o, created = LopOverride.objects.get_or_create(mpa=mpa)
        lop_o.lop = lop
        lop_o.save()
        if recalculate:
            mpa.save()
            
class MpaGeoSort(models.Model):
    """The MLPA North Coast study region is a pretty simple shape so we're just going to use the y coordinate to sort the geometries"""
    mpa = models.OneToOneField(MlpaMpa, related_name="geo_sort")
    number = models.FloatField()

    class Meta:
        ordering = ['-number']
        verbose_name, verbose_name_plural = "", "s"

    def __unicode__(self):
        return "%s geographic sort number: %f" % (self.mpa.name,self.number)
        
    def save(self, *args, **kwargs):
        self.number = self.get_sort_number()
        super(MpaGeoSort,self).save()
        
    def get_sort_number(self):
        sort_num = self.mpa.geometry_final.centroid.y
        return sort_num
