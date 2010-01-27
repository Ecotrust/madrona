from django.contrib.gis.db import models
from lingcod.common.utils import *
from mlpa.models import *
from lingcod.bioregions.models import *
import lingcod.intersection.models as int_models
import lingcod.replication.models as rep_models
from django.conf import settings
from django.contrib.gis import geos
from django.contrib.gis.measure import A, D
from django.db import transaction

class ClusterManager(models.GeoManager):
    def build_clusters_for_array_by_lop(self,array,lop,with_hab=True):
        # get rid of the old ones
        self.filter(array=array,lop=lop).delete()
        
        mpas = array.clusterable_mpa_set.filter(mpalop__lop__value__gte=lop.value)
        clustered = []
        
        for mpa in mpas:
            if mpa in clustered:
                continue
            else:
                new_cl = Cluster(lop=lop,array=array)
                new_cl.save() # have to save before we can add mpas to the mpa_set
                new_cl.mpa_set.add(mpa)
                clustered.append(mpa)
            gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
            gc.append(mpa.geometry_final)
            while mpas.exclude(pk=mpa.pk).exclude(pk__in=[c.pk for c in clustered]).filter(geometry_final__dwithin=(gc,D(m=settings.CLUSTER_THRESHOLD))):
                close_and_unclustered = mpas.exclude(pk=mpa.pk).exclude(pk__in=[c.pk for c in clustered]).filter(geometry_final__dwithin=(gc,D(m=settings.CLUSTER_THRESHOLD)))
                for m in close_and_unclustered:
                    new_cl.mpa_set.add(m)
                    clustered.append(m)
                    gc.append(m.geometry_final)
            else:
                if new_cl.area_sq_mi >= settings.MIN_CLUSTER_SIZE:
                    new_cl.save(with_hab=with_hab)
                else:
                    new_cl.delete()
        return self.filter(array=array,lop=lop)
                
    def build_clusters_for_array(self,array,with_hab=True):
        lops = Lop.objects.filter(run=True)
        for lop in lops:
            self.build_clusters_for_array_by_lop(array,lop,with_hab)
        return Cluster.objects.filter(array=array)
        
    def calculate_habitat_info(self):
        for cl in self.all():
            cl.save(with_hab=True)
            
            
class Cluster(models.Model):
    array = models.ForeignKey(get_array_class())
    mpa_set = models.ManyToManyField(get_mpa_class())
    lop = models.ForeignKey(Lop)
    bioregion = models.ForeignKey(Bioregion,null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    objects = ClusterManager()
    
    def __unicode__(self):
        return '%s LOP Cluster from %s containing %i MPAs' % (self.lop.name,self.array.name,self.mpa_set.count())
    
    def save(self, with_hab=False, *args, **kwargs):
        super(Cluster,self).save(*args,**kwargs)
        self.bioregion = self.get_bioregion()
        super(Cluster,self).save(*args,**kwargs)
        if with_hab:
            self.calculate_habitat_info()
    
    @property
    def geometry_collection(self):
        gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        for mpa in self.mpa_set.all():
            gc.append(mpa.geometry_final)
        return gc
        
    @property
    def area_sq_mi(self):
        return A(sq_m=self.geometry_collection.area).sq_mi
    
    @property
    def geo_sort(self):
        return self.geometry_collection.centroid.y
        
    def calculate_habitat_info(self):
        rs = rep_models.ReplicationSetup.objects.get(org_scheme__name=settings.SAT_OPEN_COAST)
        results = rs.analyze_single_item(self.geometry_collection)
        for d in results.values():
            chi = ClusterHabitatInfo()
            chi = chi.fill_attributes(self,d)
        
    def get_bioregion(self):
        return Bioregion.objects.which_bioregion(self.geometry_collection)
        
class ClusterHabitatInfo(models.Model):
    cluster = models.ForeignKey(Cluster)
    habitat = models.ForeignKey(int_models.FeatureMapping)
    replicate = models.NullBooleanField(null=True,blank=True)
    result = models.FloatField()
    units = models.CharField(null=True,blank=True, max_length=255)
    additional_required = models.FloatField(null=True,blank=True)
    sort = models.FloatField()
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    
    class Meta:
        ordering = ['sort']
    
    def __unicode__(self):
        return self.habitat.name
    
    @property
    def info_dict(self):
        r = {}
        r['habitat'] = self.habitat.name
        r['replicate'] = self.replicate
        r['result'] = self.result
        r['additional_required'] = self.additional_required
        r['sort'] = self.sort
        return r
        
    def fill_attributes(self, cluster, hab_result):
        """
        Given a hab_result dictionary like this:
        {'additional_required': 0.0,
          'feature_map_id': 1,
          'org_scheme_id': 1,
          'percent_of_total': 0.44132429282682328,
          'replicate': True,
          'result': 1.77191378592,
          'sort': 1.0,
          'units': u'miles'}
        fill in attributes.
        """
        hab = int_models.FeatureMapping.objects.get(pk=hab_result['feature_map_id'])
        self.cluster = cluster
        self.habitat = hab
        self.replicate = hab_result['replicate']
        self.sort = hab_result['sort']
        self.additional_required = hab_result['additional_required']
        self.result = hab_result['result']
        self.units = hab_result['units']
        self.save()