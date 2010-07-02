# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'URLtoTaskID'
        db.create_table('async_urltotaskid', (
            ('url', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task_id', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('async', ['URLtoTaskID'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'URLtoTaskID'
        db.delete_table('async_urltotaskid')
    
    
    models = {
        'async.urltotaskid': {
            'Meta': {'object_name': 'URLtoTaskID'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_id': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.TextField', [], {})
        }
    }
    
    complete_apps = ['async']
