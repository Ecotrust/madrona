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
        
    #an idea for providing the client with default return values...not sure what to do about status_code...
    #currently used by ClipToShapeManipulator just for fun
    def manipulator_return_values(self, **kwargs):
        status_code = kwargs.get('status_code', '0')
        message = kwargs.get('message', '')
        html = kwargs.get('html', '')
        clipped_shape = kwargs.get('clipped_shape', None)
        original_shape = kwargs.get('original_shape', None)
        return {'status_code': status_code, 'message': message, 'html': html, 'clipped_shape': clipped_shape, 'original_shape': original_shape}
        
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
        return:
            a dictionary containing a 'status_code', a 'message', 'html', the 'clipped_shape', and the 'orginal_shape'
            all of the returned shape geometries will be in srid GEOMETRY_CLIENT_SRID (4326) 
            'clipped_shape' will be the result from intersecting 'target_shape' with 'clip_against' 
        
        status_code==6  if either "target_shape" or "clip_against" was not found in kwargs
                        both clipped_shape and original_shape will be returned as None
        status_code==3  if either "target_shape" or "clip_against" is not a valid geometry
                        clipped_shape will be returned as None      
        status_code==4  if intersection call failed for whatever reason
                        clipped_shape will be returned as None               
        status_code==2  clipped shape is empty (no overlap with "clip_against")
        status_code==0  if "target_shape" is successfully clipped to "clip_against"
    '''
    
    def manipulate(self):
        keys = self.kwargs.keys()

        if 'target_shape' not in keys or 'clip_against' not in keys: 
            message = "one or more necessary keys not found in kwargs"
            html_message = "From ClipToShapeManipulator: " + message
            status_html = render_to_string(self.Options.status_html_templates["9"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return self.manipulator_return_values(status_code="6", message=message, html=status_html, clipped_shape=None, original_shape=None)
         
        target_shape = GEOSGeometry(self.kwargs['target_shape'])
        target_shape.set_srid(settings.GEOMETRY_CLIENT_SRID)
        
        clip_against = GEOSGeometry(self.kwargs['clip_against'])
        clip_against.set_srid(settings.GEOMETRY_CLIENT_SRID)
        
        if not target_shape.valid:
            status_html = render_to_string(self.Options.status_html_templates["3"], {'MEDIA_URL':settings.MEDIA_URL})
            return self.manipulator_return_values(status_code="3", message="target_shape is not a valid geometry", html=status_html, clipped_shape=None, original_shape=target_shape)
        if not clip_against.valid:
            message = "clip_against is not a valid geometry"
            html_message = "From ClipToShapeManipulator: " + message
            status_html = render_to_string(self.Options.status_html_templates["9"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return self.manipulator_return_values(status_code="3", message="clip_against is not a valid geometry", clipped_shape=None, original_shape=target_shape)
        try:
            ret_shape = target_shape.intersection( clip_against )
        except:
            message = "intersection call failed"
            html_message = "From ClipToShapeManipulator: " + message
            status_html = render_to_string(self.Options.status_html_templates["9"], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': html_message})
            return self.manipulator_return_values(status_code="4", message="intersection call failed", clipped_shape=None, original_shape=target_shape)
        
        if ret_shape.area == 0:
            status_html = render_to_string(self.Options.status_html_templates["2"], {'MEDIA_URL':settings.MEDIA_URL})
            return self.manipulator_return_values(status_code="2", message="intersection resulted in empty geometry", html=status_html, clipped_shape=ret_shape, original_shape=target_shape)
        
        #largest_poly = LargestPolyFromMulti(ret_shape)???
        
        status_html = render_to_string(self.Options.status_html_templates["0"], {'MEDIA_URL':settings.MEDIA_URL})
        return self.manipulator_return_values(html=status_html, clipped_shape=ret_shape, original_shape=target_shape)
    ''' 
    #the following is USED FOR TESTING, 
    #assigns db current studyregion as the shape to clip against
    class Form(forms.Form):
        available = True
        target_shape = forms.CharField( widget=forms.HiddenInput )
        clip_against = forms.CharField( widget=forms.HiddenInput, required=False )
        
        def clean(self):
            kwargs = self.cleaned_data
            
            #used for sandbox testing
            clippy = StudyRegion.objects.current().geometry
            clippy.transform(4326)
            kwargs["clip_against"] = clippy.wkt 
            
            my_manipulator = ClipToShapeManipulator( **kwargs )
            self.manipulation = my_manipulator.manipulate()
            return self.cleaned_data
    '''
    class Options:
        name = 'ClipToShape'
        status_html_templates = {
            '0':'manipulators/shape_clip.html', 
            '2':'manipulators/outside_shape.html', 
            '3':'manipulators/invalid_geometry.html',
            '9':'manipulators/internal_error.html'
        }

manipulatorsDict[ClipToShapeManipulator.Options.name] = ClipToShapeManipulator

        
        
class ClipToStudyRegionManipulator(ManipulatorBase):
    '''
        required kwargs: 
            "target_shape": GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        optional kwargs:
            generally USED FOR TESTING ONLY
            "study_region": GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        returns:
            a dictionary containing 'status_code', 'message', 'html', 'clipped_shape', 'orginal_shape'
            all of the returned shape geometries will be in srid GEOMETRY_CLIENT_SRID (4326) 
            the clipped shape will be the largest (in area) polygon result from intersecting target_shape with the study region 
        
        status_code==6  if "target_shape" was not found in kwargs, or if "study_region" was not found in kwargs and the application failed to find StudyRegion objects in the database
                        both clipped_shape and original_shape will be returned as None
        status_code==3  if "target_shape" is not valid geometry
                        clipped_shape will be returned as None
        status_code==4  if study_regions contained no geometries
                        clipped_shape will be returned as None                       
        status_code==2  clipped shape is empty (no overlap with study region?)
        status_code==0  if "target_shape" is successfully clipped to study region(s)
    '''  
    
    def manipulate(self):                    
        keys = self.kwargs.keys()
        if 'target_shape' not in keys: 
            return {"status_code": "6", "message": "necessary argument 'target_shape' not found among kwarg keys", "html": "", "clipped_shape": None, "original_shape": None}
        
        target_shape = GEOSGeometry(self.kwargs['target_shape'])
        target_shape.set_srid(settings.GEOMETRY_CLIENT_SRID)

        if not target_shape.valid:
            status_html = render_to_string(self.Options.status_html_templates["3"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"status_code": "3", "message": "target_shape is not a valid geometry", "html": status_html, "clipped_shape": None, "original_shape": target_shape}
        
        clipped_shape = None 
        
        #'study_region' kwarg is FOR UNIT-TESTING PURPOSES ONLY, otherwise we access the database
        if 'study_region' in keys:
            study_region = GEOSGeometry(self.kwargs['study_region'])
            study_region.set_srid(settings.GEOMETRY_CLIENT_SRID)
            study_region.transform(settings.GEOMETRY_DB_SRID)
            #study_regions = [study_region]
        else:
            try:
                study_region = StudyRegion.objects.current().geometry
            except:
                return {"status_code": "6", "message": "StudyRegion.objects.current() not found in database.", "html": "", "clipped_shape": None, "original_shape": None}
        
        #transform the target_shape to the srid of the study region(s)
        target_shape.transform(settings.GEOMETRY_DB_SRID)
        
        #loops through the study regions and takes the largest clipped_shape (intersection) found
        """
        for study_region in study_regions:
            intersected_geom = target_shape.intersection(study_region)
            if clipped_shape is None:
                clipped_shape = intersected_geom
            elif intersected_geom.area > clipped_shape.area:
                clipped_shape = intersected_geom
        """
        #assuming only one study region, the above loop could be replaced with the following:
        clipped_shape = target_shape.intersection(study_region)
        
        #transform the target_shape back to its original srid
        target_shape.transform(settings.GEOMETRY_CLIENT_SRID)
        if clipped_shape is None:
            return  {"status_code": "4", "message": "study_regions contained no geometries", "html": "", "clipped_shape": None, "original_shape": target_shape}
        
        #transform clipped_shape to the appropriate srid
        clipped_shape.transform(settings.GEOMETRY_CLIENT_SRID)

        if clipped_shape.area == 0:
            status_html = render_to_string(self.Options.status_html_templates["2"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"status_code": "2", "message": "clipped geometry is empty (no overlap with study region?)", "html": status_html, "clipped_shape": clipped_shape, "original_shape": target_shape}
        
        largest_poly = LargestPolyFromMulti(clipped_shape)
        
        status_html = render_to_string(self.Options.status_html_templates["0"], {'MEDIA_URL':settings.MEDIA_URL})
        return {"status_code": "0", "message": "target_shape is clipped to study region", "html": status_html, "clipped_shape": largest_poly, "original_shape": target_shape}
        
        
    class Options:
        name = 'ClipToStudyRegion'
        status_html_templates = {
            '0':'manipulators/studyregion_clip.html', 
            '2':'manipulators/outside_studyregion.html', 
            '3':'manipulators/invalid_geometry.html'
        }
        
      
manipulatorsDict[ClipToStudyRegionManipulator.Options.name] = ClipToStudyRegionManipulator
    
    
class ClipToGraticuleManipulator(ManipulatorBase):
    '''
        required kwargs: 
            "target_shape":  GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        optional kwargs:
            "n", "s", "e", "w":  expressed srid GEOMETRY_CLIENT_SRID (4326) 
        returns:
            a dictionary containing 'status_code', 'message', 'html', 'clipped_shape', and 'orginal_shape'
            all of the returned shape geometries will be in srid GEOMETRY_CLIENT_SRID (4326) 
            the clipped shape will be the largest (in area) polygon result from clipping target_shape with the requested graticule(s) 
        
        status_code==6 if one or more necessary arguments is not found in kwargs
                       both clipped_shape and original_shape will be returned as None
        status_code==3 if target_shape is not valid geometry
                       clipped_shape will be returned as None
        status_code==4 if clipping failed in creating a clipped geometry
                       clipped_shape will be returned as None
        status_code==2 if the clipped geometry is empty
        status_code==0 if target_shape is successfully clipped to the requested graticule(s)
    '''
    
    def manipulate(self):
        keys = self.kwargs.keys()
        if 'target_shape' not in keys: 
            return {"status_code": "6", "message": "necessary argument 'target_shape' not found among kwarg keys", "html": "", "clipped_shape": None, "original_shape": None}
        
        target_shape = GEOSGeometry(self.kwargs['target_shape'])
        target_shape.set_srid(settings.GEOMETRY_CLIENT_SRID) 
        
        if not target_shape.valid:
            status_html = render_to_string(self.Options.status_html_templates["3"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"status_code": "3", "message": "target_shape is not a valid geometry", "html": status_html, "clipped_shape": None, "original_shape": target_shape}
            
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
            return {"status_code": "4", "message": "Graticule clipping failed to create polygon", "html": "", "clipped_shape": None, "original_shape": target_shape}
        graticule_box.srid = settings.GEOMETRY_CLIENT_SRID
        
        #clip target_shape to the polygon created by the graticule parameters
        clipped_shape = target_shape.intersection(graticule_box)
        
        if clipped_shape.area == 0:
            status_html = render_to_string(self.Options.status_html_templates["2"], {'MEDIA_URL':settings.MEDIA_URL})
            return {"status_code": "2", "message": "Graticule dimensions produce an empty clipped geometry", "html": status_html, "clipped_shape": clipped_shape, "original_shape": target_shape}
        
        largest_poly = LargestPolyFromMulti(clipped_shape)
        
        status_html = render_to_string(self.Options.status_html_templates["0"], {'MEDIA_URL':settings.MEDIA_URL})
        return {"status_code": "0", "message": "Graticule clipping was a success", "html": status_html, "clipped_shape": clipped_shape, "original_shape": target_shape}
                
            
    class Form(forms.Form):
        available = True
        n = forms.FloatField( label='Northern boundary', required=False ) 
        s = forms.FloatField( label='Southern boundary', required=False )
        e = forms.FloatField( label='Eastern boundary', required=False )
        w = forms.FloatField( label='Western boundary', required=False )
        target_shape = forms.CharField( widget=forms.HiddenInput )
        
        def clean(self):
            kwargs = self.cleaned_data
            
            #used for sandbox testing
            #kwargs["w"] = -118.5 
            
            my_manipulator = ClipToGraticuleManipulator( **kwargs )
            self.manipulation = my_manipulator.manipulate()
            return self.cleaned_data

        
    class Options:
        name = 'ClipToGraticule'
        status_html_templates = {
            '0':'manipulators/graticule.html', 
            '2':'manipulators/no_graticule_overlap.html', 
            '3':'manipulators/invalid_geometry.html'
        }

manipulatorsDict[ClipToGraticuleManipulator.Options.name] = ClipToGraticuleManipulator        
    