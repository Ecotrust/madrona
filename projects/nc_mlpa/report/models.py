from django.contrib.gis.db import models
from lingcod.common.utils import *
from mlpa.models import *
from lingcod.bioregions.models import *
from django.conf import settings
from django.contrib.gis import geos
from django.contrib.gis.measure import A, D

class ClusterManager(models.GeoManager):
    def build_clusters_for_array_by_lop(self,array,lop):
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
                    new_cl.save()
                else:
                    new_cl.delete()
        return self.filter(array=array,lop=lop)
                
    def build_clusters_for_array(self,array):
        lops = Lop.objects.filter(run=True)
        for lop in lops:
            self.build_clusters_for_array_by_lop(array,lop)
        return Cluster.objects.filter(array=array)
            
            
class Cluster(models.Model):
    array = models.ForeignKey(get_array_class())
    mpa_set = models.ManyToManyField(get_mpa_class())
    lop = models.ForeignKey(Lop)
    bioregion = models.ForeignKey(Bioregion,null=True,blank=True)
    objects = ClusterManager()
    
    def __unicode__(self):
        return '%s LOP Cluster from %s containing %i MPAs' % (self.lop.name,self.array.name,self.mpa_set.count())
    
    @property
    def geometry_collection(self):
        gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        for mpa in self.mpa_set.all():
            gc.append(mpa.geometry_final)
        return gc
        
    @property
    def area_sq_mi(self):
        return A(sq_m=self.geometry_collection.area).sq_mi
        
    def get_bioregion(self):
        return Bioregion.objects.which_bioregion(self.geometry_collection)