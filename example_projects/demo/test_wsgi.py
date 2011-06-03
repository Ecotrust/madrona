#!/usr/bin/env python
import sys
import os

sys.stdout = sys.stderr

# Project specific 
sys.path.append('/usr/local/src/marinemap/example_projects')
sys.path.append('/usr/local/src/marinemap/example_projects/test_project')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
