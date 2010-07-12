from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.gis.measure import A, D
from lingcod.unit_converter.models import length_in_display_units, area_in_display_units
from lingcod.common.utils import KmlWrap, ComputeLookAt
from django.contrib.gis.geos import Point, Polygon, LinearRing


class StudyRegionManager(models.GeoManager):
    """Returns the currently active study region. The active study region is 
    determined by the active attribute.
    """
    def current(self):
        return self.get(active=True)
        #or should the above line now be changed to:
        #return self.current()
        

class StudyRegion(models.Model):
    """Model used for representing study regions

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================

        ``name``                Name of the Study Region
        
        ``active``              Whether the study region is treated as the
                                current authoritative copy. This should not be
                                set using the admin interface
                                
        ``creation_date``       Automatically assigned

        ``modification_date``   Automatically assigned
                                
        ``geometry``            PolygonField representing the study region boundary
        
        ``date_modified``       When the Study Region geometry was last updated.
        
        ``lookAt_Lat``          Latitude of the default look-at point
        
        ``lookAt_Lon``          Longitude of the default look-at point
        
        ``lookAt_Range``        Range camera sits from the default look-at point
        
        ``lookAt_Tilt``         Angle offset from vertical for default camera pos
        
        ``lookAt_Heading``      Angle offset from North for default camera pos
                                
        ======================  ==============================================
"""   
    name = models.CharField(verbose_name="Study Region Name", max_length=255)
    
    active = models.BooleanField(default=False, help_text='This options will usually not be set using the admin interface, but rather by using the management commands relating to study region changes.')
    
    creation_date = models.DateTimeField(auto_now_add=True) 
    modification_date = models.DateTimeField(auto_now=True)     
    
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Study region boundary")
    
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    
    lookAt_Lat = models.FloatField(default=0, null=True, blank=True)
    lookAt_Lon = models.FloatField(default=0, null=True, blank=True)
    lookAt_Range = models.FloatField(default=80000, help_text='Distance from lookAt point in meters')
    lookAt_Tilt = models.FloatField(default=0, help_text='Degrees from vertical (0=directly above)')
    lookAt_Heading = models.FloatField(default=0, help_text='View direction in degrees (0=look North)')
    
    objects = StudyRegionManager()
    
    class Meta:
        db_table = u'mm_study_region'

    def __unicode__(self):
        return u'%s' % self.name
    
    def save(self, *args, **kwargs):
        super(StudyRegion, self).save(*args, **kwargs)
        if self.active and StudyRegion.objects.filter(active=True).count() > 1:
            # Ensure that any previously active study region is deactivated
            # There can be only one!
            StudyRegion.objects.filter(active=True).exclude(pk=self.pk).update(active=False)
            
    @models.permalink
    def get_absolute_url(self):
        return ('lingcod.studyregion.views.show', [self.pk])
        
    @property    
    def area_sq_mi(self):
        """
        WARNING:  This method assumes that the native units of the geometry are meters.  
        Returns the area of the study region in sq_mi
        """
        return area_in_display_units(self.geometry.area)
            
    def kml(self, style_domain):
        """
        Get the kml of the entire study region
        """
        bUseLod = False
        
        if not bUseLod:
            transform_geom = self.geometry.simplify(settings.KML_SIMPLIFY_TOLERANCE, preserve_topology=True)
            transform_geom.transform(4326)
            
            shape_kml = transform_geom.kml
            
            # remove Polygon, outerBoundaryIs, innerBoundaryIs tags
            shape_kml = shape_kml.replace('<Polygon>', '')
            shape_kml = shape_kml.replace('</Polygon>', '')
            shape_kml = shape_kml.replace('<outerBoundaryIs>', '')
            shape_kml = shape_kml.replace('</outerBoundaryIs>', '')
            shape_kml = shape_kml.replace('<innerBoundaryIs>', '')
            shape_kml = shape_kml.replace('</innerBoundaryIs>', '')
            
            return '<Document><name>%s</name>' % (self.name, ) + self.lookAtKml() + '<Placemark><name>Study Region Boundaries</name>%s<styleUrl>http://%s/media/studyregion/styles.kml#StudyRegionStyle</styleUrl>%s</Placemark></Document>' % ( self.lookAtKml(), style_domain, shape_kml, )
    
        else:
            # use the kml_chunk LOD system,
            trans_geom = self.geometry.clone() # cloning here to avoid stepping into subfunctions with a mutated self.geometry
            trans_geom.transform(4326)
            
            w = trans_geom.extent[0]
            s = trans_geom.extent[1]
            e = trans_geom.extent[2]
            n = trans_geom.extent[3]
            
            return '<Document><name>%s</name>' % (self.name, ) + self.lookAtKml() + self.kml_chunk(n,s,e,w) + '</Document>' 
        
        
    # NOTE: not currently used, LOD system overhead not justified by performance
    def kml_chunk(self, n, s, e, w ):
        """
        Get the kml of a lat/lon bounded part of the study region, 
        with geometry simplified in proportion to the visible % of the region
        """
    
        bounds = Polygon( LinearRing([ Point( w, n ), Point( e, n ), Point( e, s ), Point( w, s ), Point( w, n)]))
        bounds.set_srid(4326)
        center_lat = bounds.centroid.y # in 4326 because it is used only for setting up the subregion calls
        center_lon = bounds.centroid.x # in 4326 because it is used only for setting up the subregion calls
        bounds.transform(settings.GEOMETRY_DB_SRID)
           
        # all longitudinal width calcs should be done in GEOMETRY_DB_SRID - 4326 can fail across the date line
        zoom_width = (Point( bounds.extent[0], bounds.centroid.y )).distance( Point( bounds.extent[2], bounds.centroid.y ))
    
        full_shape_width = (Point( self.geometry.extent[0], self.geometry.centroid.y )).distance( Point( self.geometry.extent[2], self.geometry.centroid.y ))
        
        # The following simplify values can be tuned to your preference
        # minimum geometry simplify value (highest detail) = 50 (arbitrary, based on observation)
        # maximum geometry simplify value = 200 (arbitrary, based on observation)
        # value set by pecentage of study region width requested in this chunk
        min_simplify_val = 50.0
        max_simplify_val = 200.0
        simplify_factor = max( min_simplify_val, min( max_simplify_val, max_simplify_val * zoom_width / full_shape_width))
        
        transform_geom = self.geometry.simplify(simplify_factor, preserve_topology=True)
        transform_geom = transform_geom.intersection( bounds )    
        transform_geom.transform(4326)
        
        # Debugging info
        #print zoom_width
        #print full_shape_width
        #print simplify_factor
        #print transform_geom.num_coords
        # End debugging info
        
        # only add sub-regions if this is not our highest detail level
        bLastLodLevel = simplify_factor < max_simplify_val # change this last value to build varying levels of LOD
        max_lod_pixels = 500
        min_lod_pixels = 250
        
        # make sure the most detailed lod stays active no matter how close user zooms
        if bLastLodLevel:
            max_lod_pixels = -1
            
            
        retval = '<Region><LatLonAltBox><north>%f</north><south>%f</south><east>%f</east><west>%f</west></LatLonAltBox><Lod><minLodPixels>%f</minLodPixels><maxLodPixels>%f</maxLodPixels><minFadeExtent>0</minFadeExtent><maxFadeExtent>0</maxFadeExtent></Lod></Region>' % ( n, s, e, w, min_lod_pixels, max_lod_pixels ) + '<Placemark> <name>Study Region Boundaries</name><Style> <LineStyle> <color>ff00ffff</color> <width>2</width> </LineStyle> <PolyStyle> <color>8000ffff</color> </PolyStyle></Style>%s</Placemark>' % (transform_geom.kml, )
        
        # conditionally add sub-regions
        if not bLastLodLevel:
            subregions = '<Folder><name>Study Region LODs</name>' + '<Folder><name>SE</name>' + self.kml_chunk( center_lat, s, e, center_lon ) + '</Folder>'
            
            subregions = subregions + '<Folder><name>NE</name>' + self.kml_chunk( n, center_lat, e, center_lon ) + '</Folder>'       
            
            subregions = subregions + '<Folder><name>SW</name>' + self.kml_chunk( center_lat, s, center_lon, w ) + '</Folder>'    
            
            subregions = subregions + '<Folder><name>NW</name>' + self.kml_chunk( n, center_lat, center_lon, w ) + '</Folder>'
            
            retval = retval + subregions + '</Folder>'
        
        return retval 
    
        
    def lookAtKml(self):
        """
        Get the kml for the region's lookat values saved in the DB,
        or compute them if they are set to 0
        """
    
        if self.lookAt_Lat == 0.0 and self.lookAt_Lon == 0.0:
            self.cacheLookAt()
    
        retval = '<LookAt><latitude>%f</latitude><longitude>%f</longitude><range>%f</range><tilt>%f</tilt><heading>%f</heading><altitudeMode>clampToGround</altitudeMode></LookAt>' % (self.lookAt_Lat, self.lookAt_Lon, self.lookAt_Range, self.lookAt_Tilt, self.lookAt_Heading )
        return retval
        
        
    def cacheLookAt(self):
        """
        Compute and store the camera perspective that puts the whole study region in view
        """
    
        lookAtParams = ComputeLookAt( self.geometry )
        
        self.lookAt_Range = lookAtParams['range']
        self.lookAt_Lat = lookAtParams['latitude'] 
        self.lookAt_Lon = lookAtParams['longitude'] 
        self.lookAt_Tilt = lookAtParams['tilt']
        self.lookAt_Heading = lookAtParams['heading']
        
        self.save()
    
        
        
        

#    def updated(self):
    
        # expire reports and report caches
        
        # reclip MPA's
        
