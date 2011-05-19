# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ZonalStatsCache.sum'
        db.add_column('raster_stats_zonalstatscache', 'sum', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Changing field 'RasterDataset.filepath'
        db.alter_column('raster_stats_rasterdataset', 'filepath', self.gf('django.db.models.fields.FilePathField')(path='c:\\dev\\bioregions\\marinemap\\lingcod\\raster_stats\\test_data', max_length=100, recursive=True))


    def backwards(self, orm):
        
        # Deleting field 'ZonalStatsCache.sum'
        db.delete_column('raster_stats_zonalstatscache', 'sum')

        # Changing field 'RasterDataset.filepath'
        db.alter_column('raster_stats_rasterdataset', 'filepath', self.gf('django.db.models.fields.FilePathField')(path='/Users/perry/src/marinemap/lingcod/raster_stats/test_data', max_length=100, recursive=True))


    models = {
        'raster_stats.rasterdataset': {
            'Meta': {'object_name': 'RasterDataset'},
            'filepath': ('django.db.models.fields.FilePathField', [], {'path': "'c:\\\\dev\\\\bioregions\\\\marinemap\\\\lingcod\\\\raster_stats\\\\test_data'", 'max_length': '100', 'recursive': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
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
            'stdev': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'sum': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['raster_stats']
