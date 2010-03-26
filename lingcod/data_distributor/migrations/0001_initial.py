# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'PotentialTarget'
        db.create_table('data_distributor_potentialtarget', (
            ('module_text', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('data_distributor', ['PotentialTarget'])

        # Adding model 'PotentialTargetField'
        db.create_table('data_distributor_potentialtargetfield', (
            ('potential_target', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_distributor.PotentialTarget'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('data_distributor', ['PotentialTargetField'])

        # Adding model 'LoadSetup'
        db.create_table('data_distributor_loadsetup', (
            ('origin_data_layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_manager.DataLayer'])),
            ('origin_field_choices', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('target_model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_distributor.PotentialTarget'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('geometry_only', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('target_field_choices', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target_field', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('origin_field', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('data_distributor', ['LoadSetup'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'PotentialTarget'
        db.delete_table('data_distributor_potentialtarget')

        # Deleting model 'PotentialTargetField'
        db.delete_table('data_distributor_potentialtargetfield')

        # Deleting model 'LoadSetup'
        db.delete_table('data_distributor_loadsetup')
    
    
    models = {
        'data_distributor.loadsetup': {
            'Meta': {'object_name': 'LoadSetup'},
            'geometry_only': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'origin_data_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['data_manager.DataLayer']"}),
            'origin_field': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'origin_field_choices': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'target_field': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'target_field_choices': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'target_model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['data_distributor.PotentialTarget']"})
        },
        'data_distributor.potentialtarget': {
            'Meta': {'object_name': 'PotentialTarget'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module_text': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'data_distributor.potentialtargetfield': {
            'Meta': {'object_name': 'PotentialTargetField'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'potential_target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['data_distributor.PotentialTarget']"})
        },
        'data_manager.datalayer': {
            'Meta': {'object_name': 'DataLayer'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'})
        }
    }
    
    complete_apps = ['data_distributor']
