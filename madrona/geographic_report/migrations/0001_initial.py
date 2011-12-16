# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'GeographicReport'
        db.create_table('geographic_report_geographicreport', (
            ('max_scale', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('geographic_report', ['GeographicReport'])

        # Adding model 'Annotation'
        db.create_table('geographic_report_annotation', (
            ('min', self.gf('django.db.models.fields.FloatField')(blank=True)),
            ('color', self.gf('django.db.models.fields.CharField')(default='000000', max_length=6)),
            ('max', self.gf('django.db.models.fields.FloatField')()),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geographic_report.GeographicReport'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('geographic_report', ['Annotation'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'GeographicReport'
        db.delete_table('geographic_report_geographicreport')

        # Deleting model 'Annotation'
        db.delete_table('geographic_report_annotation')
    
    
    models = {
        'geographic_report.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'color': ('django.db.models.fields.CharField', [], {'default': "'000000'", 'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'max': ('django.db.models.fields.FloatField', [], {}),
            'min': ('django.db.models.fields.FloatField', [], {'blank': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geographic_report.GeographicReport']"})
        },
        'geographic_report.geographicreport': {
            'Meta': {'object_name': 'GeographicReport'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_scale': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['geographic_report']
