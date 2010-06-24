from django.contrib.gis.db import models
from django.contrib.gis.gdal import *
from django.contrib.gis import geos
from django.contrib.gis.measure import *
from django.template.defaultfilters import slugify
from django.db import transaction
from lingcod.data_manager.models import DataLayer
from osgeo import ogr
#from django.contrib.gis.utils import LayerMapping
import os
import tempfile
import zipfile
import glob

# I think I may be able to get rid of this because I'm using django file fields now
#DATA_PATH = os.path.join(os.path.dirname(__file__), 'data') #'C:/pydevWorkspace/reporting_dev/lingcod/intersection/data/' #

# Maybe these should go somewhere else?  Maybe get stored in a model?
LINEAR_OUT_UNITS = 'miles'
AREAL_OUT_UNITS = 'sq miles'
POINT_OUT_UNITS = 'count'

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

def line_substring(linestring, startfraction, endfraction):
    """Return a linestring being a substring of the input one starting and ending at the given fractions of total 2d length. Second and third arguments are float8 values between 0 and 1. Calls ST_Line_Substring in PostGIS."""
    from django.db import connection
    cursor = connection.cursor()
    query = "select st_line_substring(st_geomfromewkt(\'%s\'),%f,%f)" % (linestring.ewkt, startfraction, endfraction)
    cursor.execute(query)
    row = cursor.fetchone()
    newline = geos.fromstr(row[0])
    return newline

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

def use_sort_as_key(results):
    """
    we want the results sorted by the sort value, not by the habitat name.
    """
    sort_results = {}
    for hab,sub_dict in results.iteritems():
        sub_dict.update( {'name':hab} )
        sort_results.update( {results[hab]['sort']:sub_dict} )
    
    return sort_results

def sum_results(results):
    """
    Take a list of dictionaries and sum them appropriately into a single dictionary.
    
    Example of expected format:
    results = \
    [{u'Beaches': {'feature_map_id': 1,                                                     \
                  'geo_collection': <GeometryCollection object at 0x1005bfa30>,             \
                  'org_scheme_id': 1,                                                       \
                  'percent_of_total': 6.9427176904575987,                                   \
                  'result': 27.874960403097003,                                             \
                  'sort': 1.0,                                                              \
                  'units': u'miles'},                                                       \
     u'Coastal Marsh': {'feature_map_id': 2,                                                \
                        'geo_collection': <GeometryCollection object at 0x1035e0b50>,       \
                        'org_scheme_id': 1,                                                 \
                        'percent_of_total': 0.0,                                            \
                        'result': 0.0,                                                      \
                        'sort': 2.0,                                                        \
                        'units': u'miles'}},                                                \
    {u'Beaches': {'feature_map_id': 1,                                                      \
                  'geo_collection': <GeometryCollection object at 0x1005bfa30>,             \
                  'org_scheme_id': 1,                                                       \
                  'percent_of_total': 6.9427176904575987,                                   \
                  'result': 27.874960403097003,                                             \
                  'sort': 1.0,                                                              \
                  'units': u'miles'},                                                       \
     u'Coastal Marsh': {'feature_map_id': 2,                                                \
                        'geo_collection': <GeometryCollection object at 0x1035e0b50>,       \
                        'org_scheme_id': 1,                                                 \
                        'percent_of_total': 0.0,                                            \
                        'result': 0.0,                                                      \
                        'sort': 2.0,                                                        \
                        'units': u'miles'}}]                                                \
                        
    from that we would expect this result:
    {u'Beaches': {'feature_map_id': 1,
                  'org_scheme_id': 1,
                  'percent_of_total': 13.885435380915197,
                  'result': 55.749920806194005,
                  'sort': 1.0,
                  'units': u'miles'},
     u'Coastal Marsh': {'feature_map_id': 2,
                        'org_scheme_id': 1,
                        'percent_of_total': 0.0,
                        'result': 0.0,
                        'sort': 2.0,
                        'units': u'miles'}}
    
    in other words:
    >>> sum_results( [{u'Beaches': {'feature_map_id': 1, 'org_scheme_id': 1, 'percent_of_total': 6.9427176904575987, 'result': 27.874960403097003, 'sort': 1.0, 'units': u'miles'}, u'Coastal Marsh': {'feature_map_id': 2, 'org_scheme_id': 1, 'percent_of_total': 0.0, 'result': 0.0, 'sort': 2.0, 'units': u'miles'}}, {u'Beaches': {'feature_map_id': 1, 'org_scheme_id': 1, 'percent_of_total': 6.9427176904575987, 'result': 27.874960403097003, 'sort': 1.0, 'units': u'miles'}, u'Coastal Marsh': {'feature_map_id': 2, 'org_scheme_id': 1, 'percent_of_total': 0.0, 'result': 0.0, 'sort': 2.0, 'units': u'miles'}}] )
    {u'Coastal Marsh': {'sort': 2.0, 'result': 0.0, 'units': u'miles', 'percent_of_total': 0.0, 'feature_map_id': 2, 'org_scheme_id': 1}, u'Beaches': {'sort': 1.0, 'result': 55.749920806194005, 'units': u'miles', 'percent_of_total': 13.885435380915197, 'feature_map_id': 1, 'org_scheme_id': 1}}
    
    """
    # These keys will be summed.  Any other key will be set to the first value encountered.
    sum_keys = ['result','percent_of_total','geo_collection']
    # The values for these keys should be equal for items we sum
    must_be_equal = ['units']
    # If the values for these keys are not equal, let's make the value null
    null_if_not_equal = ['feature_map_id','org_scheme_id']
    # I don't know how to sum kml in any convenient way
    cant_handle = ['kml']
    
    # make dictionary to hold the summed results and a list of all the unique habitat keys
    summed = {}
    for result in results:
        for r_key in result.keys():
            summed[r_key] = {}
    hab_key_list = summed.keys()
    
    for hab in hab_key_list:
        for result in results:
            if hab not in result.keys():
                continue # This may happen when summing open coast and estuary results.  A particular habitat may not show up every time.
            sub_dict = result[hab]
            for k,v in sub_dict.iteritems():
                if k in cant_handle:
                    # we don't know how to sum some things
                    pass
                elif k not in summed[hab].keys():
                    # this is the first time we've encountered this key, so just add the key/value pair
                    summed[hab].update({k:v})
                elif k in sum_keys:
                    # these are the things we need to actually sum so add it to what we've got so far
                    summed[hab][k] += v
                elif k in null_if_not_equal and summed[hab][k]<>v:
                    summed[hab][k] = None
                elif k in must_be_equal:
                    # we've gotten this key in already and it must be equal across all sub_dicts that we're summing
                    try: assert(summed[hab][k]==v)
                    except: raise Exception('sum_results has been passed an incorrect results matrix.')
    return summed

    
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
        '''unzip to a temp directory and return the path to the .shp file'''
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
    
    @transaction.commit_on_success
    def load_geometry_to_model(self, feature_model, verbose=False):
        shpfile = self.unzip_to_temp()
        file_name = os.path.basename(shpfile)
        feature_name = self.name
        ds = DataSource(shpfile)
        #Data source objects can have different layers of geospatial features; however, 
        #shapefiles are only allowed to have one layer
        lyr = ds[0] 

        for feat in lyr:
            if feat.geom.__class__.__name__.startswith('Multi'):
                if verbose:
                    print '(',
                for f in feat.geom: #get the individual geometries
                    fm = feature_model()
                    fm.geometry=f.geos
                    if not fm.geometry.valid:
                        fm.geometry = clean_geometry(fm.geometry)
                    fm.save()
                    if verbose:
                        print '-',
                if verbose:
                    print ')',
            else:
                fm = feature_model()
                fm.geometry=f.geos
                if not fm.geometry.valid:
                    fm.geometry = clean_geometry(fm.geometry)
                fm.save()
                if verbose:
                    print '.',
        
