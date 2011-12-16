# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Bioregion'
        db.create_table('bioregions_bioregion', (
            ('geometry', self.gf('django.contrib.gis.db.models.fields.PolygonField')(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('bioregions', ['Bioregion'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Bioregion'
        db.delete_table('bioregions_bioregion')
    
    
    models = {
        'bioregions.bioregion': {
            'Meta': {'object_name': 'Bioregion'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': str(settings.GEOMETRY_DB_SRID), 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['bioregions']
