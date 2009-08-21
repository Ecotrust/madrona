from django.contrib.gis.geos import GEOSGeometry, Polygon, Point, LinearRing
from django import forms
from lingcod.studyregion.models import *
from django.conf import settings
from lingcod.common.utils import LargestPolyFromMulti
from django.template.loader import render_to_string

# manipulatorsDict is bound to this module (won't be reinitialized if module is imported twice)
manipulatorsDict = {}


class ManipulatorBase():
    def __init__(self, **kwargs):
        self.kwargs = kwargs
     
    def manipulate(self):
        raise NotImplementedError()
        
    class Form:
        available = False
        
    class Options:
        name = 'Manipulator base class'
        template_name = 'manipulators/manipulator_default.html'
    
       
       
class ClipToShapeManipulator(ManipulatorBase):
    '''
        required kwargs:
            target_shape: GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
            clip_against: GEOSGeometry of the shape to clip against, in srid GEOMETRY_CLIENT_SRID (4326)
    '''
    
    def manipulate(self):
        target_shape = GEOSGeometry(self.kwargs['target_shape'])
        clip_against = GEOSGeometry(self.kwargs['clip_against'])
        ret_shape = target_shape.intersection( clip_against )
        ret_shape.set_srid(settings.GEOMETRY_CLIENT_SRID)
        return ret_shape
        
    class Options:
        name = 'ClipToShape'

manipulatorsDict[ClipToShapeManipulator.Options.name] = ClipToShapeManipulator

        
        
