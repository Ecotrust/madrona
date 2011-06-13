# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PrivateSuperOverlay'
        db.create_table('layers_privatesuperoverlay', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('priority', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length='255')),
            ('base_kml', self.gf('django.db.models.fields.FilePathField')(path='/mnt/EBS_superoverlays/display', max_length=100, recursive=True, match='^doc.kml$')),
        ))
        db.send_create_signal('layers', ['PrivateSuperOverlay'])


    def backwards(self, orm):
        
        # Deleting model 'PrivateSuperOverlay'
        db.delete_table('layers_privatesuperoverlay')


    models = {
        'layers.privatesuperoverlay': {
            'Meta': {'object_name': 'PrivateSuperOverlay'},
            'base_kml': ('django.db.models.fields.FilePathField', [], {'path': "'/mnt/EBS_superoverlays/display'", 'max_length': '100', 'recursive': 'True', 'match': "'^doc.kml$'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'255'"}),
            'priority': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'layers.publiclayerlist': {
            'Meta': {'object_name': 'PublicLayerList'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kml_file': ('django.db.models.fields.files.FileField', [], {'max_length': '510'})
        }
    }

    complete_apps = ['layers']
