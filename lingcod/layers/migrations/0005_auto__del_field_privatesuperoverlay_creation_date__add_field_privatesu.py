# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'PrivateSuperOverlay.creation_date'
        db.delete_column('layers_privatesuperoverlay', 'creation_date')

        # Adding field 'PrivateSuperOverlay.date_created'
        db.add_column('layers_privatesuperoverlay', 'date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.date(2011, 2, 9), blank=True), keep_default=False)

        # Adding field 'PrivateSuperOverlay.date_modified'
        db.add_column('layers_privatesuperoverlay', 'date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.date(2011, 2, 9), blank=True), keep_default=False)

        # Adding field 'PrivateSuperOverlay.content_type'
        db.add_column('layers_privatesuperoverlay', 'content_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='layers_privatesuperoverlay_related', null=True, to=orm['contenttypes.ContentType']), keep_default=False)

        # Adding field 'PrivateSuperOverlay.object_id'
        db.add_column('layers_privatesuperoverlay', 'object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True), keep_default=False)

        # Changing field 'PrivateSuperOverlay.base_kml'
        db.alter_column('layers_privatesuperoverlay', 'base_kml', self.gf('django.db.models.fields.FilePathField')(path='/mnt/EBS_superoverlays/display', max_length=100, recursive=True, match='^doc.kml$'))

        # Changing field 'PrivateSuperOverlay.name'
        db.alter_column('layers_privatesuperoverlay', 'name', self.gf('django.db.models.fields.CharField')(max_length='255'))

        # Deleting field 'PrivateLayerList.creation_date'
        db.delete_column('layers_privatelayerlist', 'creation_date')

        # Adding field 'PrivateLayerList.date_created'
        db.add_column('layers_privatelayerlist', 'date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.date(2011, 2, 9), blank=True), keep_default=False)

        # Adding field 'PrivateLayerList.date_modified'
        db.add_column('layers_privatelayerlist', 'date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.date(2011, 2, 9), blank=True), keep_default=False)

        # Adding field 'PrivateLayerList.content_type'
        db.add_column('layers_privatelayerlist', 'content_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='layers_privatelayerlist_related', null=True, to=orm['contenttypes.ContentType']), keep_default=False)

        # Adding field 'PrivateLayerList.object_id'
        db.add_column('layers_privatelayerlist', 'object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True), keep_default=False)

        # Changing field 'PrivateLayerList.name'
        db.alter_column('layers_privatelayerlist', 'name', self.gf('django.db.models.fields.CharField')(max_length='255'))


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'PrivateSuperOverlay.creation_date'
        raise RuntimeError("Cannot reverse this migration. 'PrivateSuperOverlay.creation_date' and its values cannot be restored.")

        # Deleting field 'PrivateSuperOverlay.date_created'
        db.delete_column('layers_privatesuperoverlay', 'date_created')

        # Deleting field 'PrivateSuperOverlay.date_modified'
        db.delete_column('layers_privatesuperoverlay', 'date_modified')

        # Deleting field 'PrivateSuperOverlay.content_type'
        db.delete_column('layers_privatesuperoverlay', 'content_type_id')

        # Deleting field 'PrivateSuperOverlay.object_id'
        db.delete_column('layers_privatesuperoverlay', 'object_id')

        # Changing field 'PrivateSuperOverlay.base_kml'
        db.alter_column('layers_privatesuperoverlay', 'base_kml', self.gf('django.db.models.fields.FilePathField')(path='/some/non-existent/path', max_length=100, recursive=True))

        # Changing field 'PrivateSuperOverlay.name'
        db.alter_column('layers_privatesuperoverlay', 'name', self.gf('django.db.models.fields.CharField')(max_length=50))

        # User chose to not deal with backwards NULL issues for 'PrivateLayerList.creation_date'
        raise RuntimeError("Cannot reverse this migration. 'PrivateLayerList.creation_date' and its values cannot be restored.")

        # Deleting field 'PrivateLayerList.date_created'
        db.delete_column('layers_privatelayerlist', 'date_created')

        # Deleting field 'PrivateLayerList.date_modified'
        db.delete_column('layers_privatelayerlist', 'date_modified')

        # Deleting field 'PrivateLayerList.content_type'
        db.delete_column('layers_privatelayerlist', 'content_type_id')

        # Deleting field 'PrivateLayerList.object_id'
        db.delete_column('layers_privatelayerlist', 'object_id')

        # Changing field 'PrivateLayerList.name'
        db.alter_column('layers_privatelayerlist', 'name', self.gf('django.db.models.fields.CharField')(max_length=50))


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
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'layers.privatelayerlist': {
            'Meta': {'object_name': 'PrivateLayerList'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'layers_privatelayerlist_related'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kml': ('django.db.models.fields.files.FileField', [], {'max_length': '510'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'255'"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'sharing_groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'layers_privatelayerlist_related'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'layers_privatelayerlist_related'", 'to': "orm['auth.User']"})
        },
        'layers.privatesuperoverlay': {
            'Meta': {'object_name': 'PrivateSuperOverlay'},
            'base_kml': ('django.db.models.fields.FilePathField', [], {'path': "'/mnt/EBS_superoverlays/display'", 'max_length': '100', 'recursive': 'True', 'match': "'^doc.kml$'"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'layers_privatesuperoverlay_related'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'255'"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'sharing_groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'layers_privatesuperoverlay_related'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'layers_privatesuperoverlay_related'", 'to': "orm['auth.User']"})
        },
        'layers.publiclayerlist': {
            'Meta': {'object_name': 'PublicLayerList'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kml': ('django.db.models.fields.files.FileField', [], {'max_length': '510'})
        },
        'layers.userlayerlist': {
            'Meta': {'object_name': 'UserLayerList'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kml': ('django.db.models.fields.files.FileField', [], {'max_length': '510'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['layers']
