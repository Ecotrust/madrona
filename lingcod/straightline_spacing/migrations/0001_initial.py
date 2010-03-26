# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'SpacingPoint'
        db.create_table('straightline_spacing_spacingpoint', (
            ('geometry', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=3310)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('straightline_spacing', ['SpacingPoint'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'SpacingPoint'
        db.delete_table('straightline_spacing_spacingpoint')
    
    
    models = {
        'straightline_spacing.spacingpoint': {
            'Meta': {'object_name': 'SpacingPoint'},
            'geometry': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '3310'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['straightline_spacing']
