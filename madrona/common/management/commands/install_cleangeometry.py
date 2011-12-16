from django.core.management.base import BaseCommand, AppCommand
from django.db import connection, transaction
import os

class Command(BaseCommand):
    help = "Installs a cleangeometry function in postgres required for processing incoming geometries."
    
    def handle(self, **options):
        path = os.path.abspath(os.path.join(__file__, '../../../cleangeometry.sql'))
        print """
        
        It's too hard to do this using the django connection interface automatically, but here's how you can do it yourself:
        
        cat %s | psql %s -U %s
        
        just copy and paste that into your terminal and you are done!
        
        """ % (path, connection.settings_dict['NAME'], connection.settings_dict['USER'])