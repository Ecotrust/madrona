# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'KmlCache'
        db.create_table('common_kmlcache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('kml_text', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('common', ['KmlCache'])


    def backwards(self, orm):
        
        # Deleting model 'KmlCache'
        db.delete_table('common_kmlcache')


    models = {
        'common.kmlcache': {
            'Meta': {'object_name': 'KmlCache'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'kml_text': ('django.db.models.fields.TextField', [], {'default': "''"})
        }
    }

    complete_apps = ['common']
