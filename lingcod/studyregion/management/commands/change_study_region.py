from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from lingcod.studyregion.models import StudyRegion
#from progressbar import Bar, Percentage, RotatingMarker, ProgressBar, ETA
import time


class Command(BaseCommand):
    help = "Switches from one study region to another, reprocessing MPAs and expiring report caches."
    args = '[pk]'

    def handle(self, pk, **options):
        # Turn them all off
        regions = StudyRegion.objects.all()
        for region in regions:
            region.active = False
            region.save()

        # Now active the single study region
        new_study_region = StudyRegion.objects.get(pk=pk)
        new_study_region.active = True
        new_study_region.save()
        
        print "%s is now the active study region" % new_study_region
    
    # Eventually we'll implement this 
    def handle2(self, pk, **options):
        new_study_region = StudyRegion.objects.get(pk=pk)
        old_study_region = StudyRegion.objects.current()
        print """
****************************************************************
This management command does not actually do anything right now. 
It is just a mockup of the desired interface.
****************************************************************
        """
        print """
This process should not be done when the MarineMap application is publicly 
accessible. Please shutdown the server or redirect users to a maintenance page
"""
        answer = raw_input("Type 'yes' to continue, or 'no' to cancel: ")
        if answer == 'yes':
            print ""
            # Get difference between old study region and new
            print "calculating difference between the specified study region and the one currently active..."
            diff = old_study_region.geometry.sym_difference(new_study_region.geometry)
            print """
            current study region: %s
                area: %s
        
            new study region: %s
                area: %s
            
            difference between study regions:
                area: %s
                sections: %s
        
            User Shapes Affected:""" % (old_study_region.name, old_study_region.geometry.area, new_study_region.name, new_study_region.geometry.area, diff.area, len(diff))
        
            # find models that need to be reclipped somehow
            # for model in models:
            #     print "%s: %s" % (model.__class__.__name__, model.objects.filter(geometry_intersects=diff).count(), )
        
            print "            Mpas: 90"
            print ""
            print "Are you sure you would like the switch to the new study region?"
            answer = raw_input("Type 'yes' to continue, or 'no' to cancel: ")
            if answer == 'yes':
                # new_study_region.active = True
                # new_study_region.save()
                print "Processing shapes:"
                widgets = [Bar('-'), ' ', Percentage(), ' | ', ETA(),]
                pbar = ProgressBar(widgets=widgets, maxval=50).start()
                for i in range(50):
                    # Re-run the appropriate manipulators
                    time.sleep(0.1)
                    pbar.update(i+1)
                print "Done processing shapes."
                print "Would you like to send an email notifying users that their shapes have changed?"
                email = raw_input("Type 'yes' or 'no': ")
                if email == 'yes':
                    print "sending emails..."
                    time.sleep(2)
                print "This process is complete. You can now resume public access to the application."
            
            else:
                print "cancelling..."
        else:
            print "cancelling..."
