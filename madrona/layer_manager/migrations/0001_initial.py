# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Theme'
        db.create_table('layer_manager_theme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('header_image', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('header_attrib', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('overview', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.URLField')(max_length=255, null=True, blank=True)),
            ('factsheet_thumb', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('factsheet_link', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('feature_image', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('feature_excerpt', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('feature_link', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('layer_manager', ['Theme'])

        # Adding model 'Layer'
        db.create_table('layer_manager_layer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('layer_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('arcgis_layers', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('subdomains', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('is_sublayer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('legend', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('legend_title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('legend_subtitle', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('utfurl', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('default_on', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('data_overview', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('data_status', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('data_source', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('data_notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('bookmark', self.gf('django.db.models.fields.CharField')(max_length=755, null=True, blank=True)),
            ('map_tiles', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('kml', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('data_download', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('learn_more', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('metadata', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('fact_sheet', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.URLField')(max_length=255, null=True, blank=True)),
            ('attribute_title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('compress_display', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attribute_event', self.gf('django.db.models.fields.CharField')(default='click', max_length=35)),
            ('lookup_field', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('vector_color', self.gf('django.db.models.fields.CharField')(max_length=7, null=True, blank=True)),
            ('vector_fill', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('vector_graphic', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('opacity', self.gf('django.db.models.fields.FloatField')(default=0.5, null=True, blank=True)),
        ))
        db.send_create_signal('layer_manager', ['Layer'])

        # Adding M2M table for field sublayers on 'Layer'
        db.create_table('layer_manager_layer_sublayers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_layer', models.ForeignKey(orm['layer_manager.layer'], null=False)),
            ('to_layer', models.ForeignKey(orm['layer_manager.layer'], null=False))
        ))
        db.create_unique('layer_manager_layer_sublayers', ['from_layer_id', 'to_layer_id'])

        # Adding M2M table for field themes on 'Layer'
        db.create_table('layer_manager_layer_themes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('layer', models.ForeignKey(orm['layer_manager.layer'], null=False)),
            ('theme', models.ForeignKey(orm['layer_manager.theme'], null=False))
        ))
        db.create_unique('layer_manager_layer_themes', ['layer_id', 'theme_id'])

        # Adding M2M table for field attribute_fields on 'Layer'
        db.create_table('layer_manager_layer_attribute_fields', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('layer', models.ForeignKey(orm['layer_manager.layer'], null=False)),
            ('attributeinfo', models.ForeignKey(orm['layer_manager.attributeinfo'], null=False))
        ))
        db.create_unique('layer_manager_layer_attribute_fields', ['layer_id', 'attributeinfo_id'])

        # Adding M2M table for field lookup_table on 'Layer'
        db.create_table('layer_manager_layer_lookup_table', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('layer', models.ForeignKey(orm['layer_manager.layer'], null=False)),
            ('lookupinfo', models.ForeignKey(orm['layer_manager.lookupinfo'], null=False))
        ))
        db.create_unique('layer_manager_layer_lookup_table', ['layer_id', 'lookupinfo_id'])

        # Adding model 'AttributeInfo'
        db.create_table('layer_manager_attributeinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('field_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('precision', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('layer_manager', ['AttributeInfo'])

        # Adding model 'LookupInfo'
        db.create_table('layer_manager_lookupinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=7, null=True, blank=True)),
            ('dashstyle', self.gf('django.db.models.fields.CharField')(default='solid', max_length=11)),
            ('fill', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('graphic', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('layer_manager', ['LookupInfo'])

        # Adding model 'DataNeed'
        db.create_table('layer_manager_dataneed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('contact_email', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('expected_date', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('layer_manager', ['DataNeed'])

        # Adding M2M table for field themes on 'DataNeed'
        db.create_table('layer_manager_dataneed_themes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dataneed', models.ForeignKey(orm['layer_manager.dataneed'], null=False)),
            ('theme', models.ForeignKey(orm['layer_manager.theme'], null=False))
        ))
        db.create_unique('layer_manager_dataneed_themes', ['dataneed_id', 'theme_id'])


    def backwards(self, orm):
        # Deleting model 'Theme'
        db.delete_table('layer_manager_theme')

        # Deleting model 'Layer'
        db.delete_table('layer_manager_layer')

        # Removing M2M table for field sublayers on 'Layer'
        db.delete_table('layer_manager_layer_sublayers')

        # Removing M2M table for field themes on 'Layer'
        db.delete_table('layer_manager_layer_themes')

        # Removing M2M table for field attribute_fields on 'Layer'
        db.delete_table('layer_manager_layer_attribute_fields')

        # Removing M2M table for field lookup_table on 'Layer'
        db.delete_table('layer_manager_layer_lookup_table')

        # Deleting model 'AttributeInfo'
        db.delete_table('layer_manager_attributeinfo')

        # Deleting model 'LookupInfo'
        db.delete_table('layer_manager_lookupinfo')

        # Deleting model 'DataNeed'
        db.delete_table('layer_manager_dataneed')

        # Removing M2M table for field themes on 'DataNeed'
        db.delete_table('layer_manager_dataneed_themes')


    models = {
        'layer_manager.attributeinfo': {
            'Meta': {'object_name': 'AttributeInfo'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'precision': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'layer_manager.dataneed': {
            'Meta': {'object_name': 'DataNeed'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expected_date': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['layer_manager.Theme']", 'null': 'True', 'blank': 'True'})
        },
        'layer_manager.layer': {
            'Meta': {'object_name': 'Layer'},
            'arcgis_layers': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'attribute_event': ('django.db.models.fields.CharField', [], {'default': "'click'", 'max_length': '35'}),
            'attribute_fields': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['layer_manager.AttributeInfo']", 'null': 'True', 'blank': 'True'}),
            'attribute_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'bookmark': ('django.db.models.fields.CharField', [], {'max_length': '755', 'null': 'True', 'blank': 'True'}),
            'compress_display': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'data_download': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'data_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'data_overview': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'data_status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'default_on': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fact_sheet': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sublayer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kml': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'layer_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'learn_more': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'legend': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'legend_subtitle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'legend_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'lookup_field': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'lookup_table': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['layer_manager.LookupInfo']", 'null': 'True', 'blank': 'True'}),
            'map_tiles': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'metadata': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'opacity': ('django.db.models.fields.FloatField', [], {'default': '0.5', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'subdomains': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'sublayers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'sublayers_rel_+'", 'null': 'True', 'to': "orm['layer_manager.Layer']"}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['layer_manager.Theme']", 'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'utfurl': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'vector_color': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            'vector_fill': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'vector_graphic': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'layer_manager.lookupinfo': {
            'Meta': {'object_name': 'LookupInfo'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            'dashstyle': ('django.db.models.fields.CharField', [], {'default': "'solid'", 'max_length': '11'}),
            'fill': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'graphic': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'layer_manager.theme': {
            'Meta': {'object_name': 'Theme'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'factsheet_link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'factsheet_thumb': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'feature_excerpt': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'feature_image': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'feature_link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'header_attrib': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'header_image': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'overview': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['layer_manager']