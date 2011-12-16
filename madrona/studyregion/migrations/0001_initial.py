# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'StudyRegion'
        db.create_table(u'mm_study_region', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lookAt_Lat', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('lookAt_Lon', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('lookAt_Heading', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('lookAt_Range', self.gf('django.db.models.fields.FloatField')(default=80000)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lookAt_Tilt', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('studyregion', ['StudyRegion'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'StudyRegion'
        db.delete_table(u'mm_study_region')
    
    
    models = {
        'studyregion.studyregion': {
            'Meta': {'object_name': 'StudyRegion', 'db_table': "u'mm_study_region'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': str(settings.GEOMETRY_DB_SRID), 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lookAt_Heading': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'lookAt_Lat': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'lookAt_Lon': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'lookAt_Range': ('django.db.models.fields.FloatField', [], {'default': '80000'}),
            'lookAt_Tilt': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['studyregion']
