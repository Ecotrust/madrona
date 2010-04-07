from django.db import models
from mlpa.models import AllowedUse, AllowedTarget, MlpaMpa
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
    
'''
The following model is used for caching the impact analysis results after they are run for the first time
'''
class FishingImpactResults(models.Model):
    mpa = models.ForeignKey(MlpaMpa, verbose_name="MPA ID")
    group = models.TextField(verbose_name="Group")
    port = models.TextField(verbose_name="Port")
    species = models.TextField(verbose_name="Species")
    perc_value = models.FloatField(verbose_name="Percentage Value affected by MPA")
    perc_area = models.FloatField(verbose_name="Percentage Area affected by MPA", null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
  
'''
The following model is used for storing some of the baseline data relating to the impact analysis 
'''  
class FishingImpactBaselineCost(models.Model):
    species = models.TextField(verbose_name="Species", null=True, blank=True)
    port = models.TextField(verbose_name="Port Name", null=True, blank=True)
    gross_revenue = models.FloatField(verbose_name="Baseline Gross Economic Revenue", null=True, blank=True)
    crew = models.FloatField(verbose_name="Percent of costs related to Crew")
    fuel = models.FloatField(verbose_name="Percent of costs related to Fuel")
    fixed = models.FloatField(verbose_name="Percent of costs that are Fixed")
    percentage_costs = models.FloatField(verbose_name="Total Percentage of Costs", editable=False)
    
    def save(self):
        if self.species is None and self.port is None:
            raise Exception, "You must specify either a Species (for Commercial) or a Port (for CPFV).  Both can not be blank."
        elif self.species and self.port:
            raise Exception, "You must specify EITHER a Species (for Commercial) OR a Port (for CPFV) but NOT both."
        self.percentage_costs = self.crew + self.fuel + self.fixed
        super(FishingImpactBaselineCost, self).save()
    