#!/usr/bin/env python
# encoding: utf-8
import sys
import os
from django.core.management import call_command, execute_manager, execute_from_command_line


def use_exec():
    """
    instead, employ the technique used by django.core.management.execute_manager()
    """
    import settings
    print "Installing media"
    execute_manager(settings,['manage.py','install_media'])

    print "Executing from command line"
    execute_manager(settings,['manage.py','test','array','--failfast','-v','2'])
    #execute_from_command_line(['manage.py','test','--failfast','-v','2'])

hdir = os.path.dirname(os.path.abspath(__file__))
pdir = os.path.join(hdir,'example_projects/test_project')
os.chdir(pdir)
sys.path.insert(0, pdir)
#spdir = os.path.join(hdir,'example_projects')
#sys.path.insert(0, spdir)

use_exec()
sys.exit()

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.conf import settings
settings.TEST_RUNNER='xmlrunner.extra.djangotestrunner.run_tests'
settings.TEST_OUTPUT_DESCRIPTIONS=True
settings.DEBUG=True
settings.POSTGIS_TEMPLATE='template1'

print "Installing media"
#call_command('install_media')
#call_command('sqlall','staticmap')
#print "Testing"
#call_command('test', failfast=True)
