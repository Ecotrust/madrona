#!/usr/bin/env python
# encoding: utf-8
import sys
import os
from django.core.management import call_command, execute_manager, execute_from_command_line
from django.conf import settings

def use_exec(pdir):
    """
    instead, employ the technique used by django.core.management.execute_manager()
    """
    #import settings
    print "Installing media"
    # RUNNING MANAGEMENT COMMANDS CAUSES WIERD SETTINGS STUFF IN TESTS
    # ALL these cause subsequent manage.py test commands to fail:
    #
    # command.execute()
    # execute_manager(settings,['manage.py','install_media'])
    # execute_from_command_line(['manage.py','install_media'])
    # call_command('install_media')
    #
    # So we have to call install_media from the shell
    manage_path = os.path.join(pdir,'manage.py')
    res = os.popen("python %s install_media" % manage_path).read() 
    print res

    print "Executing tests from command line"
    #execute_from_command_line(['manage.py','test','array','--failfast','-v','2'])
    execute_from_command_line(['manage.py','test'])

hdir = os.path.dirname(os.path.abspath(__file__))
pdir = os.path.join(hdir,'example_projects/test_project')
spdir = os.path.join(hdir,'example_projects')
sys.path.insert(0, pdir)
sys.path.insert(0, spdir)
#os.chdir(pdir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'

settings.TEST_RUNNER='xmlrunner.extra.djangotestrunner.run_tests'
settings.TEST_OUTPUT_DESCRIPTIONS=True
settings.DEBUG=True
settings.POSTGIS_TEMPLATE='template1'

use_exec(pdir)
