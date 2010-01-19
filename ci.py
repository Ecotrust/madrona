#!/usr/bin/env python
# encoding: utf-8
"""
ci.py

"""

import sys
import os
from optparse import OptionParser

usage = "usage: %prog -j PATH -d PATH | --docs-output=PATH"
parser = OptionParser(usage)
parser.add_option('-d', '--docs-output', dest='docs_output', metavar='PATH',
                help="Where you would like the generated documentation to be moved.")

parser.add_option('-j', '--jar-path', dest='jar', metavar='PATH',
                help="Location of the jsdoc toolkit jar")
                  
(options, args) = parser.parse_args()

# Add working directory to the module search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print options.docs_output
print "Generating documentation..."
os.system('cd docs; make clean; make html')
if options.docs_output:
    os.system('rm -rf %s/*' % (options.docs_output, ))
    os.system('cp -r docs/.build/html/* %s/' % (options.docs_output, ))

    if options.jar:
        print "Generating javascript documentation"
        c = 'java -jar %s/jsrun.jar %s/app/run.js -a -t=%s/templates/jsdoc media/common/js -r=10 -d=%s/jsdocs' % (options.jar, options.jar, options.jar, options.docs_output, )
        print c
        os.system(c)
    

# Remove settings_local if it exists
try:
    # os.remove('example_projects/simple/settings_local.py')
    os.remove('projects/nc_mlpa/settings_local.py')    
except:
    pass

# f = open('example_projects/simple/settings_local.py', 'w')
# template = open('example_projects/simple/settings_local.template')
f = open('projects/nc_mlpa/settings_local.py', 'w')
template = open('projects/nc_mlpa/settings_local.template')

f.write(template.read())

f.write("""
TEST_RUNNER='xmlrunner.extra.djangotestrunner.run_tests'
TEST_OUTPUT_DESCRIPTIONS=True
DEBUG=False
POSTGIS_TEMPLATE='template1'
""")

f.close()
template.close()

# Add paths of example projects
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/example_projects/simple')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/projects/nc_mlpa')
os.environ['DJANGO_SETTINGS_MODULE'] = 'projects.nc_mlpa.settings'
# from example_projects.simple import settings as project_settings
# from projects.nc_mlpa import settings as project_settings

from django.conf import settings
# from django.core.management import setup_environ
# setup_environ(settings)

from django.core import management
print "Running tests"
management.call_command('test', interactive=False)