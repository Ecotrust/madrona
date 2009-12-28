from django.contrib.gis.db import models
from django.contrib.gis import geos
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
        
    def relevant_habitat_grid(self,with_geometries=False):
        if with_geometries:
            return GridAttributes.objects.filter(habitat=self.habitat,value__gt=0.0)
        else:
            return GridAttributes.objects.filter(habitat=self.habitat,value__gt=0.0).defer('grid__geometry')

class StudyRegionManager(models.GeoManager):
    
    def multigeometry(self):
        # Returns a multipolygon of the whole study region
        mgeom = geos.fromstr('MULTIPOLYGON EMPTY')
        for sr in self.iterator():
            mgeom.append(sr.geometry)
        return mgeom
    
    def convex_hull_multigeometry(self):
        mgeom = geos.fromstr('MULTIPOLYGON EMPTY').convex_hull
        for sr in self.iterator():
            mgeom.append(sr.geometry)
        return mgeom
    
    def extent(self):
        # Returns the extent of the entire study region in the format (xmin, ymin, xmax, ymax)
        mgeom = self.multigeometry()
        return mgeom.extent
 
class StudyRegion(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    geometry = models.PolygonField(srid=3310, null=True, blank=True)
    objects = StudyRegionManager()
    
    def __unicode__(self):
        return 'Study Region: %s'  % self.name

class PolygonGridManager(models.GeoManager):
    
    def load_attributes(self, habitat_list=None):
        if not habitat_list:
            habitat_list = Habitat.objects.all()
        for pg in self.iterator():
            pg.load_attributes(habitat_list)
        

class PolygonGrid(models.Model):
    geometry = models.PolygonField(srid=3310)
    objects = PolygonGridManager()
    
    def load_attributes(self, habitat_list):
        for habitat in habitat_list:
            result = habitat.habitat.transformed_results(self.geometry)
            ga = GridAttributes()
            ga.grid = self
            ga.name = result['feature_name']
            ga.habitat = habitat
            ga.value = result['result']
            ga.save()
    
class GridAttributes(models.Model):
    name = models.CharField(max_length=255)
    grid = models.ForeignKey(PolygonGrid)
    value = models.FloatField()
    habitat = models.ForeignKey(Habitat,null=True,blank=True)



def corner_point_array(bbox, mgeom = StudyRegion.objects.multigeometry(), cell_size=1000):
    # returns an array of points that are within sqrt(2) * cell_size of mgeom
    threshold = cell_size * np.sqrt(2)
    simp_mgeom = mgeom.simplify(cell_size / 3,preserve_topology=True).buffer(threshold)
    xmin = bbox[0]
    ymin = bbox[1]
    xmax = bbox[2]
    ymax = bbox[3]
    xdist = xmax - xmin
    ydist = ymax - ymin
    xcells = int(xdist/cell_size) + 1
    ycells = int(ydist/cell_size) + 1
    
    x_current = xmin
    y_current = ymin
    points = []
    for y_num in range(0,ycells):
        y_current = ymin + (y_num * cell_size)
        print '.',
        for x_num in range(0,xcells):
            x_current = xmin + (x_num * cell_size)
            corner_pnt = geos.Point(x_current,y_current)
#            dist = corner_pnt.distance(mgeom)
            if corner_pnt.within(simp_mgeom): #dist < threshold:
                points.append(corner_pnt)
    return points

def create_grid_cell(corner_pnt, cell_size, mgeom = StudyRegion.objects.multigeometry(), test_intersection=True, srid=3310):
    bbox = (corner_pnt.x,corner_pnt.y,cell_size + corner_pnt.x,cell_size + corner_pnt.y)
    poly = geos.Polygon.from_bbox(bbox)
    if not test_intersection:
        print '+',
        pg = PolygonGrid()
        pg.geometry = poly
        pg.save()
        return True
    elif poly.intersects(mgeom):
        print '+',
        pg = PolygonGrid()
        pg.geometry = poly
        pg.save()
        return True
    else:
        return False

def create_relevent_grid(cell_size=1000):
    sr_extent = StudyRegion.objects.extent()
    PolygonGrid.objects.all().delete()
    points = corner_point_array(sr_extent)
    for pnt in points:
        create_grid_cell(pnt,cell_size)

def create_full_study_region_grid(cell_size=1000):
    sr_extent = StudyRegion.objects.extent()
    PolygonGrid.objects.all().delete()
    xmin = sr_extent[0]
    ymin = sr_extent[1]
    xmax = sr_extent[2]
    ymax = sr_extent[3]
    xdist = xmax - xmin
    ydist = ymax - ymin
    xcells = int(xdist/cell_size) + 1
    ycells = int(ydist/cell_size) + 1
    
    x_current = xmin
    y_current = ymin
    count = 0
    for y_num in range(0,ycells):
        y_current = ymin + (y_num * cell_size)
        print '.',
        for x_num in range(0,xcells):
            x_current = xmin + (x_num * cell_size)
            corner_pnt = geos.Point(x_current,y_current)
            create_grid_cell(corner_pnt,cell_size)
            if create_grid_cell(corner_pnt,cell_size):
                count += 1
    return count

def convert_to_color_ramp(the_list,base_color='green',alpha=0.5):
    # kml color format: aabbggrr
    # change the alpha to a hex value
    hex_alpha = hex(int(alpha*255))[2:]
    min = np.min(the_list)
    max = np.max(the_list)
    # transform the list into a range of color values
    def color_int(x): return int(((x-min)/(max-min))*255)
    color_int_list = map(color_int,the_list)
    def hex_string(x):
        if x==0:
            return '00'
        else:
            return hex(x)[2:]
    hex_mapped = map(hex_string,color_int_list)
    if base_color=='green':
        def green(hex_num): return '%s00%s00' % ( str(hex_alpha),str(hex_num) )
        color_hex_list = [ green(x) for x in hex_mapped ]
    return dict(zip(the_list,color_hex_list))

class PointScrap(models.Model):
    geometry = models.PointField(srid=3310)
    objects = models.GeoManager()

class Scrap(models.Model):
    geometry = models.PolygonField(srid=3310)
    objects = models.GeoManager()