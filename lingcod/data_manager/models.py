from django.contrib.gis.db import models
from django.contrib.gis.gdal import *
from django.contrib.gis import geos
from django.contrib.gis.measure import *
from django.template.defaultfilters import slugify
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
    if not zipfile.is_zipfile(file_path):
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
    # takes a polygon or a multipolygon and returns only the largest polygon
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
    
class Shapefile(models.Model):
    #shapefile = models.FileField(upload_to='intersection/shapefiles')
    name = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField(null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
#    def save(self, *args, **kwargs):
#        super(Shapefile, self).save(*args, **kwargs)
#        self.metadata = self.read_xml_metadata()
#        super(Shapefile, self).save(*args, **kwargs)
        
    def unzip_to_temp(self):
        # unzip to a temp directory and return the path to the .shp file
        valid, error = validate_zipped_shp(self.shapefile.path)
        if not valid:
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
        
class GeneralShapefile(Shapefile):
    shapefile = models.FileField(upload_to='data_manager/shapefiles/general')
    
    def __unicode__(self):
        return self.name
    
    def save(self):
        super(GeneralShapefile, self).save()
        self.link_field_names()
    
    def link_field_names(self):
        info_dict = self.field_info()
        for f in info_dict.keys():
            sf = ShapefileField(name=f,distinct_values=info_dict[f],shapefile=self)
            sf.save()
            
    
class ShapefileField(models.Model):
    # We'll need information about the fields of multi feature shapefiles so we can turn them into single feature shapefiles
    name = models.CharField(max_length=255)
    distinct_values = models.IntegerField()
    type = models.CharField(max_length=255, null=True, blank=True)
    shapefile = models.ForeignKey(GeneralShapefile)
    
    def __unicode__(self):
        return '%s: %i distinct values' % (self.name, self.distinct_values)


