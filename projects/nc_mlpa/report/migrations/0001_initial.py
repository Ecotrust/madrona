# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'MpaShapefile'
        db.create_table('report_mpashapefile', (
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('allowed_uses', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('lop_numeric', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('mpa_id_num', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.PolygonField')(srid=3310, null=True, blank=True)),
            ('other_allowed_uses', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('mpa', self.gf('django.db.models.fields.related.OneToOneField')(related_name='mpa', unique=True, to=orm['mlpa.MlpaMpa'])),
            ('desig_acro', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('array_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('name_short', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('other_regulated_activities', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('lop', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('mpa_modification_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('area_sq_mi', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('array', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mlpa.MpaArray'], null=True, blank=True)),
            ('desig_name', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('report', ['MpaShapefile'])

        # Adding model 'StudyRegionTotal'
        db.create_table('report_studyregiontotal', (
            ('open_coast_total', self.gf('django.db.models.fields.FloatField')()),
            ('feature_mapping', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.FeatureMapping'])),
            ('estuarine_total', self.gf('django.db.models.fields.FloatField')()),
            ('org_scheme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.OrganizationScheme'])),
            ('study_region_total', self.gf('django.db.models.fields.FloatField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('report', ['StudyRegionTotal'])

        # Adding model 'Cluster'
        db.create_table('report_cluster', (
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('array', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mlpa.MpaArray'])),
            ('lop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mlpa.Lop'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bioregion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bioregions.Bioregion'], null=True, blank=True)),
        ))
        db.send_create_signal('report', ['Cluster'])

        # Adding M2M table for field mpa_set on 'Cluster'
        db.create_table('report_cluster_mpa_set', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cluster', models.ForeignKey(orm['report.cluster'], null=False)),
            ('mlpampa', models.ForeignKey(orm['mlpa.mlpampa'], null=False))
        ))
        db.create_unique('report_cluster_mpa_set', ['cluster_id', 'mlpampa_id'])

        # Adding model 'ClusterHabitatInfo'
        db.create_table('report_clusterhabitatinfo', (
            ('sort', self.gf('django.db.models.fields.FloatField')()),
            ('additional_required', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('habitat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intersection.FeatureMapping'])),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['report.Cluster'])),
            ('replicate', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('result', self.gf('django.db.models.fields.FloatField')()),
            ('units', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('report', ['ClusterHabitatInfo'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'MpaShapefile'
        db.delete_table('report_mpashapefile')

        # Deleting model 'StudyRegionTotal'
        db.delete_table('report_studyregiontotal')

        # Deleting model 'Cluster'
        db.delete_table('report_cluster')

        # Removing M2M table for field mpa_set on 'Cluster'
        db.delete_table('report_cluster_mpa_set')

        # Deleting model 'ClusterHabitatInfo'
        db.delete_table('report_clusterhabitatinfo')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'bioregions.bioregion': {
            'Meta': {'object_name': 'Bioregion'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '3310', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'intersection.featuremapping': {
            'Meta': {'object_name': 'FeatureMapping'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'feature': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['intersection.IntersectionFeature']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organization_scheme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.OrganizationScheme']"}),
            'sort': ('django.db.models.fields.FloatField', [], {})
        },
        'intersection.intersectionfeature': {
            'Meta': {'object_name': 'IntersectionFeature'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'feature_model': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multi_shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.MultiFeatureShapefile']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'native_units': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'output_units': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.SingleFeatureShapefile']", 'null': 'True'}),
            'study_region_total': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'intersection.multifeatureshapefile': {
            'Meta': {'object_name': 'MultiFeatureShapefile'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'shapefile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'intersection.organizationscheme': {
            'Meta': {'object_name': 'OrganizationScheme'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'intersection.singlefeatureshapefile': {
            'Meta': {'object_name': 'SingleFeatureShapefile'},
            'clip_to_study_region': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'parent_shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.MultiFeatureShapefile']", 'null': 'True', 'blank': 'True'}),
            'shapefile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'mlpa.allowedmethod': {
            'Meta': {'object_name': 'AllowedMethod'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'mlpa.allowedpurpose': {
            'Meta': {'object_name': 'AllowedPurpose'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'mlpa.allowedtarget': {
            'Meta': {'object_name': 'AllowedTarget'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'mlpa.alloweduse': {
            'Meta': {'object_name': 'AllowedUse'},
            'draft': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlpa.Lop']", 'null': 'True', 'blank': 'True'}),
            'method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlpa.AllowedMethod']"}),
            'purpose': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlpa.AllowedPurpose']"}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlpa.LopRule']", 'null': 'True', 'blank': 'True'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlpa.AllowedTarget']"})
        },
        'mlpa.goalcategory': {
            'Meta': {'object_name': 'GoalCategory'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'mlpa.goalobjective': {
            'Meta': {'object_name': 'GoalObjective'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'goal_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlpa.GoalCategory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'mlpa.lop': {
            'Meta': {'object_name': 'Lop'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'run': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'mlpa.loprule': {
            'Meta': {'object_name': 'LopRule'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'mlpa.mlpampa': {
            'Meta': {'object_name': 'MlpaMpa'},
            'allowed_uses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mlpa.AllowedUse']", 'null': 'True', 'blank': 'True'}),
            'boundary_description': ('django.db.models.fields.TextField', [], {'default': '\'North Boundary:  [please describe, e.g. "north latitude 36 21.0 to the extent of state waters"]\\nWest Boundary:  [please describe, e.g. "the state water boundary"]\\nSouth Boundary: [please describe, e.g. "line due west of the northern tip of Sammy\\\'s Rock: at ~33 21.029"]\\nEast Boundary:   [please describe, e.g. "mean high tide line"]\'', 'null': 'True', 'blank': 'True'}),
            'cluster_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'design_considerations': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'designation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mpa.MpaDesignation']", 'null': 'True', 'blank': 'True'}),
            'dfg_feasability_guidance': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'evolution': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geometry_final': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '3310', 'null': 'True', 'blank': 'True'}),
            'geometry_orig': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '3310', 'null': 'True', 'blank': 'True'}),
            'goal_objectives': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mlpa.GoalObjective']", 'null': 'True', 'blank': 'True'}),
            'group_before_edits': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_estuary': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'255'"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'other_allowed_uses': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'other_regulated_activities': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sat_explanation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sharing_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'specific_objective': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'mlpa.mpaarray': {
            'Meta': {'object_name': 'MpaArray'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sharing_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'supportfile1': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'supportfile2': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'mpa.mpadesignation': {
            'Meta': {'object_name': 'MpaDesignation'},
            'acronym': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'poly_fill_color': ('django.db.models.fields.CharField', [], {'default': "'ff0000ff'", 'max_length': '8'}),
            'poly_outline_color': ('django.db.models.fields.CharField', [], {'default': "'ffffffff'", 'max_length': '8'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'report.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'array': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlpa.MpaArray']"}),
            'bioregion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bioregions.Bioregion']", 'null': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlpa.Lop']"}),
            'mpa_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mlpa.MlpaMpa']"})
        },
        'report.clusterhabitatinfo': {
            'Meta': {'object_name': 'ClusterHabitatInfo'},
            'additional_required': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['report.Cluster']"}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'habitat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.FeatureMapping']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'replicate': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.FloatField', [], {}),
            'sort': ('django.db.models.fields.FloatField', [], {}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'report.mpashapefile': {
            'Meta': {'object_name': 'MpaShapefile'},
            'allowed_uses': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'area_sq_mi': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'array': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlpa.MpaArray']", 'null': 'True', 'blank': 'True'}),
            'array_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'desig_acro': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'desig_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '3310', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lop': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'lop_numeric': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mpa': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'mpa'", 'unique': 'True', 'to': "orm['mlpa.MlpaMpa']"}),
            'mpa_id_num': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mpa_modification_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_short': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'other_allowed_uses': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'other_regulated_activities': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'report.studyregiontotal': {
            'Meta': {'object_name': 'StudyRegionTotal'},
            'estuarine_total': ('django.db.models.fields.FloatField', [], {}),
            'feature_mapping': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.FeatureMapping']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'open_coast_total': ('django.db.models.fields.FloatField', [], {}),
            'org_scheme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intersection.OrganizationScheme']"}),
            'study_region_total': ('django.db.models.fields.FloatField', [], {})
        }
    }
    
    complete_apps = ['report']
