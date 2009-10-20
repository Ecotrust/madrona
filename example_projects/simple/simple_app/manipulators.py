from lingcod.manipulators.manipulators import * 
from lingcod.manipulators.manipulators import * 
from django.contrib.gis.geos import *
from models import *
from lingcod.studyregion.models import StudyRegion
from lingcod.common.utils import LargestPolyFromMulti


class EastWestManipulator(BaseManipulator):
    ''' 
        required arguments:
            target_shape, a GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        concerning **kwargs:
            kwargs is included to prevent errors resulting from extra arguments being passed to this manipulator from the generic view
        manipulate() return value:
            a dictionary containing the 'clipped_shape', and the 'orginal_shape', and optional 'message' and 'html' values
            All of the returned shape geometries should be in srid GEOMETRY_CLIENT_SRID (4326 for Google Earth) 
            In the case where there is both eastern and western overlap, the largest poly is returned 
            otherwise, the original 'target_shape' geometry is returned un-modified as 'clipped_shape'
    '''

    def __init__(self, target_shape, **kwargs):
        self.target_shape = target_shape
    
    def build_geometries(self):
        try:
            geom_builder = self.GeometryBuilder()
            western_half = geom_builder.get_western()
            eastern_half = geom_builder.get_eastern()
            return eastern_half, western_half
        except Exception, e:
            raise self.InternalException("Exception raised in EastWestManipulator while initializing east/west geometries: " + e.message)
    
    def manipulate(self): 
    
        #extract target_shape geometry
        target_shape = self.target_to_valid_geom(self.target_shape)
        
        #extract geometry from the database (or elsewhere) that will be used in the manipulation
        eastern_half, western_half = self.build_geometries()
        
        #ensure the database returned an actual geometry 
        if len(eastern_half) == 0 or len(western_half) == 0: 
            return {"message": "No geometries found", "clipped_shape": target_shape, "original_shape": target_shape}
              
        #ensure the input geometry is in the same projection as the database geometry
        target_shape.transform(settings.GEOMETRY_DB_SRID)

        #obtain the intersection of the input geometry and the eastern half
        try:
            eastern_clip = target_shape.intersection(eastern_half)
            eastern_clip.transform(settings.GEOMETRY_CLIENT_SRID)
        except Exception, e:
            raise self.InternalException("Exception raised in EastWestManipulator while intersecting with eastern geometry: " + e.message)  

        #obtain the intersection of the input geometry and the western half
        try:
            western_clip = target_shape.intersection(western_half)
            western_clip.transform(settings.GEOMETRY_CLIENT_SRID)
        except Exception, e:
            raise self.InternalException("Exception raised in EastWestManipulator while intersecting with western geometry: " + e.message)  

        #reset input geometry to client-side srid
        target_shape.transform(settings.GEOMETRY_CLIENT_SRID)

        #if there was no eastern geometry overlap (only western)
        if eastern_clip.area == 0.0:
            status_html = self.do_template("0")
            return self.result(western_clip, target_shape, status_html)

        #if there was no western geometry overlap (only eastern)
        if western_clip.area == 0.0:
            status_html = self.do_template("4")
            return self.result(eastern_clip, target_shape, status_html)
        
        #since the intersection resulted in two parts, determine the largest poly from each
        eastern_clip = LargestPolyFromMulti(eastern_clip)
        western_clip = LargestPolyFromMulti(western_clip)
        
        #return the larger of the two polys
        if western_clip.area > eastern_clip.area:
            status_html = self.do_template("1")
            return self.result(western_clip, target_shape, status_html)
        else: 
            status_html = self.do_template("5")
            return self.result(eastern_clip, target_shape, status_html)

     
    class GeometryBuilder():
        def __init__(self):
            #In our example we will simlpe build eastern_half and western_half geometries
            sr_geom = StudyRegion.objects.current().geometry
            sr_extent = sr_geom.extent
            self.w = sr_extent[0]
            self.s = sr_extent[1]
            self.e = sr_extent[2]
            self.n = sr_extent[3]
            self.center_lon = sr_geom.centroid.x
        
        def get_eastern(self):
            eastern_half = Polygon( LinearRing([ Point( self.center_lon, self.n ), Point( self.e, self.n ), Point( self.e, self.s ), Point( self.center_lon, self.s ), Point( self.center_lon, self.n)]))
            eastern_half.set_srid(settings.GEOMETRY_DB_SRID)
            return eastern_half
        
        def get_western(self):
            western_half = Polygon( LinearRing([ Point( self.center_lon, self.n ), Point( self.w, self.n ), Point( self.w, self.s ), Point( self.center_lon, self.s ), Point( self.center_lon, self.n)]))
            western_half.set_srid(settings.GEOMETRY_DB_SRID)
            return western_half
    
    
    class Options:
        name = 'EitherEastOrWest'  
        html_templates = {
            '0': 'simple_app/entirely_western.html', 
            '1': 'simple_app/dual_overlap_western.html', 
            '4': 'simple_app/entirely_eastern.html', 
            '5': 'simple_app/dual_overlap_eastern.html',
        } 

        
manipulatorsDict[EastWestManipulator.Options.name] = EastWestManipulator