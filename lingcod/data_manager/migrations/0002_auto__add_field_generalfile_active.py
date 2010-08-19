# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'GeneralFile.active'
        db.add_column('data_manager_generalfile', 'active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting field 'GeneralFile.active'
        db.delete_column('data_manager_generalfile', 'active')
    
    
    models = {
        'data_manager.datalayer': {
            'Meta': {'object_name': 'DataLayer'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'})
        },
        'data_manager.generalfile': {
            'Meta': {'object_name': 'GeneralFile'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'data_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['data_manager.DataLayer']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'data_manager.shapefile': {
            'Meta': {'object_name': 'Shapefile'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'analysis_updated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'data_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['data_manager.DataLayer']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'display_updated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'field_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shapefile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'truncated_comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'update_analysis_layer': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'update_display_layer': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'data_manager.shapefilefield': {
            'Meta': {'object_name': 'ShapefileField'},
            'distinct_values': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['data_manager.Shapefile']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['data_manager']
