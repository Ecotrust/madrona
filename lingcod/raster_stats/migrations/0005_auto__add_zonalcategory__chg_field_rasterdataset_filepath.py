# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ZonalCategory'
        db.create_table('raster_stats_zonalcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.IntegerField')()),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('raster_stats', ['ZonalCategory'])

        # Adding M2M table for field categories on 'ZonalStatsCache'
        db.create_table('raster_stats_zonalstatscache_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('zonalstatscache', models.ForeignKey(orm['raster_stats.zonalstatscache'], null=False)),
            ('zonalcategory', models.ForeignKey(orm['raster_stats.zonalcategory'], null=False))
        ))
        db.create_unique('raster_stats_zonalstatscache_categories', ['zonalstatscache_id', 'zonalcategory_id'])

        # Changing field 'RasterDataset.filepath'
        db.alter_column('raster_stats_rasterdataset', 'filepath', self.gf('django.db.models.fields.FilePathField')(path='/usr/local/src/marinemap/lingcod/raster_stats/test_data', max_length=255, recursive=True))


    def backwards(self, orm):
        
        # Deleting model 'ZonalCategory'
        db.delete_table('raster_stats_zonalcategory')

        # Removing M2M table for field categories on 'ZonalStatsCache'
        db.delete_table('raster_stats_zonalstatscache_categories')

        # Changing field 'RasterDataset.filepath'
        db.alter_column('raster_stats_rasterdataset', 'filepath', self.gf('django.db.models.fields.FilePathField')(path='c:\\dev\\bioregions\\marinemap\\lingcod\\raster_stats\\test_data', max_length=255, recursive=True))


    models = {
        'raster_stats.rasterdataset': {
            'Meta': {'object_name': 'RasterDataset'},
            'filepath': ('django.db.models.fields.FilePathField', [], {'path': "'/usr/local/src/marinemap/lingcod/raster_stats/test_data'", 'max_length': '255', 'recursive': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'raster_stats.zonalcategory': {
            'Meta': {'object_name': 'ZonalCategory'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'raster_stats.zonalstatscache': {
            'Meta': {'unique_together': "(('geom_hash', 'raster'),)", 'object_name': 'ZonalStatsCache'},
            'avg': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['raster_stats.ZonalCategory']", 'symmetrical': 'False'}),
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
