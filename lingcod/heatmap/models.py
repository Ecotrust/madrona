from django.contrib.gis.db import models
from django.conf import settings
from lingcod.studyregion.models import *
import os
import sys
import numpy
import tempfile
from osgeo import gdal, osr
    
CELL_SIZE = 50

def readArray(input):
    """Borrowed from Matt Perry"""
    data = gdal.Open(input)
    band = data.GetRasterBand(1)
    
    return band.ReadAsArray()

def create_blank_raster(extent,cellsize,outfile,format,srid=settings.GEOMETRY_DB_SRID):
    """
    Creates a blank raster dataset with all zeros.  This code came from Matt Perry: http://perrygeo.googlecode.com/hg/gis-bin/blank_raster.py and got modified
    to set the projection.
    """
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(srid)
    ydist = extent[3] - extent[1]
    xdist = extent[2] - extent[0]
    xcount = int((xdist/cellsize)+1)
    ycount = int((ydist/cellsize)+1)

    # Create the blank numpy array
    outArray = numpy.zeros( (ycount, xcount) )

    # Create output raster  
    driver = gdal.GetDriverByName( format )
    dst_ds = driver.Create( outfile, xcount, ycount, 1, gdal.GDT_UInt16 )

    # This is bizzarly complicated
    # the GT(2) and GT(4) coefficients are zero,     
    # and the GT(1) is pixel width, and GT(5) is pixel height.     
    # The (GT(0),GT(3)) position is the top left corner of the top left pixel
    gt = (extent[0],cellsize,0,extent[3],0,(cellsize*-1.))
    dst_ds.SetGeoTransform(gt)
    dst_ds.SetProjection( srs.ExportToWkt() )
    
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(outArray,0,0)
    dst_ds = None
    return outfile
    
def create_raster_from_matrix(matrix,outfile,extent=None,cellsize=CELL_SIZE,format='GTiff',srid=settings.GEOMETRY_DB_SRID):
    """
    Creates a blank raster dataset with all 1s where there are shapes in the shapefile.
    """
    if extent is None:
        extent = StudyRegion.objects.current().geometry.extent
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(srid)
    ydist = extent[3] - extent[1]
    xdist = extent[2] - extent[0]
    xcount = int((xdist/cellsize)+1)
    ycount = int((ydist/cellsize)+1)

    # Create output raster  
    driver = gdal.GetDriverByName( format )
    dst_ds = driver.Create( outfile, xcount, ycount, 1, gdal.GDT_UInt16 )

    # This is bizzarly complicated
    # the GT(2) and GT(4) coefficients are zero,     
    # and the GT(1) is pixel width, and GT(5) is pixel height.     
    # The (GT(0),GT(3)) position is the top left corner of the top left pixel
    gt = (extent[0],cellsize,0,extent[3],0,(cellsize*-1.))
    dst_ds.SetGeoTransform(gt)
    dst_ds.SetProjection( srs.ExportToWkt() )

    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(matrix,0,0)
    dst_band.SetNoDataValue(0.0)
    min_val, max_val = dst_band.ComputeRasterMinMax()
    start_color = (255,255,0,160)
    end_color = (255,0,0,160)
    ct = gdal.ColorTable()
    ct.CreateColorRamp(int(min_val),start_color,int(max_val),end_color)
    dst_band.SetColorTable(ct)
    dst_ds = None
    return outfile

def shapefile_to_matrix(shapefile,cellsize=CELL_SIZE,extent=None):
    if extent is None:
        extent = StudyRegion.objects.current().geometry.extent
    tf = tempfile.mktemp()
    rast = create_blank_raster(extent,cellsize,tf,'GTiff')
    layer_arg = '-l ' + os.path.basename(shapefile).split(os.path.extsep)[0]
    sys_string = 'gdal_rasterize -b 1 -burn 1 %s %s %s' % (layer_arg,shapefile,tf)
    os.system(sys_string)
    matrix = readArray(tf)
    os.remove(tf)
    return matrix
    
def create_heatmap(shp_list):
    matrices = []
    for shp in shp_list:
        matrices.append(shapefile_to_matrix(shp))
    for i,matrix in enumerate(matrices):
        if i==0:
            mat = matrix
        else:
            mat += matrix
    outfile = tempfile.NamedTemporaryFile(suffix='.tif', mode='w+b')
    outfile.close()
    return create_raster_from_matrix(mat,outfile.name)
        


