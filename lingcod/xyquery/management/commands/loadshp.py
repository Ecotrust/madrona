import os
from django.core.management.base import BaseCommand, CommandError
from django.utils.datastructures import SortedDict
from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.gdal import SpatialReference
from django.db import transaction
from lingcod.xyquery.models import Feature, Layer, Attribute

from optparse import make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--name', dest='name',
            help='Layer name.'),
        make_option('-f', '--field', dest='fields',action='append', default=[],
            help='Field name to include in attribute table (use multiple -f to include multiple fields).'),
    )
    help = 'Load a shapefile into the xyquery app.'
    args = '[shapefile ...]'

    @transaction.commit_on_success
    def parse_layer(self,shapefile, layername, fields_of_interest):
        ds = DataSource(shapefile)
        lyr = ds[0]
        num_feat = lyr.num_feat

        overwrite = True
        if overwrite:
            try:
                old_lyr = Layer.objects.get(name=layername)
                old_lyr.delete()
            except:
                pass
        try:
            the_layer = Layer(name=layername)
            the_layer.save()
        except:
            raise Exception('Unable to create layer named %s' % layername)
        
        wgs84 = SpatialReference(4326)
        pctdone = 0
        for feat in lyr:
            try:
                the_geometry = feat.geom.transform(wgs84,clone=True)
                the_feature = Feature(layer=the_layer, geom=the_geometry.wkt)
                the_feature.save()
            except:
                raise Exception('Unable to create feature')

            try:
                for fld in lyr.fields:
                    if fld in fields_of_interest or len(fields_of_interest)==0:
                        the_attribute = Attribute(key=fld, value=str(feat[fld]), feature=the_feature)
                        the_attribute.save()
            except:
                raise Exception('Unable to create attribute')

            oldpctdone = pctdone
            pctdone = int((feat.fid * 100.) / float(num_feat))
            if pctdone > oldpctdone:
                print "Completed %d percent of %d features" % (pctdone, num_feat)

    def handle(self, *shapefile, **options):
        if len(shapefile) != 1:
            return "Specify the path of a single .shp file"
        shapefile = shapefile[0]

        if not os.path.exists(shapefile):
            return "%s not found; Specify the path to an existing .shp file" % shapefile
        
        layername = options.get('name',None)
        if not layername:
            layername = os.path.splitext(os.path.basename(shapefile))[0]
        fields_of_interest = options.get('fields',[])

        self.parse_layer(shapefile, layername, fields_of_interest)
        return "Layer %s has been created" % layername
