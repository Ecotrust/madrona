# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'ShareableContent'
        db.create_table('sharing_shareablecontent', (
            ('shared_content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shared_content_type', to=orm['contenttypes.ContentType'])),
            ('container_content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('container_set_property', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
        ))
        db.send_create_signal('sharing', ['ShareableContent'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'ShareableContent'
        db.delete_table('sharing_shareablecontent')
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sharing.shareablecontent': {
            'Meta': {'object_name': 'ShareableContent'},
            'container_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'container_set_property': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shared_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shared_content_type'", 'to': "orm['contenttypes.ContentType']"})
        }
    }
    
    complete_apps = ['sharing']
