from django.contrib.gis.db import models
from django.contrib.gis.gdal import *
from django.contrib.gis import geos
from django.contrib.gis.measure import *
from django.core.exceptions import MultipleObjectsReturned
from django.template.defaultfilters import slugify
from django.db import transaction
from django.conf import settings
from osgeo import ogr
#from django.contrib.gis.utils import LayerMapping
import os
import tempfile
import zipfile
import glob


# I think this should stay here unless I want to pull some zip handling stuff into another app.
SHP_EXTENSIONS = ['shp','dbf','prj','sbn','sbx','shx','shp.xml','qix','fix']

def endswithshp(string):
    return string.endswith('.shp')
        
def zip_check(ext, zip_file):
    if not True in [info.filename.endswith(ext) for info in zip_file.infolist()]:
        return False
    return True
    
def validate_zipped_shp(file_path):
    # Just check to see if it's a valid zip and that it has the four necessary parts.
    # We're not checking to make sure it can be read as a shapefile  probably should somewhere.
    # We should also probably verify that the projection is what we expect.
    # I got a lot of this code from Dane Sprinmeyer's django-shapes app
    if not os.path.exists(file_path):
        return False, 'This file does not exist: %s' % file_path
    elif not zipfile.is_zipfile(file_path):
        return False, 'That file is not a valid Zip Archive'
    else:
        zfile = zipfile.ZipFile(file_path)
    if not zip_check('shp', zfile):
        return False, 'Found Zip Archive but no file with a .shp extension found inside.'
    elif not zip_check('prj', zfile):
        return False, 'You must supply a .prj file with the Shapefile to indicate the projection.'
    elif not zip_check('dbf', zfile):
        return False, 'You must supply a .dbf file with the Shapefile to supply attribute data.'
    elif not zip_check('shx', zfile):
        return False, 'You must supply a .shx file for the Shapefile to have a valid index.'
    else:
        return True, None

def largest_poly_from_multi(geom):
    ''' takes a polygon or a multipolygon and returns only the largest polygon '''
    if geom.num_geom > 1:
        geom_area = 0.0
        for g in geom: # find the largest polygon in the multi polygon and use that
            if g.area > geom_area:
                the_one_true_geom = g
                geom_area = g.area
    else:
        the_one_true_geom = geom
    return the_one_true_geom

def clean_geometry(geom):
    from django.db import connection
    cursor = connection.cursor()
    query = "select cleangeometry(st_geomfromewkt(\'%s\')) as geometry" % geom.ewkt
    cursor.execute(query)
    row = cursor.fetchone()
    newgeom = geos.fromstr(row[0])
    # sometimes, clean returns a multipolygon
    geometry = largest_poly_from_multi(newgeom)
    
    if not geometry.valid or geometry.num_coords < 2:
        raise Exception("I can't clean this geometry. Dirty, filthy geometry. This geometry should be ashamed.")
    else:
        return geometry


def zip_from_shp(shp_path):
    # given a path to a '.shp' file, zip it and return the filename and a file object
    from django.core.files import File
    
    directory, file_with_ext = os.path.split(shp_path)
    if file_with_ext.count('.') <> 1:
        raise Exception('Shapefile name should only have one \'.\' in them.  This file name has %i.' % file_with_ext.count('.') )
    else:
        filename, ext = file_with_ext.split('.')
    zfile_path = os.path.join(directory, ('.').join([filename,'zip']) )    
    zfile = zipfile.ZipFile(zfile_path, 'w')
    for name in glob.glob( os.path.join(directory,filename + '.*') ):
        bn = os.path.basename(name)
        part_filenam, part_ext = bn.split('.',1)
        # make sure we're only adding allowed shapefile extensions
        if part_ext in SHP_EXTENSIONS:
            zfile.write(name, bn, zipfile.ZIP_DEFLATED)
    zfile.close()
    
    return filename, File( open(zfile_path) )
        
