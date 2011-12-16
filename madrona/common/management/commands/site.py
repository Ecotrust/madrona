from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = "Configures the sites framework to use different domain name"
    args = '[domain name] [optional site id]'

    def handle(self, dname, siteid=None, **options):
        if not siteid:
            siteid = settings.SITE_ID

        s, created = Site.objects.get_or_create(pk=siteid)
        s.domain = dname
        s.name = dname
        s.save()
        
        print "Site ID %s is now configured to run at %s. \n  (Your current settings point to SITE_ID = %s)" % (siteid, dname, settings.SITE_ID)
