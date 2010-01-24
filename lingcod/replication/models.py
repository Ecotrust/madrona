from django.contrib.gis.db import models
import lingcod.intersection.models as int_models

class ReplicationSetup(models.Model):
    org_scheme = models.ForeignKey(int_models.OrganizationScheme)
    
    def __unicode__(self):
        return self.org_scheme.name
        
    def save(self, *args, **kwargs):
        super(ReplicationSetup,self).save(*args, **kwargs)
        for fm in self.org_scheme.featuremapping_set.all():
            # calling fm.units on the next line triggers a featuremapping validation method
            ht, created = HabitatThreshold.objects.get_or_create(replication_setup=self,habitat=fm,units=fm.units)
            ht.save()
            
    def analyze(self, in_dict):
        """
        in_dict should be like: { id: hab_result_dict, id2: hab_result_dict2, etc. }.  this method will return the same 
        format with replication info added to the hab_result_dicts.
        """
        results = {}
        for k,geom in in_dict.iteritems():
            if geom.__class__.__name__<>'GeometryCollection': # This will allow us to include other info in the dict
                results[k] = geom # pass whatever this is on to the results
            else:
                results[k] = self.analyze_single_item(geom)
        return results
            
    def analyze_single_item(self,geom):
        """
        Get the habitat representation results for the geom (this could be for a cluster (geom collection) or for
        an individual MPA (polygon)) and add replication results to it.
        """
        results = self.org_scheme.transformed_results(geom)
        for ht in self.habitatthreshold_set.all():
            sub_dict = {}
            # print results
            # print ht.habitat.name
            # print '%s = %s?' % (results[ht.habitat.name]['feature_map_id'].__class__.__name__,ht.habitat.pk.__class__.__name__)
            if results[ht.habitat.name]['feature_map_id'] != ht.habitat.pk:
                raise Exception('Replication setup is out of sync with Organization Scheme feature map.')
            sub_dict = ht.analyze(results[ht.habitat.name]['result'])
            # sub_dict['result'] = results[ht.name]['result']
            # sub_dict['units'] = results[ht.name]['units']
            # sub_dict['feature_map_id'] = results[ht.name]['feature_map_id']
            # sub_dict['org_scheme_id'] = results[ht.name]['org_scheme_id']
            results[ht.habitat.name].update(sub_dict)
        return results
        
        
class HabitatThreshold(models.Model):
    replication_setup = models.ForeignKey(ReplicationSetup)
    habitat = models.ForeignKey(int_models.FeatureMapping)
    minimum_quantity = models.FloatField(null=True,blank=True)
    units = models.CharField(blank=True, max_length=255)
    
    def __unicode__(self):
        return self.habitat.name
    
    def analyze(self, value=0.0):
        results = {}
        if self.minimum_quantity:
            if value >= self.minimum_quantity:
                results['replicate'] = True
                results['additional_required'] = 0.0
            else:
                results['replicate'] = False
                results['additional_required'] = self.minimum_quantity - value
        else:
            results['replicate'] = None
            results['additional_required'] = None
        return results