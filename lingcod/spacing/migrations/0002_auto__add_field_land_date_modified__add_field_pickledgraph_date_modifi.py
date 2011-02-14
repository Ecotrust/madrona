# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'Land.date_modified'
        db.add_column('spacing_land', 'date_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 9, 1, 15, 42, 35, 766056), auto_now=True, auto_now_add=True, blank=True), keep_default=False)

        # Adding field 'PickledGraph.date_modified'
        db.add_column('spacing_pickledgraph', 'date_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 9, 1, 15, 42, 35, 765338), auto_now=True, auto_now_add=True, blank=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting field 'Land.date_modified'
        db.delete_column('spacing_land', 'date_modified')

        # Deleting field 'PickledGraph.date_modified'
        db.delete_column('spacing_pickledgraph', 'date_modified')
    
    
    models = {
        'spacing.land': {
            'Meta': {'object_name': 'Land'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 9, 1, 15, 42, 35, 766056)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '3310', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'spacing.pickledgraph': {
            'Meta': {'object_name': 'PickledGraph'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 9, 1, 15, 42, 35, 765338)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pickled_graph': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'spacing.spacingpoint': {
            'Meta': {'object_name': 'SpacingPoint'},
            'geometry': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '3310'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['spacing']
