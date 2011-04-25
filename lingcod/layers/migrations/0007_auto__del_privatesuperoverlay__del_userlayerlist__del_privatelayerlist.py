# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'PrivateSuperOverlay'
        db.delete_table('layers_privatesuperoverlay')

        # Removing M2M table for field sharing_groups on 'PrivateSuperOverlay'
        db.delete_table('layers_privatesuperoverlay_sharing_groups')

        # Deleting model 'UserLayerList'
        db.delete_table('layers_userlayerlist')

        # Removing M2M table for field user on 'UserLayerList'
        db.delete_table('layers_userlayerlist_user')

        # Deleting model 'PrivateLayerList'
        db.delete_table('layers_privatelayerlist')

        # Removing M2M table for field sharing_groups on 'PrivateLayerList'
        db.delete_table('layers_privatelayerlist_sharing_groups')

        # Deleting field 'PublicLayerList.kml'
        db.delete_column('layers_publiclayerlist', 'kml')

        # Adding field 'PublicLayerList.kml_file'
        db.add_column('layers_publiclayerlist', 'kml_file', self.gf('django.db.models.fields.files.FileField')(default='', max_length=510), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'PrivateSuperOverlay'
        db.create_table('layers_privatesuperoverlay', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='layers_privatesuperoverlay_related', to=orm['auth.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='layers_privatesuperoverlay_related', null=True, to=orm['contenttypes.ContentType'], blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_kml', self.gf('django.db.models.fields.FilePathField')(path='/mnt/EBS_superoverlays/display', max_length=100, recursive=True, match='^doc.kml$')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='255')),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('layers', ['PrivateSuperOverlay'])

        # Adding M2M table for field sharing_groups on 'PrivateSuperOverlay'
        db.create_table('layers_privatesuperoverlay_sharing_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('privatesuperoverlay', models.ForeignKey(orm['layers.privatesuperoverlay'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('layers_privatesuperoverlay_sharing_groups', ['privatesuperoverlay_id', 'group_id'])

        # Adding model 'UserLayerList'
        db.create_table('layers_userlayerlist', (
            ('kml', self.gf('django.db.models.fields.files.FileField')(max_length=510)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('layers', ['UserLayerList'])

        # Adding M2M table for field user on 'UserLayerList'
        db.create_table('layers_userlayerlist_user', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userlayerlist', models.ForeignKey(orm['layers.userlayerlist'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('layers_userlayerlist_user', ['userlayerlist_id', 'user_id'])

        # Adding model 'PrivateLayerList'
        db.create_table('layers_privatelayerlist', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='layers_privatelayerlist_related', to=orm['auth.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='layers_privatelayerlist_related', null=True, to=orm['contenttypes.ContentType'], blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='255')),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('kml_file', self.gf('django.db.models.fields.files.FileField')(max_length=510)),
        ))
        db.send_create_signal('layers', ['PrivateLayerList'])

        # Adding M2M table for field sharing_groups on 'PrivateLayerList'
        db.create_table('layers_privatelayerlist_sharing_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('privatelayerlist', models.ForeignKey(orm['layers.privatelayerlist'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('layers_privatelayerlist_sharing_groups', ['privatelayerlist_id', 'group_id'])

        # User chose to not deal with backwards NULL issues for 'PublicLayerList.kml'
        raise RuntimeError("Cannot reverse this migration. 'PublicLayerList.kml' and its values cannot be restored.")

        # Deleting field 'PublicLayerList.kml_file'
        db.delete_column('layers_publiclayerlist', 'kml_file')


    models = {
        'layers.publiclayerlist': {
            'Meta': {'object_name': 'PublicLayerList'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kml_file': ('django.db.models.fields.files.FileField', [], {'max_length': '510'})
        }
    }

    complete_apps = ['layers']
