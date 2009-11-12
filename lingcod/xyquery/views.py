import struct
from osgeo import gdal
from django.shortcuts import render_to_response
from django.contrib.gis.geos import Point as GEOSPoint
from django.contrib.gis.gdal import SpatialReference
from models import Attribute, Feature, Raster


def query(request):
    x = float(request.REQUEST['x'])
    y = float(request.REQUEST['y'])
    pnt = GEOSPoint(x,y,srid=4326)

    # Query all the vector polygon layers
    polygons = Feature.objects.filter(geom__bboverlaps=pnt).filter(geom__intersects=pnt)
    results = {}
    for poly in polygons:
        attribs = Attribute.objects.filter(feature=poly.pk)
        for attrib in attribs:
            results['%s :: %s' % (poly.layer, attrib.key)] = attrib.value
 
    # Query all the raster layers
    rasters = Raster.objects.all()
    for rast in rasters:
        ds = gdal.Open(str(rast.filepath))
        numbands = ds.RasterCount
        srs = SpatialReference(ds.GetProjection())
        pnt_proj = pnt.transform(srs,clone=True)
        for band in range(1,numbands+1):
            val = getRasterValue(pnt_proj.x, pnt_proj.y, ds, band)
            if val:
                results["%s :: %s" % (rast.layer, "Band %s" % band)] = val
    
    return render_to_response('query.html', {'x': x, 'y':y, 'results': results}) 

def getRasterValue(x,y,ds,bandnum=1):
    band = ds.GetRasterBand(bandnum)
    gt = ds.GetGeoTransform()
    nodata = band.GetNoDataValue()
    try:
        xoff = int((x - gt[0]) / gt[1])
        yoff = int((y - gt[3]) / gt[5]) 
        a = band.ReadAsArray( xoff, yoff, 1, 1)
        #return float(Numeric.sum( Numeric.sum(a) ) / Numeric.size(a))
        val = a[0][0]
        if val == nodata:
            return None
        else:
            return val
    except:
        return None
