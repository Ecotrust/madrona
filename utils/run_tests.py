#!/usr/bin/env python
# encoding: utf-8
"""
ANY sane programmer who looks at this script will have a serious case of the WTFs
It is ugly. It reaches into dark corners of django testing madness that no human should
be exposed to. 

TL;DR; This is what we're *trying* to do

    set sys.paths
    set some settings
    call the install_media command to collect static files into one place
    construct a test command with select apps 
    run the tests

This shouldn't be too hard right? Wrong.

RUNNING MANAGEMENT COMMANDS CAUSES WIERD STUFF
ALL these management commands cause subsequent tests to fail
due to breaking setttings, database sessions and other crazy stuff
completely unrelated to the code:

    command.execute()
    execute_manager(settings,['manage.py','install_media'])
    execute_from_command_line(['manage.py','install_media'])
    call_command('install_media')

The solution is a horrible, horrible hack
We're forced to reimplement the install_media command 'by hand'
and avoid using all handy managment commands at all costs.

This is a hideous beast but make no mistake ... it is fragile! 
Attempts to fix this script have been made and none of them have succeeded.
When it comes down to it, we just don't want to spend our time struggling with a 
broken test runner; we'd rather test our code in an ugly but reliable way.
"""
import sys
import os
from django.core.management import call_command, execute_manager, execute_from_command_line
from django.conf import settings

def use_exec(pdir):
    """
    instead, employ the technique used by django.core.management.execute_manager()
    """
    print "Installing media"

    from madrona.common.management.commands.install_media import Command as InstallMediaCommand
    command = InstallMediaCommand()
    command.dry_run = False
    command.media_root = settings.MEDIA_ROOT
    command.force_compress = True

    madrona_media_dir = command.get_madrona_dir()
    project_media_dir = command.get_project_dir()

    if os.path.abspath(os.path.realpath(madrona_media_dir)) == os.path.abspath(os.path.realpath(command.media_root)) or \
        os.path.abspath(os.path.realpath(project_media_dir)) == os.path.abspath(os.path.realpath(command.media_root)):
        raise Exception("Your MEDIA_ROOT setting has to be a directory other than your madrona or project media folder!")

    command.copy_media_to_root(madrona_media_dir)
    command.copy_media_to_root(project_media_dir)
    # Cant call synccompress so can't do command.compile_media()
    manage_path = os.path.join(pdir,'manage.py')
    res = os.popen("python %s synccompress" % manage_path).read() 
    print res

    print "Executing from command line"
    
    if len(sys.argv) > 1:
        print
        print "   manage.py test %s --noinput --failfast -v 2" % sys.argv[1]
        print
        execute_from_command_line(['manage.py','test',sys.argv[1],'--noinput','--failfast','-v','2'])
    else:
        cmd_dict = create_test_cmd()
        print
        print ' '.join(cmd_dict)
        print
        execute_from_command_line(cmd_dict)

def create_test_cmd():
    base = ['manage.py','test','--noinput','-v','2']
    cmd_dict = base
    for app in settings.INSTALLED_APPS:
        try:
            if not app in settings.EXCLUDE_FROM_TESTS:
                cmd_dict.append(app.split(".")[-1])
        except:
            cmd_dict = base
            break
    return cmd_dict

hdir = os.path.dirname(os.path.abspath(__file__))
pdir = os.path.join(hdir,'..','examples/test_project')
spdir = os.path.join(hdir,'..','examples')
sys.path.insert(0, pdir)
sys.path.insert(0, spdir)
sys.path.insert(0, hdir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'

settings.TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
settings.TEST_OUTPUT_VERBOSE = True
settings.DEBUG = True
import logging
settings.LOG_LEVEL = logging.WARNING
settings.MEDIA_URL = '/media/'
settings.POSTGIS_TEMPLATE = 'template1'

use_exec(pdir)
