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
    from lingcod.common.management.commands.install_media import Command as InstallMediaCommand
    command = InstallMediaCommand()
    # RUNNING COMMANDS CAUSES WIERD SETTINGS STUFF
    # The solution is a horrible, horrible hack
    # We're forced to reimplement the install_media command
    # ALL these cause subsequent management commands to fail:
    #
    # command.execute()
    # execute_manager(settings,['manage.py','install_media'])
    # execute_from_command_line(['manage.py','install_media'])
    # call_command('install_media')
    #
    command.dry_run = False
    command.media_root = settings.MEDIA_ROOT
    command.force_compress = True

    lingcod_media_dir = command.get_lingcod_dir()
    project_media_dir = command.get_project_dir()

    if os.path.abspath(os.path.realpath(lingcod_media_dir)) == os.path.abspath(os.path.realpath(command.media_root)) or \
        os.path.abspath(os.path.realpath(project_media_dir)) == os.path.abspath(os.path.realpath(command.media_root)):
        raise Exception("Your MEDIA_ROOT setting has to be a directory other than your lingcod or project media folder!")

    command.copy_media_to_root(lingcod_media_dir)
    command.copy_media_to_root(project_media_dir)
    # Cant call synccompress so can't do command.compile_media()
    manage_path = os.path.join(pdir,'manage.py')
    res = os.popen("python %s synccompress" % manage_path).read() 
    print res

    print "Executing from command line"
    #execute_from_command_line(['manage.py','test','array','--failfast','-v','2'])
    #execute_from_command_line(['manage.py','test','raster_stats'])
    execute_from_command_line(['manage.py','test'])

hdir = os.path.dirname(os.path.abspath(__file__))
pdir = os.path.join(hdir,'example_projects/test_project')
spdir = os.path.join(hdir,'example_projects')
sys.path.insert(0, pdir)
sys.path.insert(0, spdir)
sys.path.insert(0, hdir)
#os.chdir(pdir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' # test_project.settings

settings.TEST_RUNNER='xmlrunner.extra.djangotestrunner.run_tests'
settings.TEST_OUTPUT_DESCRIPTIONS=True
settings.DEBUG=True
settings.POSTGIS_TEMPLATE='template1'

use_exec(pdir)