class MultiFeatureShapefile(Shapefile):
    """These shape files may contain geometries that we want to turn into multiple intersection features.
    An example would be the ESI shoreline layer.  It contains a line that is classified into many different
    habitat types."""
    shapefile = models.FileField(upload_to='intersection/shapefiles/multifeature')
    
    def __unicode__(self):
        return self.name
    
    def save(self):
        super(MultiFeatureShapefile, self).save()
        self.link_field_names()
    
    def link_field_names(self):
        self.shapefilefield_set.all().delete()
        info_dict = self.field_info()
        for f,dv in info_dict.iteritems():
            sf = ShapefileField(name=f,distinct_values=dv,shapefile=self)
            sf.save()
    
    @transaction.commit_on_success
    def process_proxy_line(self, field_name='Aj_pct_rck', hard_name='Hard Proxy', soft_name='Soft Proxy'):
        """This function is rather specific to the North Coast MLPA but could concievably be useful elsewhere.  This method
        takes a linear shapefile and, based on the numeric field specified under field_name, splits it into two linear shapefiles.
        The new shapefiles have segements that are substrings of the original line features.  The length of the substrings is 
        determined by the values in the field_name field.  Yeah, that sounds kind of confusing but that is the best explaination I 
        can come up with.  Sorry."""
        driver = ogr.GetDriverByName('ESRI Shapefile')
        shpfile = self.unzip_to_temp()
        tempdir = tempfile.gettempdir()
        
        
        #determine what geometry type we're dealing with
        # feat = lyr_in.GetFeature(0)
        # geom = feat.GetGeometryRef()
        # gname = geom.GetGeometryName()
        # 
        # Create two new shapefiles.  One for hard, one for soft
        files = {}
        file_names = [hard_name,soft_name]
        for i,file_name in enumerate(file_names):
            # create a new data source and layer
            fn = slugify(file_name) + '.shp'
            fn = str(os.path.abspath(os.path.join(tempdir, fn)))
        
            if os.path.exists(fn):
              driver.DeleteDataSource(fn)
            ds_out = driver.CreateDataSource(fn)
            if ds_out is None:
              raise 'Could not create file: %s' % fn
            files.update({file_name: ds_out})
        
        zipped_files = {}
        for name,ds_out in files.iteritems():
            #open input data source
            ds_in = driver.Open(shpfile,0)
            if ds_in is None:
                raise 'Could not open input shapefile'
            lyr_in = ds_in.GetLayer()
            if name.lower().find('hard') != -1:
                sub_type = 'hard'
            else:
                sub_type = 'soft'
            outLayer = ds_out.CreateLayer(name,geom_type=ogr.wkbLineString)
            # get the FieldDefn's for the id field in the input shapefile
            feature = lyr_in.GetFeature(0)
            idFieldDefn = feature.GetFieldDefnRef('id')
            # create new id field in the output shapefile
            outLayer.CreateField(idFieldDefn)
            # get the FeatureDefn for the output layer
            featureDefn = outLayer.GetLayerDefn()

            # loop through the input features
            inFeature = lyr_in.GetNextFeature()
            while inFeature:
                percent_hard = inFeature.GetField(field_name)
                #create a new feature
                outFeature = ogr.Feature(featureDefn)
                
                # set the geometry
                oldGeom = geos.fromstr(inFeature.GetGeometryRef().ExportToWkt())
                # print oldGeom.__class__.__name__
                # print oldGeom.ewkt
                if sub_type == 'hard':
                    newGeom = line_substring(oldGeom,0,percent_hard)
                else:
                    newGeom = line_substring(oldGeom,percent_hard,1)
                if newGeom.num_points > 1:
                    the_id = inFeature.GetFID()
                    outFeature.SetFID(the_id)
                    outFeature.SetGeometry(ogr.CreateGeometryFromWkt(newGeom.ewkt))
                    outLayer.CreateFeature(outFeature)
                outFeature.Destroy()
                inFeature.Destroy()
                inFeature = lyr_in.GetNextFeature()
        
            # get the projection from the input shapefile and write a .prj file for the output
            spatial_ref = lyr_in.GetSpatialRef()
            fn_prj = slugify(name) + '.prj'
            fn_prj = str(os.path.abspath(os.path.join(tempdir, fn_prj)))
            file = open(fn_prj,'w')
            spatial_ref.MorphToESRI()
            file.write(spatial_ref.ExportToWkt())
            file.close()
            zip_file_name = ds_out.GetName()
            ds_in.Destroy()
            ds_out.Destroy()
            new_name, zip_o_rama = zip_from_shp(zip_file_name)
            zipped_files.update({name:zip_o_rama})
            
            
        for file_name, zipped_file in zipped_files.iteritems():
            sfsf, created = SingleFeatureShapefile.objects.get_or_create(name=file_name)
            
            if not created and sfsf.shapefile: #get rid of the old shapefile so it's not hangin around
                print 'I am deleting'
                sfsf.shapefile.delete()
            sfsf.shapefile = zipped_file
            sfsf.save()
        
        
    def split_to_single_feature_shapefiles(self, field_name):
        file_path = self.unzip_to_temp()
        ds = DataSource(file_path)
        lyr = ds[0]
        if field_name not in lyr.fields:
            raise Exception('Specified field (%s) not found in %s' % (field_name,self.name) )
        field = lyr.get_fields(field_name)
        distinct_values = dict.fromkeys(field).keys()
        
        for dv in distinct_values:
            new_name, file = self.single_shapefile_from_field_value(field_name, dv)
            sfsf, created = SingleFeatureShapefile.objects.get_or_create(name=dv)
            if not created: #get rid of the old shapefile so it's not hangin around
                sfsf.shapefile.delete()
            sfsf.shapefile = file
