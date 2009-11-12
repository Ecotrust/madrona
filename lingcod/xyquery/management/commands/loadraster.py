import os, sys
from osgeo import gdal
from subprocess import Popen
from django.core.management.base import BaseCommand, CommandError
from django.utils.datastructures import SortedDict
from django.contrib.gis.gdal import SpatialReference
from django.conf import settings
from lingcod.xyquery.models import Raster, Layer

from optparse import make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--name', dest='name',
            help='Raster name.'),
        make_option('-s', '--srs', dest='srs',
            help='Spatial reference system of input raster'),
    )
    help = 'Load a shapefile into the xyquery app.'
    args = '[shapefile ...]'

    def parse_layer(self,rast, layername, srs):
        ds = gdal.Open(rast)
        if ds is None:
            raise Exception("Dataset is not valid")
        else:
            rast = os.path.abspath(rast)

        if srs:
            srscmdpart = "-a_srs '%s'" % srs
        else:
            srscmdpart = ''
            if ds.GetProjection() == '' or not ds.GetProjection():
                raise Exception("Looks like the raster doesn't have a projection defined - use --srs")

        # Create a new layer
        overwrite = True
        if overwrite:
            try:
                old_lyr = Layer.objects.get(name=layername)
                old_lyr.delete()
            except:
                pass
        the_layer = Layer(name=layername)
        the_layer.save()
        
        # Make a vrt copy of the dataset
        vrtpath = os.path.abspath(os.path.join(settings.MEDIA_ROOT,"xyquery_rasters",layername+".vrt"))
        command = "gdal_translate %s -of VRT '%s' '%s'" % (srscmdpart, rast, vrtpath)
        output = Popen(command, shell=True).communicate()[0]
        
        ds = gdal.Open(vrtpath)
        if not ds or not os.path.exists(vrtpath):
            raise Exception("%s does not exist .. somthing went screwy in the gdal_translate command \n\n %s" % (vrtpath, command))
        del ds

        # Create a new raster model instance
        the_raster = Raster(layer=the_layer, filepath=vrtpath)
        the_raster.save()

    def handle(self, *rast, **options):
        if len(rast) != 1:
            return "Specify the path of a single raster dataset"
        rast = rast[0]

        if not os.path.exists(rast):
            return "%s not found; Specify the path to an existing raster file" % rast
        
        srs = options.get('srs',None)
        layername = options.get('name',None)
        if not layername:
            layername = os.path.splitext(os.path.basename(rast))[0]

        self.parse_layer(rast, layername, srs)
        return "Raster layer %s has been loaded" % layername
