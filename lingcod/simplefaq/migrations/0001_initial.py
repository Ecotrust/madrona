# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'FaqGroup'
        db.create_table('simplefaq_faqgroup', (
            ('faq_group_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('importance', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('simplefaq', ['FaqGroup'])

        # Adding model 'Faq'
        db.create_table('simplefaq_faq', (
            ('answer', self.gf('django.db.models.fields.TextField')(max_length=2000)),
            ('importance', self.gf('django.db.models.fields.IntegerField')()),
            ('question', self.gf('django.db.models.fields.TextField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('faq_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['simplefaq.FaqGroup'])),
        ))
        db.send_create_signal('simplefaq', ['Faq'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'FaqGroup'
        db.delete_table('simplefaq_faqgroup')

        # Deleting model 'Faq'
        db.delete_table('simplefaq_faq')
    
    
    models = {
        'simplefaq.faq': {
            'Meta': {'object_name': 'Faq'},
            'answer': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'faq_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['simplefaq.FaqGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.TextField', [], {'max_length': '200'})
        },
        'simplefaq.faqgroup': {
            'Meta': {'object_name': 'FaqGroup'},
            'faq_group_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['simplefaq']
