from django.core.management.base import BaseCommand, AppCommand
from django.db import connection, transaction
import os

class Command(BaseCommand):
    help = "Installs a cleangeometry function in postgres required for processing incoming geometries."

    def handle(self, **options):
        path = os.path.abspath(os.path.join(__file__, '../../../sql/cleangeometry.sql'))

        sql = open(path,'r').read()
        # http://stackoverflow.com/questions/1734814/why-isnt-psycopg2-
        # executing-any-of-my-sql-functions-indexerror-tuple-index-o        
        sql = sql.replace('%','%%')

        cursor = connection.cursor()
        cursor.db.enter_transaction_management()

        cursor.execute(sql)
        print cursor.statusmessage
        print "TESTING"

        cursor.execute("select cleangeometry(st_geomfromewkt('SRID=4326;POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))'))")
        assert cursor.fetchall() == [('0103000020E610000001000000050000000000000000003E4000000000000024400000000000002440000000000000344000000000000034400000000000004440000000000000444000000000000044400000000000003E400000000000002440',)]
        cursor.db.commit()
        cursor.db.leave_transaction_management()
        print "CLEANGEOMETRY function installed successfully"
