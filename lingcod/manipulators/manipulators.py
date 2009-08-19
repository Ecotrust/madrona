from django.contrib.gis.geos import GEOSGeometry, Polygon, Point, LinearRing
from django import forms
from lingcod.studyregion.models import *
from django.conf import settings


class ManipulatorBase():
    def __init__(self, **kwargs):
        self.kwargs = kwargs
     
    def manipulate(self):
        raise NotImplementedError()
        
    class Form:
        available = False
        
    class Options:
        name = 'Manipulator base class'
    
    
    
class ClipToShapeManipulator(ManipulatorBase):
    '''
    required kwargs:
        target_shape: GEOSGeometry of the shape to be clipped, in srid 4326
        clip_against: GEOSGeometry of the shape to clip against, in srid 4326
    '''
    
    def manipulate(self):
        target_shape = GEOSGeometry(self.kwargs['target_shape'])
        clip_against = GEOSGeometry(self.kwargs['clip_against'])
        ret_shape = target_shape.intersection( clip_against )
        ret_shape.set_srid(4326)
        return ret_shape
        
    class Options:
        name = 'ClipToShape manipulator'
        
        

class ClipToStudyRegionManipulator(ManipulatorBase):
    '''
    required kwargs:
        target_shape: GEOSGeometry of the shape to be clipped, in srid 4326
    '''
    
    def manipulate(self):
        target_shape = GEOSGeometry(self.kwargs['target_shape'])
        target_shape.set_srid(4326)
        target_shape.transform(settings.GEOMETRY_DB_SRID)
        
        clip_shape = StudyRegion.objects.current().geometry
        
        ret_shape = target_shape.intersection( clip_shape )
        ret_shape.set_srid(settings.GEOMETRY_DB_SRID)
        ret_shape.transform(4326)
        return ret_shape
        
    class Options:
        name = 'ClipToStudyRegion manipulator'
      
        
        
class ClipToGraticulesManipulator(ManipulatorBase):
    '''
    required kwargs:
        target_shape: GEOSGeometry of the shape to be clipped, in srid 4326
        n,s,e,w: directional boundaries, in srid 4326 (lat/lon)
    '''
    def manipulate(self):
                
        grat_box = Polygon( LinearRing([ Point( float(self.kwargs['w']), float(self.kwargs['n']) ), Point( float(self.kwargs['e']), float(self.kwargs['n']) ), Point( float(self.kwargs['e']), float(self.kwargs['s']) ), Point( float(self.kwargs['w']), float(self.kwargs['s']) ), Point( float(self.kwargs['w']), float(self.kwargs['n']))]))
        grat_box.set_srid(4326)
        
        target_shape = GEOSGeometry(self.kwargs['target_shape'])
        ret_shape = target_shape.intersection( grat_box )
        ret_shape.set_srid(4326)
        return ret_shape

        
    class Form(forms.Form):
        available = True
        n = forms.FloatField( label='Northern boundary' ) 
        s = forms.FloatField( label='Southern boundary' )
        e = forms.FloatField( label='Eastern boundary' )
        w = forms.FloatField( label='Western boundary' )
        target_shape = forms.CharField( widget=forms.HiddenInput )
        
        def clean(self):
            kwargs = self.cleaned_data
            my_manipulator = ClipToGraticulesManipulator( **kwargs )
            self.manipulated_geometry = my_manipulator.manipulate()
            return self.cleaned_data

        
    class Options:
        name = 'ClipToGraticules manipulator'