class ClipToStudyRegionManipulator(ManipulatorBase):
    '''
        required kwargs: 
            "target_shape": GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        returns a dictionary containing a 'status_code', a 'message', the 'clipped_shape', and the orginal shape
        the returned shape geometries will be in srid GEOMETRY_CLIENT_SRID (4326) 
        the clipped shape will be the largest (in area) polygon result from intersecting target_shape with each study region 
        
        status_code 6 if "target_shape" was not found in kwargs, or if "study_region" was not found in kwargs and
                         the application failed to find StudyRegion objects in the database
        status_code 3 if "target_shape" is not valid geometry
        status_code 4 if study_regions contained no geometries
        status_code 2 clipped shape is empty (no overlap with study region?)
        status_code 0 if "target_shape" is successfully clipped to study region(s)
        
        NOTE:   manipulate may still return a multi-part geometry
                it is up to the caller to determine whether that geometry should be reduced to a single polygon or not
    '''  
    
    def manipulate(self):                    
        keys = self.kwargs.keys()
        if 'target_shape' not in keys: 
            return {"status_code": "6", "message": "necessary argument 'target_shape' not found among kwarg keys", "html":"", "clipped_shape": None, "original_shape": None}
        
        target_shape = GEOSGeometry(self.kwargs['target_shape'])
        target_shape.set_srid(settings.GEOMETRY_CLIENT_SRID)

        if not target_shape.valid:
            status_html = render_to_string(self.Options.status_html_templates["3"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"status_code": "3", "message": "target_shape is not a valid geometry", "html":status_html, "clipped_shape": None, "original_shape": target_shape}
        
        clipped_shape = None 
        
        #'study_region' kwarg is FOR UNIT-TESTING PURPOSES ONLY, otherwise we access the database
        if 'study_region' in keys:
            study_region = GEOSGeometry(self.kwargs['study_region'])
            study_region.set_srid(settings.GEOMETRY_CLIENT_SRID)
            study_region.transform(settings.GEOMETRY_DB_SRID)
            study_regions = [study_region]
        else:
            try:
                study_regions = [sr.geometry for sr in StudyRegion.objects.all()]
            except:
                return {"status_code": "6", "message": "StudyRegion objects not found in database.  Check database or provide 'study_region' kwarg.", "html":"", "clipped_shape": None, "original_shape": None}
        
        #transform the target_shape to the srid of the study region(s)
        target_shape.transform(settings.GEOMETRY_DB_SRID)
        
        #loops through the study regions and takes the largest clipped_shape (intersection) found
        for study_region in study_regions:
            intersected_geom = target_shape.intersection(study_region)
            if clipped_shape is None:
                clipped_shape = intersected_geom
            elif intersected_geom.area > clipped_shape.area:
                clipped_shape = intersected_geom
        #assuming only one study region, the above loop could be replaced with the following:
        #clipped_shape = target_shape.intersection(study_region)
        
        #transform the target_shape back to its original srid
        target_shape.transform(settings.GEOMETRY_CLIENT_SRID)
        if clipped_shape is None:
            return  {"status_code": "4", "message": "study_regions contained no geometries", "clipped_shape": None, "html":"", "original_shape": target_shape}
        
        #transform clipped_shape to the appropriate srid
        clipped_shape.transform(settings.GEOMETRY_CLIENT_SRID)

        if clipped_shape.area == 0:
            status_html = render_to_string(self.Options.status_html_templates["2"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"status_code": "2", "message": "clipped geometry is empty (no overlap with study region?)", "html":status_html, "clipped_shape": clipped_shape, "original_shape": target_shape}
        
        largest_poly = LargestPolyFromMulti(clipped_shape)
        
        status_html = render_to_string(self.Options.status_html_templates["0"], {'MEDIA_URL':settings.MEDIA_URL})
        return {"status_code": "0", "message": "target_shape is clipped to study region", "html":status_html, "clipped_shape": largest_poly, "original_shape": target_shape}
     
        
    class Options:
        name = 'ClipToStudyRegion'
        status_html_templates = {
            '0':'manipulators/clipping.html', 
            '2':'manipulators/outside_studyregion.html', 
            '3':'manipulators/invalid_geometry.html'
        }
        
      
manipulatorsDict[ClipToStudyRegionManipulator.Options.name] = ClipToStudyRegionManipulator
    
    
class ClipToGraticuleManipulator(ManipulatorBase):
    '''
        ClipToGraticule takes up to 5 arguments: 
            'target_shape', in srid GEOMETRY_CLIENT_SRID (4326), is required
            'n', 's', 'e', 'w', expressed srid GEOMETRY_CLIENT_SRID (4326),  are all optional kwargs 
        the returned shape geometries will be in srid GEOMETRY_CLIENT_SRID (4326) 
        clipToGraticule returns a dictionary containing a 'status_code', a 'message', the 'clipped_shape', and the 'orginal_shape'
        
        status_code 6 if one or more necessary arguments is not found in kwargs
        status_code 3 if target_shape is not valid geometry
        status_code 4 if clipping failed in creating a clipped geometry
        status_code 2 if the clipped geometry is empty
        status_code 0 if target_shape is successfully clipped to the requested graticule(s)
    '''
    
    def manipulate(self):
        keys = self.kwargs.keys()
        if 'target_shape' not in keys: 
            return {"status_code": "6", "message": "necessary argument 'target_shape' not found among kwarg keys", "html":"", "clipped_shape": None, "original_shape": None}
        
        target_shape = GEOSGeometry(self.kwargs['target_shape'])
        target_shape.set_srid(settings.GEOMETRY_CLIENT_SRID) 
        
        if not target_shape.valid:
            return {"status_code": "3", "message": "target_shape is not a valid geometry", "html":"", "clipped_shape": None, "original_shape": target_shape}
            
        north = south = east = west = None
        keys = self.kwargs.keys()
        if 'n' in keys:
            north = self.kwargs['n']
        if 's' in keys:
            south = self.kwargs['s']
        if 'e' in keys:
            east = self.kwargs['e']
        if 'w' in keys:
            west = self.kwargs['w']

        #we will use target_shape.extent to fill in any missing graticule values
        geom_extent = target_shape.extent
        #fill in any missing graticule params with geom_extent (xmin, ymin, xmax, ymax) values
        if north is None:
            north = geom_extent[3]
        if south is None:
            south = geom_extent[1]
        if east is None:
            east = geom_extent[2]
        if west is None:
            west = geom_extent[0]
        
        #create polygon based on graticule params and/or geom_extent values 
        #clockwise starting from top-left 
        """
            top_left = (west, north)
            top_right = (east, north)
            bottom_right = (east, south)
            bottom_left = (west, south)
        """
        try:
            graticule_box = Polygon( LinearRing([ Point( float(west), float(north) ), Point( float(east), float(north) ), Point( float(east), float(south) ), Point( float(west), float(south) ), Point( float(west), float(north))]))
            graticule_box.set_srid(settings.GEOMETRY_CLIENT_SRID)
        except:
            return {"status_code": "4", "message": "Graticule clipping failed to create polygon", "html":"", "clipped_shape": None, "original_shape": target_shape}
        graticule_box.srid = settings.GEOMETRY_CLIENT_SRID
        
        #clip target_shape to the polygon created by the graticule parameters
        clipped_shape = target_shape.intersection(graticule_box)
        
        if clipped_shape.area == 0:
            return {"status_code": "2", "message": "Graticule dimensions produce an empty clipped geometry", "html":"", "clipped_shape": clipped_shape, "original_shape": target_shape}
        
        return {"status_code": "0", "message": "Graticule clipping was a success", "clipped_shape": clipped_shape, "html":"", "original_shape": target_shape}
                
            
    class Form(forms.Form):
        available = True
        n = forms.FloatField( label='Northern boundary', required=False ) 
        s = forms.FloatField( label='Southern boundary', required=False )
        e = forms.FloatField( label='Eastern boundary', required=False )
        w = forms.FloatField( label='Western boundary', required=False )
        target_shape = forms.CharField( widget=forms.HiddenInput )
        
        def clean(self):
            kwargs = self.cleaned_data
            my_manipulator = ClipToGraticuleManipulator( **kwargs )
            self.manipulation = my_manipulator.manipulate()
            return self.cleaned_data

        
    class Options:
        name = 'ClipToGraticule'

manipulatorsDict[ClipToGraticuleManipulator.Options.name] = ClipToGraticuleManipulator        
    