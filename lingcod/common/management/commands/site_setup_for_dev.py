from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = "Configures the sites framework to use localhost:8000"

    def handle(self, **options):
        site1 = Site.objects.get(pk=1)
        dname = 'localhost:8000'
        site1.domain = dname
        site1.name = dname
        site1.save()
        
        print "The site is now configured to run at %s" % dname
