# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'DataLayer'
        db.create_table('data_manager_datalayer', (
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True, null=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('metadata', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('data_manager', ['DataLayer'])

        # Adding model 'GeneralFile'
        db.create_table('data_manager_generalfile', (
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('data_layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_manager.DataLayer'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('data_manager', ['GeneralFile'])

        # Adding model 'Shapefile'
        db.create_table('data_manager_shapefile', (
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('analysis_updated', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('shapefile', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('truncated_comment', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('data_layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_manager.DataLayer'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('field_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('update_analysis_layer', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('display_updated', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('update_display_layer', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('data_manager', ['Shapefile'])

        # Adding model 'ShapefileField'
        db.create_table('data_manager_shapefilefield', (
            ('shapefile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_manager.Shapefile'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('distinct_values', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('data_manager', ['ShapefileField'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'DataLayer'
        db.delete_table('data_manager_datalayer')

        # Deleting model 'GeneralFile'
        db.delete_table('data_manager_generalfile')

        # Deleting model 'Shapefile'
        db.delete_table('data_manager_shapefile')

        # Deleting model 'ShapefileField'
        db.delete_table('data_manager_shapefilefield')
    
    
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
