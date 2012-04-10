from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.gis import geos
from django.conf import settings
from madrona.studyregion.models import StudyRegion

class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--name', action='store', dest='region_name', default=False,
            help='Give a name to the study region, otherwise the name attribute from the shapefile will be used.'),
    )
    help = "Creates a new study region from a shapefile containing a single multigeometry"
    args = '[input shapefile or wkt string]'

    def handle_ogr(self, inshape, name):
        ds = DataSource(inshape)
        layer = ds[0]  # assume first layer
        feature = layer[0]  #assume first feature
        if not name:
            try:
                name = feature.name
            except:
                raise Exception("No `name` field or --name provided!")

        g1 = feature.geom.geos
        srid = g1.srid
        if not srid:
            # See if we can assume latlon
            missing_srid = True
            ext = list(g1.extent)
            latlonmax = [180,90] * 2
            latlonmin = [x * -1 for x in latlonmax]
            overs = [a for a,b in zip(ext, latlonmax) if a > b]
            unders = [a for a,b in zip(ext, latlonmin) if a < b]
            if len(overs) == len(unders) == 0:
                srid = 4326
                g1.srid = 4326
            else:
                raise Exception("Unknown SRID. Try ewkt format; `SRID=4326;POLYGON((.....))`")
        if g1 and isinstance(g1, geos.Polygon):
            g1 = geos.MultiPolygon(g1)
            g1.srid = srid
        g1.transform(settings.GEOMETRY_DB_SRID)

        region = StudyRegion.objects.create(geometry=g1, name=name, active=True)
        region.save()

        print "Study region created: %s, primary key = %s" % (region.name, region.pk)

    def handle_wkt(self, wkt, name):
        g1 = GEOSGeometry(wkt)
        srid = g1.srid
        if not srid:
            raise Exception("Unknown SRID. Try ewkt format; `SRID=4326;POLYGON((.....))`")
        if g1 and isinstance(g1, geos.Polygon):
            g1 = geos.MultiPolygon(g1)
            g1.srid = srid

        if not name:
            raise Exception("No --name provided!")

        g1.transform(settings.GEOMETRY_DB_SRID)
        region = StudyRegion.objects.create(geometry=g1, name=name, active=True)
        region.save()

        print "Study region created: %s, primary key = %s" % (region.name, region.pk)

    def handle(self, inshape, *args, **options):
        """
        `inshape` can be a wkt string or shapefile path
        """
        htype = ''
        name = options.get('region_name')
        try:
            ds = DataSource(inshape)
            htype = 'ogr'
        except:
            try:
                g1 = GEOSGeometry(inshape)
                htype = 'wkt'
            except:
                pass

        if htype == 'ogr':
            self.handle_ogr(inshape, name)
        elif htype == 'wkt':
            self.handle_wkt(inshape, name)
        else:
            raise Exception("Your input shape is not recognized as a valid datasource or geometry string")
