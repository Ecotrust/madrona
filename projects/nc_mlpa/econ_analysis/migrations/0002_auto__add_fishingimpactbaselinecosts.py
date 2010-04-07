# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'FishingImpactBaselineCosts'
        db.create_table('econ_analysis_fishingimpactbaselinecosts', (
            ('gross_revenue', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('actual_costs', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('percentage_costs', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('species', self.gf('django.db.models.fields.TextField')()),
            ('net_revenue', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('crew', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('fuel', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('fixed', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('econ_analysis', ['FishingImpactBaselineCosts'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'FishingImpactBaselineCosts'
        db.delete_table('econ_analysis_fishingimpactbaselinecosts')
    
    
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
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'econ_analysis.fishingimpactanalysismap': {
            'Meta': {'object_name': 'FishingImpactAnalysisMap'},
            'allowed_targets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mlpa.AllowedTarget']", 'null': 'True', 'blank': 'True'}),
            'allowed_uses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mlpa.AllowedUse']", 'null': 'True', 'blank': 'True'}),
            'cell_size': ('django.db.models.fields.IntegerField', [], {}),
            'group_abbr': ('django.db.models.fields.TextField', [], {}),
            'group_name': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port_abbr': ('django.db.models.fields.TextField', [], {}),
            'port_name': ('django.db.models.fields.TextField', [], {}),
            'species_abbr': ('django.db.models.fields.TextField', [], {}),
            'species_name': ('django.db.models.fields.TextField', [], {})
        },
        'econ_analysis.fishingimpactbaselinecosts': {
            'Meta': {'object_name': 'FishingImpactBaselineCosts'},
            'actual_costs': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'crew': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'fixed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'fuel': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'gross_revenue': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'net_revenue': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'percentage_costs': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.TextField', [], {})
        },
        'econ_analysis.fishingimpactresults': {
            'Meta': {'object_name': 'FishingImpactResults'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mpa': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlpa.MlpaMpa']"}),
            'perc_area': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'perc_value': ('django.db.models.fields.FloatField', [], {}),
            'port': ('django.db.models.fields.TextField', [], {}),
            'species': ('django.db.models.fields.TextField', [], {})
        },
        'econ_analysis.fishingimpactstats': {
            'Meta': {'object_name': 'FishingImpactStats'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['econ_analysis.FishingImpactAnalysisMap']", 'unique': 'True'}),
            'srArea': ('django.db.models.fields.FloatField', [], {}),
            'srCells': ('django.db.models.fields.IntegerField', [], {}),
            'srValue': ('django.db.models.fields.FloatField', [], {}),
            'totalArea': ('django.db.models.fields.FloatField', [], {}),
            'totalCells': ('django.db.models.fields.IntegerField', [], {}),
            'totalValue': ('django.db.models.fields.FloatField', [], {})
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
    
    complete_apps = ['econ_analysis']
