# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'RasterDataset'
        db.create_table('raster_stats_rasterdataset', (
            ('filepath', self.gf('django.db.models.fields.FilePathField')(path='/Users/perry/src/marinemap/lingcod/raster_stats/test_data', max_length=100, recursive=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
        ))
        db.send_create_signal('raster_stats', ['RasterDataset'])

        # Adding model 'ZonalStatsCache'
        db.create_table('raster_stats_zonalstatscache', (
            ('raster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['raster_stats.RasterDataset'])),
            ('min', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('geom_hash', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('nulls', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('median', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('pixels', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('mode', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('stdev', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('avg', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('raster_stats', ['ZonalStatsCache'])

        # Adding unique constraint on 'ZonalStatsCache', fields ['geom_hash', 'raster']
        db.create_unique('raster_stats_zonalstatscache', ['geom_hash', 'raster_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'RasterDataset'
        db.delete_table('raster_stats_rasterdataset')

        # Deleting model 'ZonalStatsCache'
        db.delete_table('raster_stats_zonalstatscache')

        # Removing unique constraint on 'ZonalStatsCache', fields ['geom_hash', 'raster']
        db.delete_unique('raster_stats_zonalstatscache', ['geom_hash', 'raster_id'])
    
    
    models = {
        'raster_stats.rasterdataset': {
            'Meta': {'object_name': 'RasterDataset'},
            'filepath': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/perry/src/marinemap/lingcod/raster_stats/test_data'", 'max_length': '100', 'recursive': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'raster_stats.zonalstatscache': {
            'Meta': {'unique_together': "(('geom_hash', 'raster'),)", 'object_name': 'ZonalStatsCache'},
            'avg': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'geom_hash': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'median': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'nulls': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'pixels': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'raster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['raster_stats.RasterDataset']"}),
            'stdev': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['raster_stats']
