from lingcod.manipulators.manipulators import * 
from django.contrib.gis.geos import *
from mlpa.models import *
from lingcod.common.utils import LargestPolyFromMulti


class ClipToEstuariesManipulator(ManipulatorBase):
    ''' 
        required arguments:
            'target_shape', a GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        optional arguements:
            generally USED FOR TESTING PURPOSES ONLY
            'estuaries', a GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326) 
        returns:
            a dictionary containing a 'message', a 'clipped_shape' (or None value), and the 'original_shape'
            all of the returned shape geometries will be in srid GEOMETRY_CLIENT_SRID (4326) 
            in the case where there is estuary overlap, the largest poly (oceanic or estuary) is returned 
            otherwise, the original 'target_shape' geometry is returned un-modified as 'clipped_shape'
        
        html_templates==9   if "target_shape" was not found in kwargs
                            or if Estuaries not found in database
                            or geometry manipulations failed
                            clipped_shape will be returned as None
        html_templates==4   if 'target_shape' is estuary only 
        html_templates==3   if geometry can not be generated from "target_shape" 
                            or if "target_shape" is not a valid geometry
                            clipped_shape will be returned as None         
        html_templates==2   if 'target_shape' is split between estuary and oceanic, estuary part chosen
        html_templates==1   if 'target_shape' is split between estuary and oceanic, oceanic part chosen
        html_templates==0   if there is no overlap with estuary found
        
        no template returned when Estuaries is empty
        in this case, clipped_shape will be returned as target_shape
        '''
    def manipulate(self): 

        keys = self.kwargs.keys()
        if 'target_shape' not in keys: 
            message = "necessary argument 'target_shape' not found among kwarg keys"
            html_message = "From ClipToEstuariesManipulator: " + message
            status_html = render_to_string(self.Options.html_templates["9"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return {"message": message, "html": status_html, "clipped_shape": None, "original_shape": None}
         
        try:
            target_shape = GEOSGeometry(self.kwargs['target_shape'])
        except:
            message = "unable to generate geometry from 'target_shape'"
            html_message = "From ClipToEstuariesManipulator: " + message
            status_html = render_to_string(self.Options.html_templates["3"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return {"message": message, "html": status_html, "clipped_shape": None, "original_shape": None}
         
        target_shape.set_srid(settings.GEOMETRY_CLIENT_SRID)

        #'estuaries' kwarg is FOR UNIT-TESTING PURPOSES ONLY, otherwise we access the database
        if 'estuaries' in keys:
            estuaries = GEOSGeometry(self.kwargs['estuaries'])
            estuaries.set_srid(settings.GEOMETRY_CLIENT_SRID)
            estuaries.transform(settings.GEOMETRY_DB_SRID)
            estuaries = [est for est in estuaries]
        else:
            try:
                estuaries = [est.geometry for est in Estuaries.objects.all()]
                #THE FOLLOWING IS FOR TESTING PURPOSES -- simple shape in south coast
                #IN THE CASE IN WHCIH THE ESTUARIES ARE NOT YET LOADED INTO DATABASE
                #estuaries = GEOSGeometry('MULTIPOLYGON (((-118.9953602060336800 33.6703166802659840, -117.0933248787674000 33.6703166802659840, -117.0933248787674000 32.5307977227377730, -118.9953602060336800 32.5307977227377730, -118.9953602060336800 33.6703166802659840)))')
                #estuaries.set_srid(settings.GEOMETRY_CLIENT_SRID)
                #estuaries.transform(settings.GEOMETRY_DB_SRID)
            except:
                message = "Estuaries objects not found in database."
                html_message = "From ClipToEstuariesManipulator: " + message + "  Check database or provide 'estuaries' kwarg."
                status_html = render_to_string(self.Options.html_templates["9"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
                return {"message": message, "html": status_html, "clipped_shape": None, "original_shape": None}
        
        target_shape.transform(settings.GEOMETRY_DB_SRID)
        
        estuary_clip = non_estuary_clip = None
        
        if not target_shape.valid:
            status_html = render_to_string(self.Options.html_templates["3"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"message": "target_shape is not a valid geometry", "html": status_html, "clipped_shape": None, "original_shape": target_shape}
  
        #check for existence of estuaries (if there are no estuaries, we're done here)
        if len(estuaries) == 0: 
            return {"message": "No estuaries found", "html": "", "clipped_shape": target_shape, "original_shape": target_shape}
        
        try:
            #Step 1:  Union any and all estuary intersection results 
            for estuary in estuaries:
                intersected_geom = target_shape.intersection(estuary)
                if not intersected_geom.empty:
                    if estuary_clip is None:
                        estuary_clip = intersected_geom
                    else:
                        estuary_clip = estuary_clip.union(intersected_geom)
            
            #Step 2:  If the target_shape overlaps an estuary, divide target_shape 
            #         into two parts, oceanic_clip (target_shape without estuary part) and estuary_clip (estuary part only)
            #         largest poly from each is taken for potential return value 'clipped_shape'
            if estuary_clip is not None:
                oceanic_clip = target_shape.difference(estuary_clip)
                oceanic_clip = LargestPolyFromMulti(oceanic_clip)
                estuary_clip = LargestPolyFromMulti(estuary_clip)
            else:
                oceanic_clip = target_shape
        except:
            target_shape.transform(settings.GEOMETRY_CLIENT_SRID)
            message = "geometry manipulations failed"
            html_message = "From ClipToEstuariesManipulator: " + message
            status_html = render_to_string(self.Options.html_templates["9"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return {"message": message, "html": status_html, "clipped_shape": None, "original_shape": target_shape}
        
        #reset target_shape (target_shape) back to client-side srid
        target_shape.transform(settings.GEOMETRY_CLIENT_SRID)
        
        #if there was no estuary overlap
        if estuary_clip is None or estuary_clip.area == 0:
            status_html = render_to_string(self.Options.html_templates["0"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"message": "No overlap with estuary", "html": status_html, "clipped_shape": target_shape, "original_shape": target_shape}
        
        #if there was only estuary overlap (no oceanic overlap)
        if oceanic_clip is None or oceanic_clip.area == 0:
            estuary_clip.transform(settings.GEOMETRY_CLIENT_SRID)
            status_html = render_to_string(self.Options.html_templates["4"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"message": "Mpa is estuary only", "html": status_html, "clipped_shape": estuary_clip, "original_shape": target_shape}
        
        #if there was both estuary and oceanic overlap then return the larger of the two
        if oceanic_clip.area > estuary_clip.area:
            #oceanic clip is larger
            oceanic_clip.transform(settings.GEOMETRY_CLIENT_SRID)
            status_html = render_to_string(self.Options.html_templates["1"], {'MEDIA_URL': settings.MEDIA_URL})
            return {"message": "Mpa split between estuary and oceanic, oceanic part chosen", "html": status_html, "clipped_shape": oceanic_clip, "original_shape": target_shape}
        else: 
            #estuary clip is larger
            estuary_clip.transform(settings.GEOMETRY_CLIENT_SRID)
            status_html = render_to_string(self.Options.html_templates["2"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"message": "Mpa split between estuary and oceanic, estaury part chosen", "html": status_html, "clipped_shape": estuary_clip, "original_shape": target_shape}

            
    class Options:
        name = 'ClipToEstuaries'  
        html_templates = {
            '0': 'mlpa/no_estuary_overlap.html', 
            '1': 'mlpa/estuary_clip_oceanic.html', 
            '2': 'mlpa/estuary_clip_estuarine.html',
            '3': 'manipulators/invalid_geometry.html',
            '4': 'mlpa/only_estuary.html', 
            '9': 'manipulators/internal_error.html' 
        } 

        
manipulatorsDict[ClipToEstuariesManipulator.Options.name] = ClipToEstuariesManipulator