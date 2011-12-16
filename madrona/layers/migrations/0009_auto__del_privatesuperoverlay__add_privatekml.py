# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'PrivateSuperOverlay' (not yet)
        # db.delete_table('layers_privatesuperoverlay')

        # Adding model 'PrivateKml'
        db.create_table('layers_privatekml', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('priority', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length='255')),
            ('base_kml', self.gf('django.db.models.fields.FilePathField')(path='/mnt/EBS_superoverlays/display', max_length=100, recursive=True, match='^*.kml$')),
        ))
        db.send_create_signal('layers', ['PrivateKml'])

        # Adding M2M table for field sharing_groups on 'PrivateKml'
        db.create_table('layers_privatekml_sharing_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('privatekml', models.ForeignKey(orm['layers.privatekml'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('layers_privatekml_sharing_groups', ['privatekml_id', 'group_id'])


    def backwards(self, orm):
        
        # Deleting model 'PrivateKml'
        db.delete_table('layers_privatekml')

        # Removing M2M table for field sharing_groups on 'PrivateKml'
        db.delete_table('layers_privatekml_sharing_groups')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'layers.privatekml': {
            'Meta': {'object_name': 'PrivateKml'},
            'base_kml': ('django.db.models.fields.FilePathField', [], {'path': "'/mnt/EBS_superoverlays/display'", 'max_length': '100', 'recursive': 'True', 'match': "'^*.kml$'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'255'"}),
            'priority': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'sharing_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'})
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
