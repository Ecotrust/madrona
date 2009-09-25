from lingcod.manipulators.manipulators import * 
from lingcod.manipulators.manipulators import * 
from django.contrib.gis.geos import *
from models import *
from lingcod.studyregion.models import StudyRegion
from lingcod.common.utils import LargestPolyFromMulti


class EastWestManipulator(ManipulatorBase):
    ''' 
        required arguments:
            'target_shape', a GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        returns:
            a dictionary that usually includes a 'message', 'html', 'clipped_shape', and 'original_shape'
            At minimum, it's a good idea to include at least the following two keys:
            a 'clipped_shape' (or None value), and the 'original_shape'
            All of the returned shape geometries should be in srid GEOMETRY_CLIENT_SRID (4326 for Google Earth) 
            In the case where there is both eastern and western overlap, the largest poly is returned 
            otherwise, the original 'target_shape' geometry is returned un-modified as 'clipped_shape'
    '''
    
    def manipulate(self): 

        keys = self.kwargs.keys()

        #make sure an input geometry was provided
        if 'target_shape' not in keys: 
            message = "necessary argument 'target_shape' not found among kwarg keys"
            html_message = "From EastWestManipulator: " + message
            status_html = render_to_string(self.Options.html_templates["9"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return {"message": message, "html": status_html, "clipped_shape": None, "original_shape": None}
            
        #build the geometry from the wkt that was passed in
        try:
            target_shape = GEOSGeometry(self.kwargs['target_shape'])
        except:
            message = "unable to generate geometry from 'target_shape'"
            html_message = "From EastWestManipulator: " + message
            status_html = render_to_string(self.Options.html_templates["3"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return {"message": message, "html": status_html, "clipped_shape": None, "original_shape": None}
        
        #as the input geometry has no srid, an appropriate srid should be assigned  
        target_shape.set_srid(settings.GEOMETRY_CLIENT_SRID)

        #grab a geometry from the database (or elsewhere) that will be used in the manipulation
        try:
            #In our example we will simlpe build eastern_half and western_half geometries
            sr_extent = StudyRegion.objects.current().geometry 
            w = sr_extent.extent[0]
            s = sr_extent.extent[1]
            e = sr_extent.extent[2]
            n = sr_extent.extent[3]
            center_lon = sr_extent.centroid.x
            
            eastern_half = Polygon( LinearRing([ Point( center_lon, n ), Point( e, n ), Point( e, s ), Point( center_lon, s ), Point( center_lon, n)]))
            eastern_half.set_srid(settings.GEOMETRY_DB_SRID)
            
            western_half = Polygon( LinearRing([ Point( center_lon, n ), Point( w, n ), Point( w, s ), Point( center_lon, s ), Point( center_lon, n)]))
            western_half.set_srid(settings.GEOMETRY_DB_SRID)
        except:
            message = "Objects not found in database."
            html_message = "From EastWestManipulator: " + message 
            status_html = render_to_string(self.Options.html_templates["9"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return {"message": message, "html": status_html, "clipped_shape": None, "original_shape": None}
        
        #ensure the input geometry is in the same projection as the database geometry
        target_shape.transform(settings.GEOMETRY_DB_SRID)
        
        eastern_clip = western_clip = None

        #ensure the input geometry is a valid geometry
        if not target_shape.valid:
            status_html = render_to_string(self.Options.html_templates["3"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"html": status_html, "clipped_shape": None, "original_shape": target_shape}
  
        #ensure the database returned an actual geometry 
        if len(eastern_half) == 0 or len(western_half) == 0: 
            return {"message": "No geometries found", "clipped_shape": target_shape, "original_shape": target_shape}
        
        #obtain the intersection of the input geometry and the eastern half
        try:
            eastern_clip = target_shape.intersection(eastern_half)
        except:
            message = "east intersection failed"
            html_message = "From EastWestManipulator: " + message
            status_html = render_to_string(self.Options.html_templates["9"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return {"message": message, "html": status_html, "clipped_shape": None, "original_shape": target_shape}

        #obtain the intersection of the input geometry and the western half
        try:
            western_clip = target_shape.intersection(western_half)
        except:
            message = "west intersection failed"
            html_message = "From EastWestManipulator: " + message
            status_html = render_to_string(self.Options.html_templates["9"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return {"message": message, "html": status_html, "clipped_shape": None, "original_shape": target_shape}
 
        #If the intersection results in two parts (target is split in western and eastern parts)
        #the largest polygon from each is determined for the potential final return value
        if eastern_clip.area > 0.0 and western_clip.area > 0.0:
            eastern_clip = LargestPolyFromMulti(eastern_clip)
            western_clip = LargestPolyFromMulti(western_clip)
        
        #reset input geometry to client-side srid
        target_shape.transform(settings.GEOMETRY_CLIENT_SRID)

        #if there was no eastern geometry overlap (only western)
        if eastern_clip.area == 0.0:
            western_clip.transform(settings.GEOMETRY_CLIENT_SRID)
            status_html = render_to_string(self.Options.html_templates["0"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"html": status_html, "clipped_shape": western_clip, "original_shape": target_shape}
        
        #if there was no western geometry overlap (only eastern)
        if western_clip.area == 0.0:
            eastern_clip.transform(settings.GEOMETRY_CLIENT_SRID)
            status_html = render_to_string(self.Options.html_templates["4"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"html": status_html, "clipped_shape": eastern_clip, "original_shape": target_shape}
        
        #if there was both western geometry and eastern geometry overlap then return the larger of the two
        if western_clip.area > eastern_clip.area:
            western_clip.transform(settings.GEOMETRY_CLIENT_SRID)
            status_html = render_to_string(self.Options.html_templates["1"], {'MEDIA_URL': settings.MEDIA_URL})
            return {"html": status_html, "clipped_shape": western_clip, "original_shape": target_shape}
        else: 
            eastern_clip.transform(settings.GEOMETRY_CLIENT_SRID)
            status_html = render_to_string(self.Options.html_templates["5"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"html": status_html, "clipped_shape": eastern_clip, "original_shape": target_shape}

            
    class Options:
        name = 'EitherEastOrWest'  
        html_templates = {
            '0': 'simple_app/entirely_western.html', 
            '1': 'simple_app/dual_overlap_western.html', 
            '3': 'manipulators/invalid_geometry.html',
            '4': 'simple_app/entirely_eastern.html', 
            '5': 'simple_app/dual_overlap_eastern.html',
            '9': 'manipulators/internal_error.html'  
        } 

        
manipulatorsDict[EastWestManipulator.Options.name] = EastWestManipulator