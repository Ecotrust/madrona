# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'PickledGraph'
        db.create_table('spacing_pickledgraph', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pickled_graph', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('spacing', ['PickledGraph'])

        # Adding model 'Land'
        db.create_table('spacing_land', (
            ('geometry', self.gf('django.contrib.gis.db.models.fields.PolygonField')(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('spacing', ['Land'])

        # Adding model 'SpacingPoint'
        db.create_table('spacing_spacingpoint', (
            ('geometry', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=settings.GEOMETRY_DB_SRID)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('spacing', ['SpacingPoint'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'PickledGraph'
        db.delete_table('spacing_pickledgraph')

        # Deleting model 'Land'
        db.delete_table('spacing_land')

        # Deleting model 'SpacingPoint'
        db.delete_table('spacing_spacingpoint')
    
    
    models = {
        'spacing.land': {
            'Meta': {'object_name': 'Land'},
            'geometry': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': str(settings.GEOMETRY_DB_SRID), 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'spacing.pickledgraph': {
            'Meta': {'object_name': 'PickledGraph'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pickled_graph': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'spacing.spacingpoint': {
            'Meta': {'object_name': 'SpacingPoint'},
            'geometry': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': str(settings.GEOMETRY_DB_SRID)}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['spacing']
