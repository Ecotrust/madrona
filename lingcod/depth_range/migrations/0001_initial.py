# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'DepthSounding'
        db.create_table('depth_range_depthsounding', (
            ('geometry', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=3310)),
            ('depth_ft', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('depth_range', ['DepthSounding'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'DepthSounding'
        db.delete_table('depth_range_depthsounding')
    
    
    models = {
        'depth_range.depthsounding': {
            'Meta': {'object_name': 'DepthSounding'},
            'depth_ft': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '3310'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['depth_range']