#            if os.path.exists(sfsf.shapefile.path):
#                os.remove(sfsf.shapefile.path)
            sfsf.parent_shapefile = self
            sfsf.save()
            
    def single_shapefile_from_field_value(self, field_name, field_value):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        shpfile = self.unzip_to_temp()
        tempdir = tempfile.gettempdir()
        #open input data source
        ds_in = driver.Open(shpfile,0)
        if ds_in is None:
            raise 'Could not open input shapefile'
        lyr_in = ds_in.GetLayer()
        
        #determine what geometry type we're dealing with
        feat = lyr_in.GetFeature(0)
        geom = feat.GetGeometryRef()
        gname = geom.GetGeometryName()
            
        # create a new data source and layer
        fn = slugify(field_value) + '.shp'
        fn = str(os.path.abspath(os.path.join(tempdir, fn)))
        
        if os.path.exists(fn):
          driver.DeleteDataSource(fn)
        ds_out = driver.CreateDataSource(fn)
        if ds_out is None:
          raise 'Could not create file: %s' % fn
        
        if gname.lower().endswith('polygon'):
            geometry_type = ogr.wkbMultiPolygon
        elif gname.lower().endswith('linestring'):
            geometry_type = ogr.wkbMultiLineString
        elif gname.lower().endswith('point'):
            geometry_type = ogr.wkbMultiPoint
        else:
            raise 'Unregonized geometry type'
        
        lyr_out = ds_out.CreateLayer(str(slugify(field_value)), geom_type=geometry_type)
        
        # get the FieldDefn's for the fields in the input shapefile
        transferFieldDefn = feat.GetFieldDefnRef(field_name)
        
        #create new fields in the output shapefile
        lyr_out.CreateField(transferFieldDefn)
        
        #get the FeatureDefn for the output
        feat_defn = lyr_out.GetLayerDefn()
        
        # loop through the input features
        feat_in = lyr_in.GetNextFeature()
        while feat_in:
            field = feat_in.GetField(field_name)
            
            if field==field_value:
                # create new feature
                feat_out = ogr.Feature(feat_defn)
                #set the geometry
                geom_in = feat_in.GetGeometryRef()
                feat_out.SetGeometry(geom_in)
                #set the attributes
                id = feat_in.GetFID()
                feat_out.SetFID(id)
                feat_out.SetField(field_name,field)
                # add the feature to the ouput layer
                lyr_out.CreateFeature(feat_out)
                # destroy the output feature
                feat_out.Destroy()
            
            #destroy the input feature and get a new one
            feat_in.Destroy()
            feat_in = lyr_in.GetNextFeature()
        
        # get the projection from the input shapefile and write a .prj file for the output
        spatial_ref = lyr_in.GetSpatialRef()
        fn_prj = slugify(field_value) + '.prj'
        fn_prj = str(os.path.abspath(os.path.join(tempdir, fn_prj)))
        file = open(fn_prj,'w')
        spatial_ref.MorphToESRI()
        file.write(spatial_ref.ExportToWkt())
        file.close()
        
        ds_in.Destroy()
        ds_out.Destroy()
        
        return zip_from_shp(fn)
    
