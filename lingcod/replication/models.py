from django.contrib.gis.db import models
from lingcod.intersection import models as int_models
from lingcod.data_distributor.models import functions_in_module
from django.contrib.gis.geos import fromstr

def use_sort_as_key(results):
    """
    we want the results sorted by the sort value, not by the habitat name.
    """
    sort_results = {}
    for hab,sub_dict in results.iteritems():
        sub_dict.update( {'name':hab} )
        sort_results.update( {results[hab]['sort']:sub_dict} )
    
    return sort_results
    
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
        format with replication info added to the cd
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
            if results[ht.habitat.name]['feature_map_id'] != ht.habitat.pk:
                raise Exception('Replication setup is out of sync with Organization Scheme feature map.')
            sub_dict = ht.analyze(value=results[ht.habitat.name]['result'],geom=geom)
            results[ht.habitat.name].update(sub_dict)
        return results
        
class HabitatThreshold(models.Model):
    replication_setup = models.ForeignKey(ReplicationSetup)
    habitat = models.ForeignKey(int_models.FeatureMapping)
    minimum_quantity = models.FloatField(null=True, blank=True)
    rule = models.ForeignKey('ThresholdRule', null=True, blank=True)
    units = models.CharField(blank=True, max_length=255)
    date_modified = models.DateTimeField(null=True, auto_now=True, verbose_name="Date Modified")
    
    def __unicode__(self):
        return self.habitat.name
    
    def save(self):
        if self.minimum_quantity!=None and self.rule!=None:
            raise Exception, "You can specify minimum quantity or a rule.  You may not specify both."
        else:
            super(HabitatThreshold, self).save()
            
    def analyze(self, value=0.0, geom=fromstr('POLYGON EMPTY')):
        results = {}
        if self.minimum_quantity:
            if value >= self.minimum_quantity:
                results['replicate'] = True
                results['additional_required'] = 0.0
            else:
                results['replicate'] = False
                results['additional_required'] = self.minimum_quantity - value
        elif self.rule:
            rule = self.rule.name
            r_func = rule_functions()[rule]
            results['replicate'], results['reason'] = r_func(geom)
            results['additional_required'] = -1
        else:
            results['replicate'] = None
            results['additional_required'] = None
        return results

### Rule Functions ###
# These rules are actually specific to a particular organization scheme which is, in turn, specific to a particular project (nc_mlpa in this case).
# That kind of sucks and perhaps I should really move this into the report app somehow, but I'm just going this way for now.

def rule_for_soft_30_100m(geom):
    """
    IF area 30-100m soft bottom >= 7 sq mi
    OR total area soft bottom >= 7 sq mi AND area 30-100m soft bottom >= 5 sq mi AND [length 0-30m soft proxy >= 1.1 mi OR area >100m soft bottom >= 1 sq mi]
    """
    from lingcod.intersection.models import OrganizationScheme, FeatureMapping
    replicate = False
    # The following are lamely dependent on data loaded into the intersection app
    soft_0_30_proxy = OrganizationScheme.objects.get(name='satopencoast_replication').featuremapping_set.filter(name__icontains='soft').filter(name__icontains='0 - 30').filter(name__icontains='proxy')[0].transformed_results(geom).values()[0]['result']
    soft_30_100 = OrganizationScheme.objects.get(name='satopencoast_replication').featuremapping_set.filter(name__icontains='soft').filter(name__icontains='30 - 100')[0].transformed_results(geom).values()[0]['result']
    soft_100_3000 = OrganizationScheme.objects.get(name='satopencoast_replication').featuremapping_set.filter(name__icontains='soft').filter(name__icontains='100 - 3000')[0].transformed_results(geom).values()[0]['result']
    total_soft = OrganizationScheme.objects.get(name='satopencoast').featuremapping_set.filter(name__icontains='soft all depths')[0].transformed_results(geom).values()[0]['result']
    if soft_30_100 >= 7:
        replicate = True
        reason = '7 or more square miles of Soft 30-100m (%f square miles).' % soft_30_100
    elif total_soft >= 7 and soft_30_100 >= 5 and (soft_0_30_proxy >= 1.1 or soft_100_3000 >= 1):
        replicate = True
        reason = 'total_soft >= 7 sq mi and soft_30_100 >= 5 sq mi and (soft_0_30_proxy >= 1.1 mi or soft_100_3000 >= 1 sq mi). total_soft: %f sq mi, soft_30_100: %f sq mi, soft_0_30_proxy: %f mi, soft_100_3000: %f sq mi' % (total_soft, soft_30_100, soft_0_30_proxy, soft_100_3000)
    # elif total_soft >= 10 and soft_100_3000 >= 1 and soft_30_100 >= 5 and soft_0_30_proxy >= 1.1:
    #     replicate = True
    #     reason = 'total_soft >= 10 and soft_100_3000 >= 1 and soft_30_100 >= 5 and soft_0_30_proxy >= 1.1  (total_soft: %f sq mi, soft_30_100: %f sq mi, soft_0_30_proxy: %f mi, soft_100_3000: %f sq mi)' % (total_soft, soft_30_100, soft_0_30_proxy, soft_100_3000)
    else:
        reason = 'None of the replication requirements were met: IF area 30-100m soft bottom >= 7 sq mi OR total area soft bottom >= 7 sq mi AND area 30-100m soft bottom >= 5 sq mi AND [length 0-30m soft proxy >= 1.1 mi OR area >100m soft bottom >= 1 sq mi]'
    return replicate, reason
    
