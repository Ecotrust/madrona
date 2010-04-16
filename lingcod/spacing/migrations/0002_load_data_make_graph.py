from lingcod.spacing.models import Land, create_pickled_graph
from south.v2 import SchemaMigration

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        call_command('loaddata','south_initial_data.json')
        create_pickled_graph()
        
    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")
        