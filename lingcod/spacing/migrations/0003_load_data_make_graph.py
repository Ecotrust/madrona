from lingcod.spacing.models import Land, create_pickled_graph
from south.v2 import SchemaMigration
from django.core.management import call_command
from django.conf import settings


class Migration(SchemaMigration):
    
    def forwards(self, orm):
        # can't call this yet since columns havent been made 
        # migrations are out of order essentially - we'll do this in 0004
        #call_command('loaddata','south_initial_data.json')
        #create_pickled_graph()
        pass
        
    def backwards(self, orm):
        pass
        
    models = {
        'spacing.land': {
            'Meta': {'object_name': 'Land'},
            'geometry': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': str(settings.GEOMETRY_DB_SRID), 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'spacing.pickledgraph': {
            'Meta': {'object_name': 'PickledGraph'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pickled_graph': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'spacing.spacingpoint': {
            'Meta': {'object_name': 'SpacingPoint'},
            'geometry': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': str(settings.GEOMETRY_DB_SRID)}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['spacing']
        