def rule_for_soft_100_3000m(geom):
    """
    IF area 100-3000m soft bottom >= 17 sq mi
    OR total area soft bottom >= 7 sq mi AND area 100-3000m >= 1 sq mi AND area 30-100m soft bottom >= 5 sq mi
    """
    from lingcod.intersection.models import OrganizationScheme, FeatureMapping
    replicate = False
    # The following are lamely dependent on data loaded into the intersection app
    soft_0_30_proxy = OrganizationScheme.objects.get(name='satopencoast_replication').featuremapping_set.filter(name__icontains='soft').filter(name__icontains='0 - 30').filter(name__icontains='proxy')[0].transformed_results(geom).values()[0]['result']
    soft_30_100 = OrganizationScheme.objects.get(name='satopencoast_replication').featuremapping_set.filter(name__icontains='soft').filter(name__icontains='30 - 100')[0].transformed_results(geom).values()[0]['result']
    soft_100_3000 = OrganizationScheme.objects.get(name='satopencoast_replication').featuremapping_set.filter(name__icontains='soft').filter(name__icontains='100 - 3000')[0].transformed_results(geom).values()[0]['result']
    total_soft = OrganizationScheme.objects.get(name='satopencoast').featuremapping_set.filter(name__icontains='soft all depths')[0].transformed_results(geom).values()[0]['result']
    if soft_100_3000 >= 17:
        replicate = True
        reason = '17 or more square miles of Soft 100-3000m (%f square miles).' % soft_100_3000
    elif total_soft >= 7 and soft_100_3000 >= 1 and soft_30_100 >= 5:
        replicate = True
        reason = 'total area soft bottom >= 7 sq mi AND area 100-3000m >= 1 sq mi AND area 30-100m soft bottom >= 5 sq mi. total_soft: %f sq mi, soft_30_100: %f sq mi, soft_100_3000: %f sq mi' % (total_soft, soft_30_100, soft_100_3000)
    # elif total_soft >= 10 and soft_100_3000 >= 1 and soft_30_100 >= 5 and soft_0_30_proxy >= 1.1:
    #     replicate = True
    #     reason = 'total area soft bottom >= 10 sq mi AND area 100-3000m soft bottom >= 1 sq mi AND area 30-100m soft bottom >=5 sq mi AND length 0-30m soft proxy >= 1.1 mi. (total_soft: %f sq mi, soft_30_100: %f sq mi, soft_0_30_proxy: %f mi, soft_100_3000: %f sq mi)' % (total_soft, soft_30_100, soft_0_30_proxy, soft_100_3000)
    else: 
        reason = 'None of the replication requirements for this habitat were met: IF area 100-3000m soft bottom >= 17 sq mi OR total area soft bottom >= 7 sq mi AND area 100-3000m >= 1 sq mi AND area 30-100m soft bottom >= 5 sq mi'
    return replicate, reason
### End Rule Functions ###
    
def rule_functions(module=__name__):
    all_funcs = functions_in_module(module)
    for key in all_funcs.keys():
        if not key.startswith('rule_for_'):
            all_funcs.pop(key)
    return all_funcs

class ThresholdRule(models.Model):
    name_choices = zip(rule_functions().keys(),rule_functions().keys())
    name = models.CharField(max_length=180, choices=name_choices)
    description = models.TextField(blank=True,null=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.description = rule_functions()[self.name].__doc__
        super(ThresholdRule,self).save(*args, **kwargs)

        