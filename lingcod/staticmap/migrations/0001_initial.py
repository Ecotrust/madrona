# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'MapConfig'
        db.create_table('staticmap_mapconfig', (
            ('mapfile', self.gf('django.db.models.fields.files.FileField')(max_length=510)),
            ('default_width', self.gf('django.db.models.fields.IntegerField')()),
            ('default_srid', self.gf('django.db.models.fields.IntegerField')(default=4326)),
            ('mapname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('default_x1', self.gf('django.db.models.fields.FloatField')()),
            ('default_x2', self.gf('django.db.models.fields.FloatField')()),
            ('default_y2', self.gf('django.db.models.fields.FloatField')()),
            ('default_y1', self.gf('django.db.models.fields.FloatField')()),
            ('default_height', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('staticmap', ['MapConfig'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'MapConfig'
        db.delete_table('staticmap_mapconfig')
    
    
    models = {
        'staticmap.mapconfig': {
            'Meta': {'object_name': 'MapConfig'},
            'default_height': ('django.db.models.fields.IntegerField', [], {}),
            'default_srid': ('django.db.models.fields.IntegerField', [], {'default': '4326'}),
            'default_width': ('django.db.models.fields.IntegerField', [], {}),
            'default_x1': ('django.db.models.fields.FloatField', [], {}),
            'default_x2': ('django.db.models.fields.FloatField', [], {}),
            'default_y1': ('django.db.models.fields.FloatField', [], {}),
            'default_y2': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mapfile': ('django.db.models.fields.files.FileField', [], {'max_length': '510'}),
            'mapname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }
    
    complete_apps = ['staticmap']
