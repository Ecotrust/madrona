from lingcod.manipulators.manipulators import * 
from django.contrib.gis.geos import *
from mlpa.models import *
from lingcod.common.utils import LargestPolyFromMulti


class ClipToEstuariesManipulator(BaseManipulator):
    ''' 
        required argument:
            target_shape, a GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        optional arguments:
            generally USED FOR TESTING PURPOSES ONLY
            estuaries, a GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326) 
        concerning **kwargs:
            kwargs is included to prevent errors resulting from extra arguments being passed to this manipulator from the generic view
        manipulate() return value:
            a dictionary containing the 'clipped_shape', and the 'orginal_shape', and optional 'message' and 'html' values
            all of the returned shape geometries will be in srid GEOMETRY_CLIENT_SRID (4326) 
            in the case where there is estuary overlap, the largest poly (oceanic or estuary) is returned 
            otherwise, the original target_shape geometry is returned un-modified as 'clipped_shape'
        
        html_templates==9   This represents an 'internal error' and is accessed by raising a ManipulatorInternalException
                            This should occur under the following circumstances:
                                if Estuaries not found in database
                                or geometry manipulations failed
                            clipped_shape will be returned as None
        html_templates==3   This represents an 'user error' and is accessed by raising a InvalidGeometryException
                            This should occur under the following circumstances:
                                if geometry can not be generated from target_shape 
                                or if target_shape is not a valid geometry
                            clipped_shape will be returned as None      
        html_templates==4   if target_shape is estuary only    
        html_templates==2   if target_shape is split between estuary and oceanic
        html_templates==0   if there is no overlap with estuary found
        
        no template returned when Estuaries is empty
        in this case, clipped_shape will be returned as target_shape
    '''

    def __init__(self, target_shape, estuaries=None, **kwargs):
        self.target_shape = target_shape
        self.estuaries = estuaries
        
    def intersect_and_union(self, target, estuaries):
        '''
            Intersect the target_shape with each of the estuaries in the database.  
            As there may be multiple estuaries present within the boundaries of target_shape,
            we want to include all intersections within the estuary_clip return geometry.
        '''
        estuary_clip = None
        for estuary in estuaries:
            intersected_geom = target.intersection(estuary)
            if not intersected_geom.empty:
                if estuary_clip is None:
                    estuary_clip = intersected_geom
                else:
                    estuary_clip = estuary_clip.union(intersected_geom)
        return estuary_clip
                    
    def manipulate(self): 
        #extract target_shape geometry
        target_shape = self.target_to_valid_geom(self.target_shape)
        #extract estuaries geometry
        #estuaries argument is FOR UNIT-TESTING PURPOSES ONLY, otherwise we access the database
        if self.estuaries is not None:
            try:
                estuaries = GEOSGeometry(self.estuaries)
                estuaries.set_srid(settings.GEOMETRY_CLIENT_SRID)
                estuaries.transform(settings.GEOMETRY_DB_SRID)
                estuaries = [est for est in estuaries]
            except Exception, e:
                raise self.InternalException("Exception raised in ClipToEstuariesManipulator while initializing estuaries geometry: " + e.message)
        else:
            try:
                estuaries = [est.geometry for est in Estuaries.objects.all()]
            except Exception, e:
                raise self.InternalException("Exception raised in ClipToEstuariesManipulator while obtaining estuaries geometry from database: " + e.message)    
        
        #check for existence of estuaries (if there are no estuaries, we're done here)
        if len(estuaries) == 0: 
            #message="No estuaries found"
            #return self.result(target_shape, target_shape, message="No estuaries found")
            return self.result(target_shape)
        
        #intersect the two geometries
        try:
            target_shape.transform(settings.GEOMETRY_DB_SRID)
            #Step 1:  Union any and all estuary intersection results 
            estuary_clip = self.intersect_and_union(target_shape, estuaries)
            #Step 2:  If the target_shape overlaps an estuary, divide target_shape into two parts:
            #         oceanic_clip (target_shape without estuary part) and estuary_clip (estuary part only)
            if estuary_clip is not None:
                oceanic_clip = target_shape.difference(estuary_clip)
                oceanic_clip = LargestPolyFromMulti(oceanic_clip)
                estuary_clip = LargestPolyFromMulti(estuary_clip)
            else:
                oceanic_clip = target_shape
        except Exception, e:
            raise self.InternalException("Exception raised in ClipToEstuariesManipulator while manipulating geometries: " + e.message)  
       
        #reset target_shape to client-side srid
        target_shape.transform(settings.GEOMETRY_CLIENT_SRID)
        
        #if there was no estuary overlap
        if estuary_clip is None or estuary_clip.area == 0:
            #message = "No overlap with estuary"
            status_html = self.do_template("0")
            oceanic_clip = target_shape
            #return self.result(oceanic_clip, target_shape, status_html, "No overlap with estuary")
            return self.result(oceanic_clip, status_html)
        
        estuary_clip.transform(settings.GEOMETRY_CLIENT_SRID)
        
        #if there was only estuary overlap (no oceanic overlap)
        if oceanic_clip is None or oceanic_clip.area == 0:
            #message = "Mpa is estuary only"
            status_html = self.do_template("4")
            #return self.result(estuary_clip, target_shape, status_html, "Mpa is estuary only")
            return self.result(estuary_clip, status_html)
        
        oceanic_clip.transform(settings.GEOMETRY_CLIENT_SRID)  
        
        #if there was both estuary and oceanic overlap then return the larger of the two
        if oceanic_clip.area > estuary_clip.area:
            message = "Non-Estuary Part"
            status_html = self.do_template("2", message)
            #return self.result(oceanic_clip, target_shape, status_html, message) 
            return self.result(oceanic_clip, status_html) 
        else: 
            message = "Estuary Part"
            status_html = self.do_template("2", message)
            #return self.result(estuary_clip, target_shape, status_html, message) 
            return self.result(estuary_clip, status_html) 
            
    class Options:
        name = 'ClipToEstuaries'  
        html_templates = {
            '0': 'mlpa/no_estuary_overlap.html',
            '2': 'mlpa/estuary.html',
            '4': 'mlpa/only_estuary.html', 
        } 

        
manipulatorsDict[ClipToEstuariesManipulator.Options.name] = ClipToEstuariesManipulator