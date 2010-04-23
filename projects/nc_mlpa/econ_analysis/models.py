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
    map = models.OneToOneField(FishingImpactAnalysisMap)    
    totalCells = models.IntegerField()  #Overall number of cells with fishing value
    srCells = models.IntegerField()     #Number of cells with fishing value in study region
    totalArea = models.FloatField()   #Total fishing area in square miles
    srArea = models.FloatField()      #Fishing area within the study region
    totalValue = models.FloatField()  #Total fishing value overall
    srValue = models.FloatField()     #Fishing value in the study region
    
'''
The following model was originally used for caching the impact analysis results after they are run for the first time
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
The following model is used for caching the impact analysis results after they are run for the first time
'''
class FishingImpactCache(models.Model):
    mpa = models.ForeignKey(MlpaMpa, verbose_name="MPA ID")
    group = models.TextField(verbose_name="Group")
    port = models.TextField(verbose_name="Port")
    species = models.TextField(verbose_name="Species")
    perc_value = models.FloatField(verbose_name="Percentage Value affected by MPA")
    perc_area = models.FloatField(verbose_name="Percentage Area affected by MPA", null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    wkt_hash = models.CharField(max_length=255)
    
    def save(self, *args, **kwargs):
        #Update FishingImpactCacheAllowedUse table (if necessary)
        old_cache_uses = FishingImpactCacheAllowedUse.objects.filter(mpaid=self.mpa.id)
        old_uses = [cache.use for cache in old_cache_uses]
        new_uses = self.mpa.allowed_uses.all()
        if self.uses_differ(old_uses, new_uses):
            #if old cache has values, these values need to be removed because allowed uses have changed
            #what if cached mpas didn't have any allowed uses before, but now they do? does this still work?
            original_cache = FishingImpactResults.objects.filter(mpa__id=self.mpa.id)
            old_cache = FishingImpactCache.objects.filter(mpa__id=self.mpa.id)
            if len(old_cache) > 0:
                #remove any rows from FishingImpactResults that relate to this mpas id
                for cache in original_cache:
                    cache.delete()
                #remove any rows from FishingImpactCahe table that relate to this mpas id
                for cache in old_cache:
                    cache.delete()
                #remove any rows from FishingImpactCacheAllowedUse table that relate to this mpas id
                for cache in old_cache_uses:
                    cache.delete()
            #add new uses to FishingImpactCacheAllowedUse table
            for use in new_uses:
                mpa_use = FishingImpactCacheAllowedUse(mpaid=self.mpa.id, use=use)
                mpa_use.save() 
        #make sure an identical entry is not there already
        if not FishingImpactCache.objects.filter(mpa__id = self.mpa.id, group=self.group, port=self.port, species=self.species).exists():
            super(FishingImpactCache, self).save(*args, **kwargs)
        else:
            from django.db import IntegrityError
            raise IntegrityError("Entry already exists in database...")
    
    def uses_differ(self, old_uses, new_uses):
        if len(old_uses) != len(new_uses):
            return True
        for use in old_uses:
            if use not in new_uses:
                return True
        return False
        
class FishingImpactCacheAllowedUse(models.Model):
    mpaid = models.IntegerField(verbose_name="Mpa Id")
    use = models.ForeignKey(AllowedUse, verbose_name="Allowed Use")
        
'''
The following model provides a list of Species (Method) names that relate to the Commercial user group
'''
class CommercialSpecies(models.Model):
    name = models.TextField(verbose_name="Species Name (Method)", unique=True)
    def __unicode__(self):
        return u'%s' % (self.name)

'''
The following model provides a list of Port names that relate to the Commercial user group
'''
class CommercialPort(models.Model):
    name = models.TextField(verbose_name="Port Name", unique=True)
    def __unicode__(self):
        return u'%s' % (self.name)
    
'''
The following model relates cost percentages to given species related to the Commercial user group
'''
class CommercialCosts(models.Model):
    species = models.ForeignKey(CommercialSpecies, verbose_name="Species")
    crew = models.FloatField(verbose_name="Percent of costs related to Crew")
    fuel = models.FloatField(verbose_name="Percent of costs related to Fuel")
    fixed = models.FloatField(verbose_name="Percent of costs that are Fixed")
    percentage_costs = models.FloatField(verbose_name="Total Percentage of Costs", editable=False)
    def save(self):
        self.percentage_costs = self.crew + self.fuel + self.fixed
        super(CommercialCosts, self).save()
       
'''
The following model relates gross revenue values to given species,ports related to the Commercial user group
''' 
class CommercialGrossRevenue(models.Model):
    species = models.ForeignKey(CommercialSpecies, verbose_name="Species")
    port = models.ForeignKey(CommercialPort, verbose_name="Port")
    gross_revenue = models.FloatField(verbose_name="Baseline Gross Economic Revenue")
    def __unicode__(self):
        return u'%s, %s, $%.2f' % (self.species.name, self.port.name, self.gross_revenue)
    
'''
The following model provides a list of Port names that relate to the Commercial Passenger Fishing Vessel user group
'''
class CPFVPort(models.Model):
    name = models.TextField(verbose_name="Port Name", unique=True)
    def __unicode__(self):
        return u'%s' % (self.name)
      
'''
The following model relates cost percentages to given ports related to the Commercial Passenger Fishing Vessel user group
'''  
class CPFVCosts(models.Model):
    port = models.ForeignKey(CPFVPort, verbose_name="Port")
    crew = models.FloatField(verbose_name="Percent of costs related to Crew", default=27)
    fuel = models.FloatField(verbose_name="Percent of costs related to Fuel", default=8.7)
    fixed = models.FloatField(verbose_name="Percent of costs that are Fixed", default=16.1)
    percentage_costs = models.FloatField(verbose_name="Total Percentage of Costs", editable=False)
    def save(self):
        self.percentage_costs = self.crew + self.fuel + self.fixed
        super(CPFVCosts, self).save()        
            
'''
The following model relates gross revenue values to given ports related to the Commercial Passenger Fishing Vessel user group
''' 
class CPFVGrossRevenue(models.Model):
    port = models.ForeignKey(CPFVPort, verbose_name="Port")
    gross_revenue = models.FloatField(verbose_name="Baseline Gross Economic Revenue", default=100)
    def __unicode__(self):
        return u'%s, $%.2f' % (self.port.name, self.gross_revenue)
        