import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.contrib.gis.utils import add_postgis_srs

try:
    add_postgis_srs(900913)
    print 'Projection added'
except Exception, E:
    print "Could not insert projection. Error was: %s" % E