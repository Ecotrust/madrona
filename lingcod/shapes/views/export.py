# -*- coding: utf-8 -*-

import os
import zipfile
import tempfile
import datetime
import cStringIO
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.gis.gdal.libgdal import lgdal as ogr
from django.contrib.gis.gdal import Driver, OGRGeometry, OGRGeomType, SpatialReference, check_err, CoordTransform

class ShpResponder(object):
    def __init__(self, queryset, readme=None, geo_field=None, proj_transform=None, mimetype='application/zip',file_name='shp_download'):
        """
        """
        self.queryset = queryset
        self.readme = readme
        self.geo_field = geo_field
        self.proj_transform = proj_transform
        self.mimetype = mimetype
        self.file_name = smart_str(file_name)

    def __call__(self, *args, **kwargs):
        """
        """
        fields = self.queryset.model._meta.fields
        geo_fields = [f for f in fields if isinstance(f, GeometryField)]
        geo_fields_names = ', '.join([f.name for f in geo_fields])
        attributes = [f for f in fields if not isinstance(f, GeometryField)]
        
        if len(geo_fields) > 1:
            if not self.geo_field:
                raise ValueError("More than one geodjango geometry field found, please specify which to use by name using the 'geo_field' keyword. Available fields are: '%s'" % geo_fields_names)
            else:
                geo_field_by_name = [fld for fld in geo_fields if fld.name == self.geo_field]
                if not geo_field_by_name:
                    raise ValueError("Geodjango geometry field not found with the name '%s', fields available are: '%s'" % (self.geo_field,geo_fields_names))
                else:
                    geo_field = geo_field_by_name[0]
        elif geo_fields:
            geo_field = geo_fields[0]
        else:
            raise ValueError('No geodjango geometry fields found in this model queryset')
        
        # Get the shapefile driver
        dr = Driver('ESRI Shapefile')
        
        # create a temporary file to write the shapefile to
        # since we are ultimately going to zip it up
        tmp = tempfile.NamedTemporaryFile(suffix='.shp', mode = 'w+b')
        # we must close the file for GDAL to be able to open and write to it
        tmp.close()
        
        # Creating the datasource
        ds = ogr.OGR_Dr_CreateDataSource(dr._ptr, tmp.name, None)
        
        # Get the right geometry type number for ogr
        if hasattr(geo_field,'geom_type'):
            ogr_type = OGRGeomType(geo_field.geom_type).num
        else:
            ogr_type = OGRGeomType(geo_field._geom).num

        # Set up the native spatial reference of the geometry field using the srid
        if hasattr(geo_field,'srid'):
            native_srs = SpatialReference(geo_field.srid)
        else:
            native_srs = SpatialReference(geo_field._srid)
        
        if self.proj_transform:
            output_srs = SpatialReference(self.proj_transform)
            ct = CoordTransform(native_srs, output_srs)
        else:
            output_srs = native_srs
        
        # create the layer
        # print 'about to try to create data layer'
        # print 'ds: %s, path: %s' % (ds, tmp.name)
        layer = ogr.OGR_DS_CreateLayer(ds, tmp.name, output_srs._ptr, ogr_type, None)
        
        # Create the fields
        # Todo: control field order as param
        for field in attributes:
            fld = ogr.OGR_Fld_Create(str(field.name), 4)
            added = ogr.OGR_L_CreateField(layer, fld, 0)
            check_err(added) 
        
        # Getting the Layer feature definition.
        feature_def = ogr.OGR_L_GetLayerDefn(layer) 
        
        # Loop through queryset creating features
        for item in self.queryset:
            feat = ogr.OGR_F_Create(feature_def)
            
            # For now, set all fields as strings
            # TODO: catch model types and convert to ogr fields
            # http://www.gdal.org/ogr/classOGRFeature.html
            
            # OGR_F_SetFieldDouble
            #OFTReal => FloatField DecimalField
            
            # OGR_F_SetFieldInteger
            #OFTInteger => IntegerField
            
            #OGR_F_SetFieldStrin
            #OFTString => CharField
            
            
            # OGR_F_SetFieldDateTime()
            #OFTDateTime => DateTimeField
            #OFTDate => TimeField
            #OFTDate => DateField
            
            idx = 0
            for field in attributes:
                value = getattr(item,field.name)
                try:
                    string_value = str(value)
                except UnicodeEncodeError, E:
                    # pass for now....
                    # http://trac.osgeo.org/gdal/ticket/882
                    string_value = ''
                ogr.OGR_F_SetFieldString(feat, idx, string_value)
                idx += 1
              
            # Transforming & setting the geometry
            geom = getattr(item,geo_field.name)
            
            # if requested we transform the input geometry
            # to match the shapefiles projection 'to-be'            
            if geom:
                ogr_geom = OGRGeometry(geom.wkt,output_srs)
                if self.proj_transform:
                    ogr_geom.transform(ct)
                # create the geometry
                check_err(ogr.OGR_F_SetGeometry(feat, ogr_geom._ptr))
            else:
                # Case where geometry object is not found because of null value for field
                # effectively looses whole record in shapefile if geometry does not exist
                pass
            
            
            # creat the feature in the layer.
            check_err(ogr.OGR_L_SetFeature(layer, feat))
        
        # Cleaning up
        check_err(ogr.OGR_L_SyncToDisk(layer))
        ogr.OGR_DS_Destroy(ds)
        ogr.OGRCleanupAll()
        
        # Read resulting shapefile into a zipfile buffer
        buffer = cStringIO.StringIO()
        zip = zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED)
        files = ['shp','shx','prj','dbf']
        for item in files:
            filename= '%s.%s' % (tmp.name.replace('.shp',''), item)
            zip.write(filename, arcname='%s.%s' % (self.file_name.replace('.shp',''), item))
        if self.readme:
            zip.writestr('README.txt',self.readme)
        zip.close()
        buffer.flush()
        zip_stream = buffer.getvalue()
        buffer.close()
        
        # Stick it all in a django HttpResponse
        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % self.file_name.replace('.shp','')
        response['Content-length'] = str(len(zip_stream))
        response['Content-Type'] = self.mimetype
        response.write(zip_stream)
        return response