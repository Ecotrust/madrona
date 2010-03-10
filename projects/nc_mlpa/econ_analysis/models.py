from django.db import models
from mlpa.models import AllowedUse, AllowedTarget
from econ_analysis.managers import *

class FishingImpactAnalysisMap(models.Model):  
        
           
    group_name = models.TextField(verbose_name='User Group Name')
    group_abbr = models.TextField(verbose_name='User Group Abbreviation')
    port_name = models.TextField(verbose_name='Port Name')
    port_abbr = models.TextField(verbose_name='Port Abbreviation')
    species_name = models.TextField(verbose_name='Species Name')
    species_abbr = models.TextField(verbose_name='Species Abbreviation')
    cell_size = models.IntegerField()
    #should this really be 'allowed_'targets??  
    allowed_targets = models.ManyToManyField(AllowedTarget, null=True, blank=True, verbose_name="Fishing Impact Analysis Map Allowed Targets")
    allowed_uses = models.ManyToManyField(AllowedUse, null=True, blank=True, verbose_name="Fishing Impact Analysis Map Allowed Uses")

    objects = FishingImpactAnalysisMapManager()
    
    def __unicode__(self):
        #return unicode("%s : %s : %s" % (self.group_name, self.port_name, self.species_name))
        return ': '.join([self.group_name, self.port_name, self.species_name])
       
    def getGridName(self):
        return self.species_abbr+'_'+self.port_abbr
    
    def getFullName(self):
        return self.group_abbr+'_'+self.species_abbr+'_'+self.port_abbr
        
'''
FishingImpactStats maintains the results of fishing impact analysis precalculations
at the overall and study region level.  These results are then combined with
mpa analysis done real-time.
'''
class FishingImpactStats(models.Model):
    #class Meta:
    #    db_table = u'fishing_impact_stats'    
    map = models.OneToOneField(FishingImpactAnalysisMap)    
    totalCells = models.IntegerField()  #Overall number of cells with fishing value
    srCells = models.IntegerField()     #Number of cells with fishing value in study region
    totalArea = models.FloatField()   #Total fishing area in square miles
    srArea = models.FloatField()      #Fishing area within the study region
    totalValue = models.FloatField()  #Total fishing value overall
    srValue = models.FloatField()     #Fishing value in the study region
    