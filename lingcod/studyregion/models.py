from django.contrib.gis.db import models
from django.conf import settings
from lingcod.common.utils import KmlWrap
from django.contrib.gis.geos import Point, Polygon, LinearRing


class StudyRegion(models.Model):
    """Model used for representing study regions

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================

        ``name``                Name of the Study Region
                                
        ``geometry``            PolygonField representing the study region boundary
        
        ``date_modified``       When the Study Region geometry was last updated.
        
        ``lookAt_Lat``          Latitude of the default look-at point
        
        ``lookAt_Lon``          Longitude of the default look-at point
        
        ``lookAt_Range``        Range camera sits from the default look-at point
        
        ``lookAt_Tilt``         Angle offset from vertical for default camera pos
        
        ``lookAt_Heading``      Angle offset from North for default camera pos
                                
        ======================  ==============================================
"""   
    name = models.TextField(verbose_name="Study Region Name")
    
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Study region boundary")
    
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    
    lookAt_Lat = models.FloatField(default=0, null=True, blank=True)
    lookAt_Lon = models.FloatField(default=0, null=True, blank=True)
    lookAt_Range = models.FloatField(default=80000, help_text='Distance from lookAt point in meters')
    lookAt_Tilt = models.FloatField(default=0, help_text='Degrees from vertical (0=directly above)')
    lookAt_Heading = models.FloatField(default=0, help_text='View direction in degrees (0=look North)')
    
    objects = models.GeoManager()
    
    class Meta:
        db_table = u'mm_study_region'
    
    
    def kml(self, style_domain):
        """
        Get the kml of the entire study region
        """
        
        transform_geom = self.geometry.simplify(20, preserve_topology=True)
        transform_geom.transform(4326)
        
        return '<Document><name>%s</name>' % (self.name, ) + self.lookAtKml() + '<Placemark> <name>%s</name><styleUrl>http://%s/media/studyregion/styles.kml#YellowFillNoLine</styleUrl>%s</Placemark></Document>' % (self.name, style_domain, transform_geom.kml, )
    
        # To use the kml_chunk LOD system, use the following instead:
    
        #trans_geom = self.geometry.clone()
        #trans_geom.transform(4326)
        
        #w = trans_geom.extent[0]
        #s = trans_geom.extent[1]
        #e = trans_geom.extent[2]
        #n = trans_geom.extent[3]
        
        #retval = '<Document><name>%s</name>' % (self.name, ) + self.lookAtKml() + self.kml_chunk(n,s,e,w) + '</Document>' 

        #return retval
        
        
    # NOTE: not currently used, LOD system overhead not justified by performance
    def kml_chunk(self, n, s, e, w ):
        """
        Get the kml of a lat/lon bounded part of the study region, 
        with geometry simplified in proportion to the visible % of the region
        """
    
        bounds = Polygon( LinearRing([ Point( w, n ), Point( e, n ), Point( e, s ), Point( w, s ), Point( w, n)]))
        bounds.set_srid(4326)
        center_lat = bounds.centroid.y
        center_lon = bounds.centroid.x
        bounds.transform( settings.GEOMETRY_DB_SRID )
            
        zoom_width = abs(bounds.extent[0] - bounds.extent[2])
    
        # minimum geometry simplify value (highest detail) = 50
        # maximum geometry simplify value = 200
        # value set by pecentage of study region width requested in this chunk
        simplify_factor = max( 50, min( 200, 200.0 * float(zoom_width) / abs( self.geometry.extent[0] - self.geometry.extent[2]))) # TODO: fix this extent subtraction at the end -- will not account for international date line if in srid 4326
        
        transform_geom = self.geometry.simplify(simplify_factor, preserve_topology=True)
        transform_geom = transform_geom.intersection( bounds )    
        transform_geom.transform(4326)
        
        # Debugging info
        #print zoom_width
        #print simplify_factor
        #print transform_geom.num_coords
        # End debugging info
        
        # only add sub-regions if this is not our highest detail level
        bLastLevel = simplify_factor == 200 # change value to build varying levels of LOD
        max_lod_pixels = 500
        if bLastLevel:
            max_lod_pixels = -1
            
        retval = '<Region><LatLonAltBox><north>%f</north><south>%f</south><east>%f</east><west>%f</west></LatLonAltBox><Lod><minLodPixels>250</minLodPixels><maxLodPixels>%f</maxLodPixels><minFadeExtent>0</minFadeExtent><maxFadeExtent>0</maxFadeExtent></Lod></Region>' % ( n, s, e, w, max_lod_pixels )
        
        # conditionally add sub-regions
        if not bLastLevel:
            subregions = '<Folder>' + self.kml_chunk( center_lat, s, e, center_lon ) 
            
            subregions = subregions + self.kml_chunk( n, center_lat, e, center_lon )       
            
            subregions = subregions + self.kml_chunk( center_lat, s, center_lon, w )    
            
            subregions = subregions + self.kml_chunk( n, center_lat, center_lon, w )
            
            retval = retval + subregions + '</Folder>'
        
        return retval + '<Placemark> <name>Study Region Boundaries</name><Style> <LineStyle> <color>ff00ffff</color> <width>2</width> </LineStyle> <PolyStyle> <color>8000ffff</color> </PolyStyle></Style>%s</Placemark>' % (transform_geom.kml, )
    
        
    def lookAtKml(self):
        """
        Get the kml for the region's lookat values saved in the DB,
        or compute them if they are set to 0
        """
    
        if self.lookAt_Lat == 0.0 and self.lookAt_Lon == 0.0:
            self.computeLookAt()
    
        retval = '<LookAt><latitude>%f</latitude><longitude>%f</longitude><range>%f</range><tilt>%f</tilt><heading>%f</heading><altitudeMode>clampToGround</altitudeMode></LookAt>' % (self.lookAt_Lat, self.lookAt_Lon, self.lookAt_Range, self.lookAt_Tilt, self.lookAt_Heading )
        return retval
        
        
    def computeLookAt(self):
        """
        Kml defining a camera perspective that puts the whole study region in view
        """
    
        from math import pi, sin, tan, sqrt, pow
        
        DEGREES = pi / 180.0
        EARTH_RADIUS = 6378137.0
  
        trans_geom = self.geometry
    
        w = trans_geom.extent[0]
        s = trans_geom.extent[1]
        e = trans_geom.extent[2]
        n = trans_geom.extent[3]
        
        center_lon = trans_geom.centroid.y
        center_lat = trans_geom.centroid.x
        
        lngSpan = abs( w - e ) # TODO: fix this calculation, it will break over the date line
        latSpan = abs( n - s )
        
        aspectRatio = 1.0
    
        PAD_FACTOR = 1.5 # add 50% to the computed range for padding
        
        aspectUse = max( aspectRatio, min((lngSpan / latSpan),1.0))
        alpha = (45.0 / (aspectUse + 0.4) - 2.0) * DEGREES # computed experimentally;
      
        # create LookAt using distance formula
        if lngSpan > latSpan:
            # polygon is wide
            beta = min(DEGREES * 90.0, alpha + lngSpan / 2.0 / EARTH_RADIUS)
        else:
            # polygon is taller
            beta = min(DEGREES * 90.0, alpha + latSpan / 2.0 / EARTH_RADIUS)
      
        self.lookAt_Range = PAD_FACTOR * EARTH_RADIUS * (sin(beta) *
            sqrt(1.0 / pow(tan(alpha),2.0) + 1.0) - 1.0)
            
        trans_geom.transform(4326)
        self.lookAt_Lat = trans_geom.centroid.y
        self.lookAt_Lon = trans_geom.centroid.x
        
        self.lookAt_Tilt = 0
        
        self.save()
    
        
        
        

#    def updated(self):
    
        # expire reports and report caches
        
        # reclip MPA's
        
