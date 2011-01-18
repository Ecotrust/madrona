from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from lingcod.common.utils import get_class

#omm_manipulator_list = ['EastOfTerritorialSeaLine', 'TerrestrialAndEstuaries', 'Terrestrial', 'Estuaries']

class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--name', action='store', dest='region_name', default=False,
            help='Give a name to the manipulator, otherwise the name attribute from the shapefile will be used.'),
    )
    help = """Creates a new study region from a shapefile containing a single multigeometry.
            \n\tmanage.py create_manipulator_geom <path to shape> <module name>.models.<manipulator model name>"""
    args = '[shapefile, manipulator]'
    
    def handle(self, shapefile, manipulator, *args, **options):
        try:
            manip_model = get_class(manipulator)
        except:
            raise Exception("The %s model could not be found.  \nBe sure and provide the complete description: <module name>.models.<manipulator model name>" %manipulator)
            
        ds = DataSource(shapefile)
        if len(ds) != 1:
            raise Exception("Data source should only contain a single layer. Aborting.")
        
        layer = ds[0]
        if len(layer) != 1: 
            raise Exception("Layer should containing ONLY a single feature")

        if not 'polygon' in layer.geom_type.name.lower():
            print layer.geom_type.name
            raise Exception("This geometry must be a polygon")

        mapping = {'geometry': 'MULTIPOLYGON'}
            
        lm = LayerMapping(manip_model, shapefile, mapping)
        lm.save()
        manip_geom = manip_model.objects.order_by('-creation_date')[0]
        if options.get('region_name'):
            manip_geom.name = options.get('region_name')
            manip_geom.save()
        else:
            manip_geom.name = layer.name
            manip_geom.save()
        
        print ""
        print "The manipulaotr geometry, %s, has been added to the %s model with primary key = %s" % (manip_geom.name, manipulator, manip_geom.pk)
        
        print "To switch to this geometry, you will need to run 'manage.py change_manipulator_geom %s %s'" % (manip_geom.pk, manipulator)
        print ""
