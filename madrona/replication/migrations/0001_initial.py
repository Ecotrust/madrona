# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'ReplicationSetup'
        db.create_table('replication_replicationsetup', (
            ('org_scheme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.OrganizationScheme'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('replication', ['ReplicationSetup'])

        # Adding model 'HabitatThreshold'
        db.create_table('replication_habitatthreshold', (
            ('units', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('minimum_quantity', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('habitat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.FeatureMapping'])),
            ('replication_setup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['replication.ReplicationSetup'])),
        ))
        db.send_create_signal('replication', ['HabitatThreshold'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'ReplicationSetup'
        db.delete_table('replication_replicationsetup')

        # Deleting model 'HabitatThreshold'
        db.delete_table('replication_habitatthreshold')
    
    
    models = {
        'intersection.featuremapping': {
            'Meta': {'object_name': 'FeatureMapping'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'feature': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['intersection.IntersectionFeature']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organization_scheme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.OrganizationScheme']"}),
            'sort': ('django.db.models.fields.FloatField', [], {})
        },
        'intersection.intersectionfeature': {
            'Meta': {'object_name': 'IntersectionFeature'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'feature_model': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multi_shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.MultiFeatureShapefile']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'native_units': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'output_units': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.SingleFeatureShapefile']", 'null': 'True'}),
            'study_region_total': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'intersection.multifeatureshapefile': {
            'Meta': {'object_name': 'MultiFeatureShapefile'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'shapefile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'intersection.organizationscheme': {
            'Meta': {'object_name': 'OrganizationScheme'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'intersection.singlefeatureshapefile': {
            'Meta': {'object_name': 'SingleFeatureShapefile'},
            'clip_to_study_region': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'parent_shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.MultiFeatureShapefile']", 'null': 'True', 'blank': 'True'}),
            'shapefile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'replication.habitatthreshold': {
            'Meta': {'object_name': 'HabitatThreshold'},
            'habitat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.FeatureMapping']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum_quantity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'replication_setup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replication.ReplicationSetup']"}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'replication.replicationsetup': {
            'Meta': {'object_name': 'ReplicationSetup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'org_scheme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.OrganizationScheme']"})
        }
    }
    
    complete_apps = ['replication']