class DataLayer(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField(null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name
        
    @property
    def active_shapefile(self):
        """Return the active shapefile (or None if there aren't any). Raise a stink if there is more than one shapefile marked as active."""
        try:
            return self.shapefile_set.get(active=True)
        except MultipleObjectsReturned:
            raise Exception("The %s data layer has more than one shapefile marked as active.  That is bad.  There can be only one!" % self.name)
        except Shapefile.DoesNotExist:
            return None
            
    @property 
    def has_active_shapefile(self):
        """Returns true if there's an active shapefile associated with this data layer.  Returns False otherwise.  I just realize this is kind of useless
        because you can just call active shapfile and see if it's Null or has something.  Oh well."""
        try:
            self.shapefile_set.get(active=True)
            return True
        except MultipleObjectsReturned:
            raise Exception("The %s data layer has more than one shapefile marked as active.  That is bad.  There can be only one!" % self.name)
        except Shapefile.DoesNotExist:
            return False
    
class GeneralFile(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True)
    data_layer = models.ForeignKey(DataLayer)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='data_manager/general_files')
    
    def __unicode__(self):
        return self.name
    
class Shapefile(models.Model):
    active = models.BooleanField(default=False,help_text="The shapefile marked as active will be used to represent this data layer.")
    comment = models.TextField()
    data_layer = models.ForeignKey(DataLayer)
    truncated_comment = models.CharField(max_length=255, editable=False) 
    update_display_layer = models.BooleanField(help_text='Does this data update require an update of the assoicated display layer?')
    update_analysis_layer = models.BooleanField(help_text='Does this data update require an update of the assoicated analysis layer?')
    display_updated = models.BooleanField(help_text='Has the requested display update been made?')
    analysis_updated = models.BooleanField(help_text='Has the requested analysis update been made?')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    shapefile = models.FileField(upload_to='data_manager/shapefiles')
    field_description = models.TextField(null=True, blank=True, help_text='This is list of field names within the shapefile.  It is generated automatically when the shapefile is saved.  There is no need to edit this.')
    
    class Meta:
        ordering = ['-date_created']
    
    def save(self):
        # create a truncated comment to use as a title for the comment in the admin tool
        trunc_com = self.comment[0:25]
        if self.comment.__len__() > 25:
            trunc_com += '...'
        self.truncated_comment = trunc_com
        # make the file name what we want it to be before saving.
        self.shapefile = self.new_filename_and_path()
        super(Shapefile, self).save()
        self.data_layer.active_shapefile # this should throw an exception if there is more than one shapefile associated with this data layer marked as active.
        self.link_field_names()
        self.load_field_info()
        super(Shapefile, self).save()
#    def save(self, *args, **kwargs):
#        super(Shapefile, self).save(*args, **kwargs)
#        self.metadata = self.read_xml_metadata()
#        super(Shapefile, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s: %s' % (self.data_layer.name, self.shapefile.name)
    
    def new_filename_and_path(self):
        import time
        from django.template.defaultfilters import slugify
        time_str = time.strftime('%y%m%d', time.localtime() )
        old_path = self.shapefile.path
        
        dir = os.path.dirname(self.shapefile.name)
        newbasename = '%s_%s.zip' % (slugify(self.data_layer.name), time_str)
        self.shapefile.name = os.path.join(dir, newbasename)
        
        #dir = os.path.dirname(self.shapefile.path)
        #self.shapefile.path = os.path.join(dir, newbasename)
        # turns out that you can't do that but magically, you don't need to.  the magical
        # ponies inside django do it for you!
        
        if os.path.exists(old_path):
            from django.core.files.move import file_move_safe
            file_move_safe(old_path,self.shapefile.path)
        
        return self.shapefile
    
    def unzip_to_temp(self):
        # unzip to a temp directory and return the path to the .shp file
        valid, error = validate_zipped_shp(self.shapefile.path)
        if not valid:
            is_it_there = os.path.exists(self.shapefile.path)
            name = self.shapefile.name
            path = self.shapefile.path
            raise Exception(error)
        
        tmpdir = tempfile.gettempdir()
        zfile = zipfile.ZipFile(self.shapefile.path)
        for info in zfile.infolist():
            data = zfile.read(info.filename)
            if not info.filename[-1]==os.path.sep and not info.filename.startswith('__MACOSX'):
                shp_part = os.path.join(tmpdir, info.filename.split(os.path.sep)[-1])             
                fout = open(shp_part, "wb")
                fout.write(data)
                fout.close()
                if shp_part.endswith('.shp'):
                    shp_file = shp_part
        return shp_file
    
    def read_xml_metadata(self):
        shpfile = self.unzip_to_temp()
        xmlfile = shpfile + '.xml'
        if os.path.exists(xmlfile):
            f = open(xmlfile,'r')
            xml_text = f.readlines()
            f.close()
        else:
            xml_text = None
        return xml_text
    
    def field_info(self):
        fpath = self.unzip_to_temp()
        result = {}
        ds = DataSource(fpath)
        lyr = ds[0]
        field_names = lyr.fields
        for fname in field_names:
            field = lyr.get_fields(fname)
            distinct_values_count = dict.fromkeys(field).keys().__len__()
            result[fname] = distinct_values_count
        return result
    
    def field_info_str(self):
        dict = self.field_info()
        return_str = ''
        for key in dict.keys():
            return_str += '%s: %i distinct values, ' % (key, dict[key])
        return return_str
    
    def link_field_names(self):
        info_dict = self.field_info()
        for f in info_dict.keys():
            sf = ShapefileField(name=f,distinct_values=info_dict[f],shapefile=self)
            sf.save()
    
    def load_field_info(self):
        self.field_description = self.field_info_str()
     
    @transaction.commit_on_success  
    def load_to_model(self, feature_model, geometry_only=True, origin_field_name=None, target_field_name=None, verbose=False):
        shpfile = self.unzip_to_temp()
        file_name = os.path.basename(shpfile)
        # feature_name = self.name
        ds = DataSource(shpfile)
        #Data source objects can have different layers of geospatial features; however, 
        #shapefiles are only allowed to have one layer
        lyr = ds[0]
        
        # Treat feature models with multigeometry fields different that those without
        if has_multi_geometry(feature_model):
            for feat in lyr:
                fm = feature_model()
                load_single_record(feat.geom, fm, geometry_only, feat, origin_field_name, target_field_name)
                fm.save()
            
        else: # Target Feature Model has non-multi geometry (Polygon and so forth)
            for feat in lyr:
                if feat.geom.__class__.__name__.startswith('Multi'):
                    if verbose:
                        print '(',
                    for f in feat.geom: #get the individual geometries
                        fm = feature_model()
                        load_single_record(f, fm, geometry_only, feat, origin_field_name, target_field_name)
                        fm.save()
                        if verbose:
                            print '-',
                    if verbose:
                        print ')',
                else:
                    fm = feature_model()
                    load_single_record(feat.geom, fm, geometry_only, feat, origin_field_name, target_field_name)
                    fm.save()
                    if verbose:
                        print '.',

def has_multi_geometry(feature_model,field_name='geometry'):
    """Figure out if the model field is a multi or single geometry.  Note that I'm using the private method _field.
    I tried to find another way but the only other way I could think of involves the private method _meta."""
    g_type = feature_model.__dict__[field_name]._field.geom_type
    if g_type.lower().startswith('multi'):
        return True
    else:
        return False
        
def is_multi_geometry(geom):
    if geom.__class__.__name__.lower().startswith('multi'):
        return True
    else:
        return False

def load_single_record(geom,target_model_instance,geometry_only=True,origin_feature=None,origin_field_name=None,target_field_name=None):
    """docstring for load_single_record"""
    if not geometry_only:
        if not origin_field_name or not target_field_name:
            raise Exception('If you want to import attribute values, you must specify an Origin Field and a Target Field in the Load Setup.  Otherwise make sure the Geometry Only option is checked.')
        target_model_instance.__setattr__(target_field_name,origin_feature.__getitem__(origin_field_name).value)
    target_model_instance = load_single_geometry(geom,target_model_instance)
    return target_model_instance    
                    
def load_single_geometry(geom, target_model_instance):
    """Take a geometry and a model_instance.  Check the projections.  If different from the srid defined in settings, transform the geom to match.
    Check the validity of the geometry.  Clean if neccessary.  Return the model_instance with the geometry loaded.  For now, I'm assuming
    that the geometry field is named geometry.  Down the road we may want to generalize by detecting the name of the geometry field."""
    tmi = target_model_instance
    if not geom.srid == settings.GEOMETRY_DB_SRID:
        geom.transform(settings.GEOMETRY_DB_SRID)
        
    tmi_multi = has_multi_geometry(tmi.__class__)
    geom_multi = is_multi_geometry(geom)
    
    if tmi_multi == geom_multi:
        tmi.geometry = geom.geos
    elif tmi_multi:
        g_type = geom.geos.geom_type.upper()
        mgeom = geos.fromstr('MULTI%s EMPTY' % g_type)
        mgeom.append(geom.geos)
        tmi.geometry = mgeom
    elif geom_multi:
        pass # uh, actually this shouldn't ever happen because this is load_SINGLE_geometry, right?
    
    if not tmi.geometry.valid:
        tmi.geometry = clean_geometry(tmi.geometry)
    return tmi
    
class ShapefileField(models.Model):
    # We'll need information about the fields of multi feature shapefiles so we can turn them into single feature shapefiles
    name = models.CharField(max_length=255)
    distinct_values = models.IntegerField()
    type = models.CharField(max_length=255, null=True, blank=True)
    shapefile = models.ForeignKey(Shapefile)
    
    def __unicode__(self):
        return '%s: %i distinct values' % (self.name, self.distinct_values)

    
#class GeneralShapeComment(models.Model):
#    comment = models.TextField()
#    truncated_comment = models.CharField(max_length=255, editable=False) 
#    date_modified = models.DateTimeField(auto_now=True)
#    update_display_layer = models.BooleanField(help_text='Does this data update require an update of the assoicated display layer')
#    update_analysis_layer = models.BooleanField(help_text='Does this data update require an update of the assoicated analysis layer')
#    general_shapefile = models.ForeignKey(GeneralShapefile)
#    shapefile_name = models.CharField(max_length=255, null=True, editable=False)
#    
#    def __unicode__(self):
#        return self.comment
#
#    def save(self):
#        self.shapefile_name = self.general_shapefile.name
#        trunc_com = self.comment[0:25]
#        if self.comment.__len__() > 25:
#            trunc_com += '...'
#        self.truncated_comment = trunc_com
#        super(GeneralShapeComment, self).save(