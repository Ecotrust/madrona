from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from lingcod.common.utils import LookAtKml
from lingcod.sharing.managers import ShareableGeoManager
from lingcod.manipulators.manipulators import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.gis.db.models.query import GeoQuerySet

class MpaDesignation(models.Model):
    """Model used to represent the designation of the MPA
        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``name``                Designation of the MPA

        ``acronym``             The acronym for this MPA designation

        ``poly_outline_color``  Hex Color for rendering the outline/border

        ``poly_fill_color``     Hex Color for rendering the polygon area
        ======================  ==============================================
    """
    name = models.TextField(verbose_name="Designation Name")
    acronym = models.CharField(max_length=10, unique=True, verbose_name="Designation Acronym")
    poly_outline_color = models.CharField(max_length=8, default="ffffffff", verbose_name="Hex Color for rendering outline/border")
    poly_fill_color = models.CharField(max_length=8, default="ff0000ff", verbose_name="Hex Color for rendering polygon area")
    url = models.URLField(verify_exists=False,verbose_name="URL to more info on this MPA Designation")

    def __unicode__(self):
        return "(%s) %s" % (self.acronym, self.name)

class GeoQuerySetManager(ShareableGeoManager):
    """ 
    Used to extend the queryset manager; see http://simonwillison.net/2008/May/1/orm/
    """
    def get_query_set(self):
        return self.model.QuerySet(self.model)

class Mpa(models.Model):
    """Model used for representing marine protected areas or MPAs

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``user``                Owner of the MPA

        ``name``                Name of the MPA
                                
        ``date_created``        When the MPA was created. Is not changed on
                                updates.
        ``date_modified``       When the MPA geometry was last updated.
        
        ``geometry_orig``       PolygonField representing the MPA boundary as
                                originally drawn by the user
        
        ``geometry_final``      PolygonField representing the MPA boundary
                                after postprocessing.
                                
        ``content_type``        Content type of the associated Array 
                                (Generic One-to-Many)
                                
        ``object_id``           pk of the specific array object
        
        ``array``               Use to access the associated Array (read-only)
        ======================  ==============================================
    """   
    user = models.ForeignKey(User)
    name = models.CharField(verbose_name="MPA Name", max_length="255")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    geometry_orig = models.PolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Original MPA boundary")
    geometry_final = models.PolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Final MPA boundary")
    designation = models.ForeignKey(MpaDesignation, blank=True, null=True)
    # Array relation fields
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True,null=True)
    array = generic.GenericForeignKey('content_type', 'object_id')
    # Expose sharing functionality
    sharing_groups = models.ManyToManyField(Group,blank=True,null=True,verbose_name="Share this MPA with the following groups")

    objects = GeoQuerySetManager()
    class QuerySet(GeoQuerySet):
        def add_kml(self):
            """
            Custom queryset method which adds an 'extra' .kml property to the returned object -
                a kml string with correct dimensions and Left-Hand Rule (LHR) enforced (ie the reversed RHR)
                Ensures proper styling and clickability compared to the GEOSGeometry.kml property in geodjango
                See issue #190 for more details
            Warning: This relies on postgis-specific SQL and assumes 'geometry_final' is the geometry column name
            Usage: 
                mpas = Mpa.objects.filter(...).add_kml()
                mpas[0].kml
                # Note you can still access the geodjango way (may not render correctly in GE though)
                mpas[0].geometry_final.kml
            """
            return self.extra(select={'kml':'replace(AsKML(ST_Reverse(ST_ForceRHR(ST_Translate(ST_Force_3d(simplify("%s"."geometry_final", 20)), 0, 0, 100)))), \'<Polygon>\', \'<Polygon><altitudeMode>absolute</altitudeMode><extrude>1</extrude>\')' % str(self.model._meta.db_table)})
    
    class Meta:
        permissions = (("can_share_mpas", "Can share MPAs"),)
        abstract=True
        
    class Options:
        manipulators = [ ClipToStudyRegionManipulator ]

    def __unicode__(self):
        return self.name
        
    @models.permalink
    def get_absolute_url(self):
        return ('mpa_resource', (), {
            'pk': self.pk
        })
            
    def centroid_kml(self):
        geom = self.geometry_final.transform(4326, clone=True)
        return geom.point_on_surface.kml

    def geom_as_kml(self):
        """
        DEPRECATED
        returns the final geometry as a kml geometry string projected into wgs84
        Note: this is not guaranteed to be valid at geodjango's GEOSGeometry.kml may not behave properly in GE
        Use the queryset method add_kml() then use the objects' .kml property instead 
        """
        wgs84_geom = self.geometry_final.transform(4326, clone=True)
        prepend = """<Polygon>
      <extrude>0</extrude>
      <tessellate>0</tessellate>
      <altitudeMode>clampToGround</altitudeMode>
        """
        kml = wgs84_geom.kml.replace("<Polygon>", prepend) 
        return kml

    def lookAtKml(self):
        """
        Get the kml for a camera perspective looking at the MPA's final geometry
        """
        return LookAtKml( self.geometry_final )
    
    
    def kmlOrigGeom(self, style_domain):
        self.geometry_orig.transform(4326)
        return '<Placemark>' + '<name>' + self.name + ' original geometry</name>' + self.kmlOrigGeomStyle(style_domain) + LookAtKml( self.geometry_orig ) + self.geometry_orig.kml + '</Placemark>'
    
    def kmlFinalGeom(self, style_domain):
        self.geometry_final.transform(4326)
        return '<Placemark>' + '<name>' + self.name + ' final geometry</name>' + self.kmlFinalGeomStyle(style_domain) + LookAtKml( self.geometry_final ) + self.geometry_final.kml + '</Placemark>'
        
    
    def kmlOrigGeomStyle(self, style_domain):
        return '<Style> <LineStyle> <color>ffffffff</color> <width>2</width> </LineStyle> <PolyStyle> <color>80ffffff</color> </PolyStyle></Style>'
    
    
    def kmlFinalGeomStyle(self, style_domain):
        return '<Style> <LineStyle> <color>ffffffff</color> <width>2</width> </LineStyle> <PolyStyle> <color>80ff0000</color> </PolyStyle></Style>'
        
        
    def kmlFolder(self, style_domain):
        """
        Return a kml folder containing the kml for this mpa's final and orginal geometry
        """
        return '<Document><name>MPAs</name><Folder>' + '<name>' + self.name + '</name>' + self.kmlFinalGeom(style_domain) + self.kmlOrigGeom(style_domain) + '</Folder></Document>'

    def add_to_array(self, array):
        """Adds the MPA to the specified array."""
        self.array = array
        self.save()
        
    def remove_from_array(self):
        """Sets the MPA's `array` property to None."""
        self.array = None
        self.save()

    def save(self):
        target_shape = self.geometry_orig.transform(settings.GEOMETRY_CLIENT_SRID, clone=True).wkt
        result = False
        for manipulator in self.__class__.Options.manipulators:
            m = manipulator(target_shape)
            result = m.manipulate()
            target_shape = result['clipped_shape'].wkt
        geo = result['clipped_shape']
        geo.transform(settings.GEOMETRY_DB_SRID)
        if geo:
            self.geometry_final = geo
        else:
            raise Exception('Could not pre-process geometry')
        super(Mpa, self).save() # Call the "real" save() method
