# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'MultiFeatureShapefile'
        db.create_table('intersection_multifeatureshapefile', (
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('shapefile', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True, null=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('metadata', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('intersection', ['MultiFeatureShapefile'])

        # Adding model 'SingleFeatureShapefile'
        db.create_table('intersection_singlefeatureshapefile', (
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('shapefile', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('clip_to_study_region', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True, null=True)),
            ('parent_shapefile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.MultiFeatureShapefile'], null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('metadata', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('intersection', ['SingleFeatureShapefile'])

        # Adding model 'ShapefileField'
        db.create_table('intersection_shapefilefield', (
            ('shapefile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.MultiFeatureShapefile'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('distinct_values', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('intersection', ['ShapefileField'])

        # Adding model 'TestPolygon'
        db.create_table('intersection_testpolygon', (
            ('geometry', self.gf('django.contrib.gis.db.models.fields.PolygonField')(srid=3310)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('intersection', ['TestPolygon'])

        # Adding model 'IntersectionFeature'
        db.create_table('intersection_intersectionfeature', (
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('shapefile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.SingleFeatureShapefile'], null=True)),
            ('feature_model', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('output_units', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('native_units', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('study_region_total', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('multi_shapefile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.MultiFeatureShapefile'], null=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('intersection', ['IntersectionFeature'])

        # Adding model 'OrganizationScheme'
        db.create_table('intersection_organizationscheme', (
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('intersection', ['OrganizationScheme'])

        # Adding model 'FeatureMapping'
        db.create_table('intersection_featuremapping', (
            ('sort', self.gf('django.db.models.fields.FloatField')()),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('organization_scheme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.OrganizationScheme'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('intersection', ['FeatureMapping'])

        # Adding M2M table for field feature on 'FeatureMapping'
        db.create_table('intersection_featuremapping_feature', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('featuremapping', models.ForeignKey(orm['intersection.featuremapping'], null=False)),
            ('intersectionfeature', models.ForeignKey(orm['intersection.intersectionfeature'], null=False))
        ))
        db.create_unique('intersection_featuremapping_feature', ['featuremapping_id', 'intersectionfeature_id'])

        # Adding model 'ArealFeature'
        db.create_table('intersection_arealfeature', (
            ('feature_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.IntersectionFeature'])),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.PolygonField')(srid=3310)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('intersection', ['ArealFeature'])

        # Adding model 'LinearFeature'
        db.create_table('intersection_linearfeature', (
            ('feature_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.IntersectionFeature'])),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=3310)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('intersection', ['LinearFeature'])

        # Adding model 'PointFeature'
        db.create_table('intersection_pointfeature', (
            ('feature_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.IntersectionFeature'])),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=3310)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('intersection', ['PointFeature'])

        # Adding model 'ResultCache'
        db.create_table('intersection_resultcache', (
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.GeometryCollectionField')()),
            ('percent_of_total', self.gf('django.db.models.fields.FloatField')()),
            ('wkt_hash', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('intersection_feature', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.IntersectionFeature'])),
            ('result', self.gf('django.db.models.fields.FloatField')()),
            ('units', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('intersection', ['ResultCache'])

        # Adding unique constraint on 'ResultCache', fields ['wkt_hash', 'intersection_feature']
        db.create_unique('intersection_resultcache', ['wkt_hash', 'intersection_feature_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'MultiFeatureShapefile'
        db.delete_table('intersection_multifeatureshapefile')

        # Deleting model 'SingleFeatureShapefile'
        db.delete_table('intersection_singlefeatureshapefile')

        # Deleting model 'ShapefileField'
        db.delete_table('intersection_shapefilefield')

        # Deleting model 'TestPolygon'
        db.delete_table('intersection_testpolygon')

        # Deleting model 'IntersectionFeature'
        db.delete_table('intersection_intersectionfeature')

        # Deleting model 'OrganizationScheme'
        db.delete_table('intersection_organizationscheme')

        # Deleting model 'FeatureMapping'
        db.delete_table('intersection_featuremapping')

        # Removing M2M table for field feature on 'FeatureMapping'
        db.delete_table('intersection_featuremapping_feature')

        # Deleting model 'ArealFeature'
        db.delete_table('intersection_arealfeature')

        # Deleting model 'LinearFeature'
        db.delete_table('intersection_linearfeature')

        # Deleting model 'PointFeature'
        db.delete_table('intersection_pointfeature')

        # Deleting model 'ResultCache'
        db.delete_table('intersection_resultcache')

        # Removing unique constraint on 'ResultCache', fields ['wkt_hash', 'intersection_feature']
        db.delete_unique('intersection_resultcache', ['wkt_hash', 'intersection_feature_id'])
    
    
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
