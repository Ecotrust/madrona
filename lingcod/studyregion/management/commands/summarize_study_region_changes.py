from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from lingcod.studyregion.models import StudyRegion
from progressbar import Bar, Percentage, RotatingMarker, ProgressBar, ETA
import time


class Command(BaseCommand):
    help = "Switches from one study region to another, reprocessing MPAs and expiring report caches."
    args = '[pk]'
    
    def handle(self, pk, **options):
        # new_study_region = StudyRegion.objects.get(pk=pk)
        # old_study_region = StudyRegion.objects.current()
        # diff = old_study_region.geometry.sym_difference(new_study_region.geometry)        
        # find models that need to be reclipped somehow
        # for model in models:
        #     for obj in model.objects.filter(geometry_intersects=diff)
        #         print "%s,%s,%s" % (obj.__class__.__name__, obj.name, obj.user.username, )
        print """
            **********************************************
            This is just example output until implemented.
            **********************************************
        """
        print "MLPAMpas, MPA Name, cburt"
        print "MLPAMpas, Test MPA, another_user"