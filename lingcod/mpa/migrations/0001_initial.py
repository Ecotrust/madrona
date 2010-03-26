# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'MpaDesignation'
        db.create_table('mpa_mpadesignation', (
            ('sort', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('poly_outline_color', self.gf('django.db.models.fields.CharField')(default='ffffffff', max_length=8)),
            ('acronym', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('poly_fill_color', self.gf('django.db.models.fields.CharField')(default='ff0000ff', max_length=8)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('mpa', ['MpaDesignation'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'MpaDesignation'
        db.delete_table('mpa_mpadesignation')
    
    
    models = {
        'mpa.mpadesignation': {
            'Meta': {'object_name': 'MpaDesignation'},
            'acronym': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'poly_fill_color': ('django.db.models.fields.CharField', [], {'default': "'ff0000ff'", 'max_length': '8'}),
            'poly_outline_color': ('django.db.models.fields.CharField', [], {'default': "'ffffffff'", 'max_length': '8'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['mpa']
