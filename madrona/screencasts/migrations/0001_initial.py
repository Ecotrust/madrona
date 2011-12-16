# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Screencast'
        db.create_table('mm_screencast', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=350)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('importance', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('selected_for_help', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('video', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('urlname', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('screencasts', ['Screencast'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Screencast'
        db.delete_table('mm_screencast')
    
    
    models = {
        'screencasts.screencast': {
            'Meta': {'object_name': 'Screencast', 'db_table': "'mm_screencast'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'importance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'selected_for_help': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'urlname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'video': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['screencasts']