class SingleFeatureShapefile(Shapefile):
    # These shape files contain geometries that represent only one intersection feature.
    shapefile = models.FileField(upload_to='intersection/shapefiles/singlefeature')
    parent_shapefile = models.ForeignKey(MultiFeatureShapefile, null=True, blank=True)
    clip_to_study_region = models.BooleanField(default=True,help_text="Clip to the active study region to ensure accuracy of study region totals.")
    
    def __unicode__(self):
        return self.name
    
    @transaction.commit_on_success
    def load_to_features(self, verbose=False):
        """
        This method loads individual features (with polygon, linestring, or point geometry) into
        the appropriate model and loads relevant data 
        """
        shpfile = self.unzip_to_temp()
        file_name = os.path.basename(shpfile)
        feature_name = self.name
        ds = DataSource(shpfile)
        #Data source objects can have different layers of geospatial features; however, 
        #shapefiles are only allowed to have one layer
        lyr = ds[0] 
        
        # make or update the intersection feature in the IntersectionFeature model
        try:
            intersection_feature = IntersectionFeature.objects.get(name=feature_name)
            created = False
        except IntersectionFeature.DoesNotExist:
            intersection_feature = IntersectionFeature(name=feature_name)
            created = True

        intersection_feature.native_units = lyr.srs.units[1]
        intersection_feature.save() # we need the pk value
        if created:
            intersection_feature = IntersectionFeature.objects.get(name=feature_name)
        
        if lyr.geom_type=='LineString':
            feature_model = LinearFeature
            out_units = LINEAR_OUT_UNITS
            #mgeom = geos.fromstr('MULTILINESTRING EMPTY')
        elif lyr.geom_type=='Polygon':
            feature_model = ArealFeature
            out_units = AREAL_OUT_UNITS
            intersection_feature.native_units = 'Sq ' + intersection_feature.native_units
            #mgeom = geos.fromstr('MULTIPOLYGON EMPTY')
        elif lyr.geom_type=='Point':
            feature_model = PointFeature
            out_units = POINT_OUT_UNITS
            #mgeom = geos.fromstr('MULTILIPOINT EMPTY')
        else:
            raise 'Unrecognized type for load_features.'
        
        # get rid of old stuff if it's there
        feature_model.objects.filter(feature_type=intersection_feature).delete()
        
        if verbose:
            print 'Loading %s from %s' % (feature_name,file_name)
        
        area = 0.0
        length = 0.0
        count = 0
        
        # gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        # for feat in lyr:
        #     gc.append(feat.geom.geos)
        #     
        # if self.clip_to_study_region:
        #     from lingcod.studyregion.models import StudyRegion
        #     sr = StudyRegion.objects.current()
        #     new_gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        #     int_result = gc.intersection(sr.geometry)
        #     new_gc.append(int_result)
        #     gc = new_gc
            
        for feat in lyr:
            if feat.geom.__class__.__name__.startswith('Multi'):
                if verbose:
                    print '(',
                for f in feat.geom: #get the individual geometries
                    fm = feature_model(name=feature_name,feature_type=intersection_feature)
                    fm.geometry = f.geos
                    if not fm.geometry.valid:
                        fm.geometry = clean_geometry(fm.geometry)
                    #mgeom.append(fm.geometry)
                    if out_units==AREAL_OUT_UNITS:
                        area += fm.geometry.area
                    elif out_units==LINEAR_OUT_UNITS:
                        length += fm.geometry.length
                    else:
                        count += 1
                    fm.save()
                    if verbose:
                        print '-',
                if verbose:
                    print ')',
            else:
                fm = feature_model(name=feature_name,feature_type=intersection_feature)
                fm.geometry = feat.geom.geos
                if not fm.geometry.valid:
                    fm.geometry = clean_geometry(fm.geometry)
                #mgeom.append(fm.geometry)
                if out_units==AREAL_OUT_UNITS:
                    area += fm.geometry.area
                elif out_units==LINEAR_OUT_UNITS:
                    length += fm.geometry.length
                else:
                    count += 1
                fm.save()
                if verbose:
                    print '.',
        
        
        if out_units==AREAL_OUT_UNITS:
            intersection_feature.study_region_total = A(sq_m=area).sq_mi
        elif out_units==LINEAR_OUT_UNITS:
            intersection_feature.study_region_total = D(m=length).mi
        else:
            intersection_feature.study_region_total = count
        intersection_feature.output_units = out_units
        intersection_feature.shapefile = self
        intersection_feature.multi_shapefile = self.parent_shapefile
        intersection_feature.feature_model = feature_model.__name__
        intersection_feature.save()
        
        # This is super slow.  I'm giving up on it for now and just declaring that hab data needs to be clipped
        # to the study region before it's loaded into the tool.  I'll look into making this work later.
        # if self.clip_to_study_region:
        #     intersection_feature.study_region_total = intersection_feature.calculate_study_region_total()
        #     intersection_feature.save()
    
