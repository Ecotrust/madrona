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
    
    
    def kml(self):
        """
        Get the kml of the entire study region
        """
    
        trans_geom = self.geometry.clone()
        trans_geom.transform(4326)
        
        w = trans_geom.extent[0]
        s = trans_geom.extent[1]
        e = trans_geom.extent[2]
        n = trans_geom.extent[3]
        
        return self.kml_chunk(n,s,e,w)
        
    
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
    
        simplify_factor = max( 50, min( 200, 200.0 * float(zoom_width) / abs( self.geometry.extent[0] - self.geometry.extent[2])))
        
        #print zoom_width
        #print simplify_factor
        
        transform_geom = self.geometry.simplify(simplify_factor, preserve_topology=True)
        transform_geom = transform_geom.intersection( bounds )    
        transform_geom.transform(4326)
        
        
        # only add sub-regions if this is not our highest detail level
        bLastLevel = True #simplify_factor == 50
        max_lod_pixels = 250
        if bLastLevel:
            max_lod_pixels = -1
        
        retval = '<Document><Region><LatLonAltBox><north>%f</north><south>%f</south><east>%f</east><west>%f</west></LatLonAltBox><Lod><minLodPixels>125</minLodPixels><maxLodPixels>%d</maxLodPixels><minFadeExtent>0</minFadeExtent><maxFadeExtent>0</maxFadeExtent></Lod></Region><Placemark> <Style> <LineStyle> <color>ff00ffff</color> <width>2</width> </LineStyle> <PolyStyle> <color>8000ffff</color> </PolyStyle> </Style>%s</Placemark>' % ( n, s, e, w, max_lod_pixels, transform_geom.kml )
        
        # conditionally add sub-regions
        if not bLastLevel:
            subregions = '<NetworkLink><Region><LatLonAltBox><north>%f</north><south>%f</south><east>%f</east><west>%f</west></LatLonAltBox><Lod><minLodPixels>125</minLodPixels><maxLodPixels>250</maxLodPixels></Lod></Region><Link><href>http://localhost:8080/studyregion/kml_chunk/%f/%f/%f/%f/</href><viewRefreshMode>onRegion</viewRefreshMode></Link></NetworkLink>' % ( center_lat, s, e, center_lon, center_lat, s, e, center_lon )
            
            subregions = subregions +            '<NetworkLink><Region><LatLonAltBox><north>%f</north><south>%f</south><east>%f</east><west>%f</west></LatLonAltBox><Lod><minLodPixels>125</minLodPixels><maxLodPixels>250</maxLodPixels></Lod></Region><Link><href>http://localhost:8080/studyregion/kml_chunk/%f/%f/%f/%f/</href><viewRefreshMode>onRegion</viewRefreshMode></Link></NetworkLink>' % ( n, center_lat, e, center_lon, n, center_lat, e, center_lon )
            
            subregions = subregions +'<NetworkLink><Region><LatLonAltBox><north>%f</north><south>%f</south><east>%f</east><west>%f</west></LatLonAltBox><Lod><minLodPixels>125</minLodPixels><maxLodPixels>250</maxLodPixels></Lod></Region><Link><href>http://localhost:8080/studyregion/kml_chunk/%f/%f/%f/%f/</href><viewRefreshMode>onRegion</viewRefreshMode></Link></NetworkLink>' % ( center_lat, s, center_lon, w, center_lat, s, center_lon, w )
            
            subregions = subregions +'<NetworkLink><Region><LatLonAltBox><north>%f</north><south>%f</south><east>%f</east><west>%f</west></LatLonAltBox><Lod><minLodPixels>125</minLodPixels><maxLodPixels>250</maxLodPixels></Lod></Region><Link><href>http://localhost:8080/studyregion/kml_chunk/%f/%f/%f/%f/</href><viewRefreshMode>onRegion</viewRefreshMode></Link></NetworkLink>' % ( n, center_lat, center_lon, w, n, center_lat, center_lon, w )
            
            retval = retval + subregions
            
        retval = retval + '</Document>'
        
        return KmlWrap( retval )
    
        
    def lookAtKml(self):
        """
        Get the kml for the region's lookat values saved in the DB,
        or compute them if they are set to 0
        """
    
        if self.lookAt_Lat == 0.0 and self.lookAt_Lon == 0.0:
            self.computeLookAt()
    
        retval = '<Document><LookAt>\
            <latitude>%f</latitude>\
            <longitude>%f</longitude>\
            <range>%f</range>\
            <tilt>%f</tilt>\
            <heading>%f</heading>\
            <altitudeMode>clampToGround</altitudeMode>\
            </LookAt></Document>' % (self.lookAt_Lat, self.lookAt_Lon, self.lookAt_Range, self.lookAt_Tilt, self.lookAt_Heading )
        return KmlWrap( retval )
        
        
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
        
        center_lon = (w + e)/2
        center_lat = (n + s)/2
        
        lngSpan = abs( w - e )
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
        
