# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.core.management import call_command

class Migration(DataMigration):
    
    def forwards(self, orm):
        call_command('loaddata', 'youtube_screencasts.json')

    def backwards(self, orm):
        pass
    
