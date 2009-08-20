from lingcod.manipulators.manipulators import * 
from django.contrib.gis.geos import *
from lingcod.common.utils import LargestPolyFromMulti


class ClipToEstuariesManipulator(ManipulatorBase):

    def manipulate(self): 
        ''' 
            ClipToEstuariesManipulator expects 1 named kwargs: 'target_shape' 
            target_shape is a GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
            additional kwarg 'estuaries' can be passed in as well (currently used for testing purposes)
            returns a dictionary containing: 
                a 'status_code', a 'message', a 'clipped_shape' (or None value), and the 'original_shape'
            in the case where there is estuary overlap, 
                the largest poly (oceanic or estuary) is returned 
            otherwise, the original 'target_shape' geometry is returned untouched as clipped_shape
            
            status_code 6 "target_shape" is not included in POST, or if "estuaries" was not included and 
                          the application failed to find Estuaries objects in the database
            status_code 3 if target_shape is not valid geometry
            status_code 2 no estuaries are found
            status_code 0 if there is no overlap with estuary
            status_code 4 if target_shape is estuary only
            status_code 1 if target_shape is split between estuary and oceanic, oceanic part chosen
            status_code 5 if target_shape is split between estuary and oceanic, estuary part chosen
        '''

        keys = self.kwargs.keys()
        if 'target_shape' not in keys: 
            return {"status_code": "6", "message": "necessary argument 'target_shape' not found among kwarg keys", "clipped_shape": None, "original_shape": None}
         
        target_shape = GEOSGeometry(self.kwargs['target_shape'])
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
            except:
                return {"status_code": "6", "message": "Estuaries objects not found in database.  Check database or provide 'estuaries' kwarg.", "clipped_shape": None, "original_shape": None}
        
        target_shape.transform(settings.GEOMETRY_DB_SRID)
        
        estuary_clip = non_estuary_clip = None
        
        if not target_shape.valid:
            return {"status_code": "3", "message": "target_shape is not a valid geometry", "clipped_shape": None, "original_shape": target_shape}
  
        #check for existence of estuaries (if there are no estuaries, we're done here)
        if len(estuaries) == 0: 
            return {"status_code": "2", "message": "No estuaries found", "clipped_shape": target_shape, "original_shape": target_shape}
        
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
        
        #reset target_shape (target_shape) back to client-side srid
        target_shape.transform(settings.GEOMETRY_CLIENT_SRID)
        
        #if there was no estuary overlap
        if estuary_clip is None or estuary_clip.area == 0:
            return {"status_code": "0", "message": "No overlap with estuary", "clipped_shape": target_shape, "original_shape": target_shape}
        
        #if there was only estuary overlap (no oceanic overlap)
        if oceanic_clip is None or oceanic_clip.area == 0:
            estuary_clip.transform(settings.GEOMETRY_CLIENT_SRID)
            return {"status_code": "4", "message": "Mpa is estuary only", "clipped_shape": estuary_clip, "original_shape": target_shape}
        
        #if there was both estuary and oceanic overlap then return the larger of the two
        if oceanic_clip.area > estuary_clip.area:
            #oceanic clip is larger
            oceanic_clip.transform(settings.GEOMETRY_CLIENT_SRID)
            return {"status_code": "1", "message": "Mpa split between estuary and oceanic, oceanic part chosen", "clipped_shape": oceanic_clip, "original_shape": target_shape}
        else: 
            #estuary clip is larger
            estuary_clip.transform(settings.GEOMETRY_CLIENT_SRID)
            return {"status_code": "5", "message": "Mpa split between estuary and oceanic, estaury part chosen", "clipped_shape": estuary_clip, "original_shape": target_shape}

            
    class Options:
        name = 'ClipToEstuaries'   
        
manipulatorsDict[ClipToEstuariesManipulator.Options.name] = ClipToEstuariesManipulator