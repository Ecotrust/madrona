from django.core.management.base import BaseCommand, AppCommand
from django.db import connection, transaction
import os

class Command(BaseCommand):
    help = "Installs a cleangeometry function in postgres required for processing incoming geometries."

    def handle(self, **options):
        path = os.path.abspath(os.path.join(__file__, '../../../cleangeometry.sql'))

        sql = open(path,'r').read()
        # http://stackoverflow.com/questions/1734814/why-isnt-psycopg2-
        # executing-any-of-my-sql-functions-indexerror-tuple-index-o        
        sql = sql.replace('%','%%')

        cursor = connection.cursor()
        cursor.execute(sql)
        print cursor.statusmessage
