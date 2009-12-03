from django.contrib.gis.db import models
import numpy as np

# Create your models here.

class Organism(models.Model):
    common_name = models.CharField(max_length=255,null=True,blank=True)
    genus = models.CharField(max_length=255)
    species = models.CharField(max_length=255)
    
    def __unicode__(self):
        return "%s %s" % (self.genus.title(),self.species.lower())
    
class OrganizationScheme(models.Model):
    from lingcod.intersection.models import OrganizationScheme as OrgScheme
    scheme = models.ForeignKey(OrgScheme)
    
    def __unicode__(self):
        return self.scheme.name
    
    def save(self):
        super(OrganizationScheme,self).save()
        for fm in self.scheme.featuremapping_set.all():
            habitat, created = Habitat.objects.get_or_create(org_scheme=self,habitat=fm)
            habitat.save()
    
class Habitat(models.Model):
    from lingcod.intersection.models import FeatureMapping as FeatMap
    org_scheme = models.ForeignKey(OrganizationScheme)
    habitat = models.ForeignKey(FeatMap)
    
    class Meta:
        ordering = ('org_scheme__scheme__name','habitat__sort')
    
    def __unicode__(self):
        return '%s (%s)' % (self.habitat.name,self.org_scheme.scheme.name,)
    
class Extent(models.Model):
    name = models.CharField(max_length=255, help_text="Very brief description of the area.")
    description = models.TextField(help_text="A full description of the area.")
    geometry = models.PolygonField(srid=3310, null=True, blank=True)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
class Reference(models.Model):
    author = models.CharField(max_length=255, help_text="Author(s) name(s) as you want them to appear in a short citation. Examples: 'Burt, C et al', 'Burt, C', 'McClintock, W and Burt, C'")
    year = models.IntegerField()
    citation = models.TextField(help_text="Full citation")
    url = models.URLField(null=True,blank=True)
    document = models.FileField(upload_to="bioeconomic_model/references/",null=True,blank=True)
    
    def __unicode__(self):
        return "%s %s" % (self.author,self.year)
    
class LengthUnit(models.Model):
    description = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.description
    
class OrganismParameters(models.Model):
    organism = models.ForeignKey(Organism)
    habitat = models.ForeignKey(Habitat)
    habitat_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='habitat_ref')
    range = models.ForeignKey(Extent, related_name='range_extent')
    range_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='range_ref')
    biogeography = models.ForeignKey(Extent, related_name='biogeography_extent')
    biogeography_references = models.ManyToManyField(Reference,null=True,blank=True)
    pelagic_larval_duration = models.IntegerField(help_text="Pelagic Larval Duration in days")
    pelagic_larval_duration_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='pelagic_larval_duration_ref')
    month_choices = ( (1,'January'), (2,'February'), (3,'March'), (4,'April'), (5,'May'), (6,'June'), (7,'July'), (8,'August'), (9,'September'), (10,'October'), (11,'November'), (12,'December'),)
    spawn_start = models.IntegerField(choices=month_choices)
    spawn_start_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='spawn_start_ref')
    spawn_end = models.IntegerField(choices=month_choices)
    spawn_end_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='spawn_end_ref')
    home_range = models.FloatField(help_text="Mean home range diameter in km.")
    home_range_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='home_range_ref')
    length_units = models.ForeignKey(LengthUnit)
    asymtotic_length = models.FloatField()
    asymtotic_length_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='asymtotic_length_ref')
    instantaneous_growth = models.FloatField(help_text="von Bertalanffy instantaneous growth parameter (L in cm TL, t in years)")
    instantaneous_growth_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='instantaneous_growth_ref')
    age_at_length_zero = models.FloatField(help_text="von Bertalanffy parameter for age when length equals zero")
    age_at_length_zero_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='age_at_length_zero_ref')
    c_one = models.FloatField()
    c_one_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='c_one_ref')
    c_two = models.FloatField()
    c_two_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='c_two_ref')
    age_at_maturity = models.FloatField()
    age_at_maturity_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='age_at_maturity_ref')
    age_first_fished = models.FloatField()
    age_first_fished_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='age_first_fished_ref')
    maximum_age = models.FloatField()
    maximum_age_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='maximum_age_ref')
    natural_mortality = models.FloatField()
    natural_mortality_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='natural_mortality_ref')
    compensation_ratio = models.FloatField()
    compensation_ratio_references = models.ManyToManyField(Reference,null=True,blank=True,related_name='compensation_ratio_ref')
    
    def __unicode__(self):
        return '%s Parameters' % self.organism.__unicode__()
    
    @property
    def array(self):
        return np.array([self.organism.pk,self.habitat.pk,self.range.pk,self.biogeography.pk,self.pelagic_larval_duration,self.spawn_start,self.spawn_end,self.home_range,
                         self.length_units.pk,self.asymtotic_length,self.instantaneous_growth,self.age_at_length_zero,self.c_one,self.c_two, self.age_at_maturity,self.maximum_age,
                         self.natural_mortality,self.compensation_ratio])