class ShapefileField(models.Model):
    # We'll need information about the fields of multi feature shapefiles so we can turn them into single feature shapefiles
    name = models.CharField(max_length=255)
    distinct_values = models.IntegerField()
    type = models.CharField(max_length=255, null=True, blank=True)
    shapefile = models.ForeignKey(MultiFeatureShapefile)
    
    def __unicode__(self):
        return self.name

class TestPolygon(models.Model):
    geometry = models.PolygonField(srid=3310)
    objects = models.GeoManager()

class IntersectionFeature(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    study_region_total = models.FloatField(null=True, blank=True, help_text="This is the quantity of this habitat type available within the study region. This value will be generated programmatically and should not be manually altered")
    native_units = models.CharField(max_length=255,null=True, blank=True, help_text="Units native to this layer's projection.")
    output_units = models.CharField(max_length=255,null=True, blank=True, help_text="Unit label to be displayed after results from this table.")
    shapefile = models.ForeignKey(SingleFeatureShapefile, null=True)
    multi_shapefile = models.ForeignKey(MultiFeatureShapefile,null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    TYPE_CHOICES = (
                    ('ArealFeature', 'Areal'),
                    ('LinearFeature', 'Linear'),
                    ('PointFeature', 'Point'),
                   )
    feature_model = models.CharField(null=True, blank=True, max_length=20, choices=TYPE_CHOICES)
    objects = models.GeoManager()
    
    class Meta:
        ordering = ('name',)
   
    def __unicode__(self):
        return self.name
    
    def save(self):
        self.expire_cached_results()
        super(IntersectionFeature,self).save()
    
    @property
    def model_with_my_geometries(self):
        appname = os.path.dirname(__file__).split(os.path.sep).pop()
        model_with_geom = models.get_model(appname,self.feature_model)
        return model_with_geom
    
    @property
    def geometry(self):
        # Returns a multigeometry of the appropriate type containing all geometries for this intersection feature.
        # Don't bother to call this on the large polygon features.  It takes far too long.
        individual_features = self.model_with_my_geometries.objects.filter(feature_type=self)
        
        if self.model_with_my_geometries==ArealFeature:
            mgeom = geos.fromstr('MULTIPOLYGON EMPTY')
        elif self.model_with_my_geometries==LinearFeature:
            mgeom = geos.fromstr('MULTILINESTRING EMPTY')
        elif self.model_with_my_geometries==PointFeature:
            mgeom = geos.fromstr('MULTIPOINT EMPTY')
        else:
            raise 'Could not figure out what geometry type to use.'
        
        if individual_features:
            for feature in individual_features:
                mgeom.append(feature.geometry)
        return mgeom
    
    @property
    def geometries_set(self):
        # Returns a query set of all the ArealFeature, LinearFeature, or PointFeature objects related to this intersection feature.
        return self.model_with_my_geometries.objects.filter(feature_type=self)
    
    def calculate_study_region_total_old(self):
        from lingcod.studyregion.models import StudyRegion
        sr = StudyRegion.objects.current()
        result = self.geometry.intersection(sr.geometry)
        if self.feature_model == 'ArealFeature':
            return A(sq_m=result.area).sq_mi
        elif self.feature_model == 'LinearFeature':
            return D(m=result.length).mi
        else:
            return result.count
    
    def calculate_study_region_total(self):
        from lingcod.studyregion.models import StudyRegion
        sr = StudyRegion.objects.current()
        #result = self.geometry.intersection(sr.geometry)
        features_within = self.geometries_set.filter(geometry__within=sr.geometry)
        if self.feature_model == 'ArealFeature':
            area_within = sum( [ a.geometry.area for a in features_within ] )
            mgeom = geos.fromstr('MULTIPOLYGON EMPTY')
            [ mgeom.append(a.geometry) for a in self.geometries_set.filter(geometry__overlaps=sr.geometry) ]
            area_overlap = mgeom.intersection(sr.geometry).area
            area_total = area_overlap + area_within
            return A(sq_m=area_total).sq_mi
        elif self.feature_model == 'LinearFeature':
            length_within = sum( [ a.geometry.length for a in features_within ] )
            mgeom = geos.fromstr('MULTILINESTRING EMPTY')
            [ mgeom.append(a.geometry) for a in self.geometries_set.filter(geometry__crosses=sr.geometry) ]
            length_overlap = mgeom.intersection(sr.geometry).length
            length_total = length_overlap + length_within
            return D(m=length_total).mi
        else:
            return features_within.count
    def expire_cached_results(self):
        self.resultcache_set.all().delete()

class OrganizationScheme(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True,help_text="Description of this organization scheme and what it is used for.")
    
    def __unicode__(self):
        return self.name
        
    def copy(self):
        new_name = '%s_copy' % self.name
        new = OrganizationScheme(name=new_name)
        new.save()
        for fm in self.featuremapping_set.all():
            fm.copy_to_org_scheme(new)
        return new
        
    @property
    def info(self):
        subdict = {}
        subdict['name'] = self.name
        subdict['pk'] = self.pk
        subdict['num_features'] = self.featuremapping_set.all().count()
        subdict['feature_info'] = {}
        for f in self.featuremapping_set.all().order_by('sort'):
            subdict['feature_info'].update( { f.sort : {'name':f.name, 'pk':f.pk, 'sort':f.sort, 'study_region_total':f.study_region_total, 'units': f.units} } )
        return subdict
    
    def my_validate(self):
        for fm in self.featuremapping_set.all():
            if not fm.my_validate(quiet=True):
                return False
        return True
    
    @transaction.commit_on_success
    def transformed_results(self, geom_or_collection, with_geometries=False, with_kml=False):
        if geom_or_collection.empty: # If we've been given empty
            geom_or_collection = geos.fromstr('SRID=3310;POLYGON ((386457.8191845841938630 87468.5562629736959934, 386725.8874563252902590 87481.1556781106628478, 386612.4574658756027929 87036.4770780648104846, 386457.8191845841938630 87468.5562629736959934))')
        if geom_or_collection.geom_type.lower().endswith('polygon'):
            return self.transformed_results_single_geom(geom_or_collection, with_geometries=with_geometries, with_kml=with_kml)
        elif geom_or_collection.geom_type.lower().endswith('collection'):
            #do stuff for a collection
            list_of_dicts = []
            for geom in geom_or_collection:
                geom_results = self.transformed_results_single_geom(geom, with_geometries=with_geometries, with_kml=with_kml)
                list_of_dicts.append(geom_results)
            summed_results = sum_results(list_of_dicts)
            return summed_results
        else:
            raise Exception('transformed results only available for Polygons and geometry collections.  something else was submitted.')
    
    def transformed_results_single_geom(self, geom, with_geometries=False, with_kml=False):
        new_results = {}
        for fm in self.featuremapping_set.all():
            result_dict = fm.transformed_results_single_geom(geom,with_geometries=with_geometries,with_kml=with_kml)
            if not True in [ k in result_dict.keys() for k in new_results.keys() ]:
                for key in result_dict.keys():
                    result_dict[key].update({'org_scheme_id': self.pk})
                new_results.update(result_dict)
            else:
                raise Exception('You are getting the same key more than once in your dictionary.  You need to sum instead of update.')
        return new_results
            
    
class FeatureMapping(models.Model):
    organization_scheme = models.ForeignKey(OrganizationScheme)
    feature = models.ManyToManyField(IntersectionFeature)
    name = models.CharField(max_length=255)
    sort = models.FloatField()
    description = models.TextField(null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('sort','name')
    
    def __unicode__(self):
        return self.name
        
    def copy_to_org_scheme(self, org_scheme):
        new = FeatureMapping(organization_scheme=org_scheme)
        new.name = self.name
        new.sort = self.sort
        new.description = self.description
        new.save()
        for f in self.feature.all():
            new.feature.add(f)
        new.save()
    
    def transformed_results(self, geom_or_collection, with_geometries=False, with_kml=False):
        if geom_or_collection.geom_type.lower().endswith('polygon'):
            return self.transformed_results_single_geom(geom_or_collection, with_geometries=with_geometries, with_kml=with_kml)
        elif geom_or_collection.geom_type.lower().endswith('collection'):
            #do stuff for a collection
            list_of_dicts = []
            for geom in geom_or_collection:
                geom_results = self.transformed_results_single_geom(geom, with_geometries=with_geometries, with_kml=with_kml)
                list_of_dicts.append(geom_results)
            summed_results = sum_results(list_of_dicts)
            return summed_results
        else:
            raise Exception('transformed results only available for Polygons and geometry collections.  something else was submitted.')
    
    def transformed_results_single_geom(self, geom, with_geometries=False, with_kml=False):
        return_dict = {}
        return_dict[self.name] = {}
        feature_pks = [f.pk for f in self.feature.all()]
        results = intersect_the_features(geom, feature_list=feature_pks, with_geometries=with_geometries or with_kml, with_kml=with_kml)
        intersection_total = 0.0
        sr_total = 0.0
        if with_geometries or with_kml:
            f_gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        for pk in feature_pks:
            for hab, had_dict in results.iteritems():
                if had_dict['hab_id']==pk:
                    intersection_total += had_dict['result']
                    #percent_sr_total += result['percent_of_total'] #wrong, can't add these percentages up have to determine total/total available
                    #sr_total += IntersectionFeature.objects.get(pk=pk).study_region_total
                    if with_geometries or with_kml:
                        f_gc = f_gc + had_dict['geo_collection']
        return_dict[self.name]['result'] = intersection_total
        blah = self.feature.all()
        return_dict[self.name]['units'] = self.feature.all()[0].output_units
        return_dict[self.name]['percent_of_total'] = (intersection_total / self.study_region_total) * 100
        return_dict[self.name]['sort'] = self.sort
        return_dict[self.name]['feature_map_id'] = self.pk
        if with_geometries:
            return_dict[self.name]['geo_collection'] = f_gc
        if with_kml:
            return_dict[self.name]['kml'] = f_gc.kml
            
        return return_dict
    
    @property
    def study_region_total(self):
        total = 0.0
        for feature in self.feature.all().only('study_region_total'):
            total += feature.study_region_total
        return total
    
    def calculate_study_region_total(self,sr_geom):
        if self.type == 'linear':
            return D(m=self.geometry_collection_within(sr_geom).length).mi
        elif self.type == 'areal':
            return A(sq_m=self.geometry_collection_within(sr_geom).area).sq_mi
        else:
            return self.geometry_collection_within(sr_geom).num_points
        
    @property
    def units(self):
        if self.my_validate():
            return self.feature.all()[0].output_units
        
    @property
    def type(self):
        if self.my_validate():
            return self.feature.all()[0].feature_model.lower().replace('feature','')
            
    @property
    def geometry_collection(self):
        gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        for feature in self.feature.all():
            gc.append(feature.geometry)
        return gc
    
    ##transaction.commit_on_success    
    def geometry_collection_within(self,geom):
        return self.geometry_collection.intersection(geom)
    
    def my_validate(self, quiet=False):
        if not self.pk:
            return True # I'm gonna punt if there's no pk yet
        elif self.validate_feature_count(quiet) and self.validate_type(quiet) and self.validate_units(quiet):
            return True
        else:
            return False
    
    def validate_feature_count(self, quiet=False):
        if self.feature.all().count() < 1:
            if quiet:
                return False
            else:
                error = '%s in %s organization scheme has no features.' % (self.name, self.organization_scheme.name)
                raise Exception(error)
        else:
            return True
    
    def validate_units(self, quiet=False):
        # Make sure that if there are multiple features to be combined that they all have the 
        # same units.
        units = self.feature.all()[0].output_units
        if False in [units==f.output_units for f in self.feature.all()]:
            if quiet:
                return False
            else:
                error = '%s in %s organization scheme combines features with different units.' % (self.name, self.organization_scheme.name)
                raise Exception(error)
        else:
            return True
    
    def validate_type(self, quiet=False):
        # Make sure that if there are multiple features to be combined that they all have the 
        # same type.
        type = self.feature.all()[0].feature_model
        if False in [type==f.feature_model for f in self.feature.all()]:
            if quiet:
                return False
            else:
                error = '%s in %s organization scheme combines different types of features.' % (self.name, self.organization_scheme.name)
                raise Exception(error)
        else:
            return True
    
class CommonFeatureInfo(models.Model):
    name = models.CharField(max_length=255)
    feature_type = models.ForeignKey(IntersectionFeature)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True) # updating also handled by a trigger defined in lingcod/intersection/sql. manage.py creates the trigger.  This will let us modify features in qgis if we need to and still know when features were updated.
    objects = models.GeoManager()
    
    class Meta:
        abstract = True
        
class ArealFeature(CommonFeatureInfo):
    geometry = models.PolygonField(srid=3310)
    objects = models.GeoManager()
    
    def intersection(self,geom):
        return self.geometry.intersection(geom)
    
class LinearFeature(CommonFeatureInfo):
    geometry = models.LineStringField(srid=3310)
    objects = models.GeoManager()
    
    def intersection(self,geom):
        return self.geometry.intersection(geom)
    
class PointFeature(CommonFeatureInfo):
    geometry = models.PointField(srid=3310)
    objects = models.GeoManager()
    
class ResultCache(models.Model):
    wkt_hash = models.CharField(max_length=255)
    intersection_feature = models.ForeignKey(IntersectionFeature)
    result = models.FloatField()
    units = models.CharField(max_length=255)
    percent_of_total = models.FloatField()
    date_modified = models.DateTimeField(auto_now=True)
    geometry = models.GeometryCollectionField()
    objects = models.GeoManager()
    
    class Meta:
        unique_together = ('wkt_hash','intersection_feature',)
    
def delete_cached_results(geom):
    results = ResultCache.objects.filter(wkt_hash=str(geom.wkt.__hash__()))
    results.delete()
    
def intersect_the_features(geom, feature_list=None, with_geometries=False, with_kml=False):
    # if no feature list is specified, get all the features
    if not feature_list:
        feature_list = [i.pk for i in IntersectionFeature.objects.all()]
    result_dict = {}
    for f_pk in feature_list:
        f_gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        int_feature = IntersectionFeature.objects.get(pk=f_pk)
        result_dict[int_feature.name] = {}
        dict = {}
        result_dict[int_feature.name]['hab_id'] = f_pk
        result_dict[int_feature.name]['units'] = int_feature.output_units
        try: # get results from cache if they're there
            rc = ResultCache.objects.get( wkt_hash=str(geom.wkt.__hash__()), intersection_feature=int_feature )
            result_dict[int_feature.name]['result'] = rc.result
            result_dict[int_feature.name]['percent_of_total'] = rc.percent_of_total
            if with_geometries:
                result_dict[int_feature.name]['geo_collection'] = rc.geometry
            if with_kml:
                result_dict[int_feature.name]['kml'] = rc.geometry.kml 
                
        except ResultCache.DoesNotExist: # Calculate if cached results doen't exist
            if not int_feature.feature_model=='PointFeature':
                geom_set = int_feature.geometries_set.filter(geometry__intersects=geom)
                for g in geom_set:
                    from django.contrib.gis.geos.error import GEOSException
                    try:
                        intersect_geom = geom.intersection(g.geometry)
                    except GEOSException:
                        print 'Intersection threw a GEOSException that we are going to ignore.  If you see this every once in a while, no problem.  If you see it a lot, Jared is fired'
                        continue
                    #geom_area = geom.area
                    try:
                        f_gc.append(intersect_geom)
                    except:
                        # if this fails, it's probably because the intersection returned a multigeometry
                        # so we'll assume that's what happened and stick all the geometries in there.
                        # This is a bit weird because we might be putting in a line with our polys or vice versa
                        # but it shouldn't really matter when we measure the length or area.
                        for wtf in intersect_geom:
                            f_gc.append(wtf)
            else:
                geom_set = int_feature.geometries_set.filter(geometry__within=geom)
                for p in geom_set:
                    f_gc.append(p.geometry)
                
            if with_geometries:
                result_dict[int_feature.name]['geo_collection'] = f_gc
            if with_kml:
                result_dict[int_feature.name]['kml'] = f_gc.kml    
                
            if int_feature.feature_model=='ArealFeature':
                result_dict[int_feature.name]['result'] = A(sq_m=f_gc.area).sq_mi
            elif int_feature.feature_model=='LinearFeature':
                result_dict[int_feature.name]['result'] = D(m=f_gc.length).mi
            elif int_feature.feature_model=='PointFeature':
                result_dict[int_feature.name]['result'] = f_gc.num_geom
                
            result_dict[int_feature.name]['percent_of_total'] = (result_dict[int_feature.name]['result'] / int_feature.study_region_total) * 100
            
            # Cache the results we've calculated
            rc = ResultCache( wkt_hash=geom.wkt.__hash__(), intersection_feature=int_feature )
            rc.result = result_dict[int_feature.name]['result']
            rc.units = int_feature.output_units
            rc.percent_of_total = result_dict[int_feature.name]['percent_of_total']
            rc.geometry = f_gc
            rc.save()
        
    return result_dict
    
