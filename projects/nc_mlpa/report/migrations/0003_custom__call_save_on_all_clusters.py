from report.models import Cluster
from south.v2 import SchemaMigration

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        for cl in Cluster.objects.all():
            cl.save()
            
    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")
