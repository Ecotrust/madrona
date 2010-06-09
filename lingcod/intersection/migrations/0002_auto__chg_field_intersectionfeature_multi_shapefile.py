# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'IntersectionFeature.multi_shapefile'
        db.alter_column('intersection_intersectionfeature', 'multi_shapefile_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.MultiFeatureShapefile'], null=True, blank=True))
    
    
    def backwards(self, orm):
        
        # Changing field 'IntersectionFeature.multi_shapefile'
        db.alter_column('intersection_intersectionfeature', 'multi_shapefile_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.MultiFeatureShapefile'], null=True))
    
    
    models = {
        'intersection.arealfeature': {
            'Meta': {'object_name': 'ArealFeature'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'feature_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.IntersectionFeature']"}),
            'geometry': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '3310'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'intersection.featuremapping': {
            'Meta': {'object_name': 'FeatureMapping'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'feature': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['intersection.IntersectionFeature']", 'symmetrical': 'False'}),
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
            'multi_shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.MultiFeatureShapefile']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'native_units': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'output_units': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.SingleFeatureShapefile']", 'null': 'True'}),
            'study_region_total': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'intersection.linearfeature': {
            'Meta': {'object_name': 'LinearFeature'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'feature_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.IntersectionFeature']"}),
            'geometry': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '3310'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
        'intersection.pointfeature': {
            'Meta': {'object_name': 'PointFeature'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'feature_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.IntersectionFeature']"}),
            'geometry': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '3310'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'intersection.resultcache': {
            'Meta': {'unique_together': "(('wkt_hash', 'intersection_feature'),)", 'object_name': 'ResultCache'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.GeometryCollectionField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intersection_feature': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.IntersectionFeature']"}),
            'percent_of_total': ('django.db.models.fields.FloatField', [], {}),
            'result': ('django.db.models.fields.FloatField', [], {}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'wkt_hash': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'intersection.shapefilefield': {
            'Meta': {'object_name': 'ShapefileField'},
            'distinct_values': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.MultiFeatureShapefile']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
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
        'intersection.testpolygon': {
            'Meta': {'object_name': 'TestPolygon'},
            'geometry': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '3310'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['intersection']
