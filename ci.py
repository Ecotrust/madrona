#!/usr/bin/env python
# encoding: utf-8
"""
ci.py

"""

import sys
import os
from optparse import OptionParser

usage = "usage: %prog -d PATH | --docs-output=PATH"
parser = OptionParser(usage)
parser.add_option('-d', '--docs-output', dest='docs_output', metavar='PATH',
                help="Where you would like the generated documentation to be moved.")
                  
(options, args) = parser.parse_args()

# Add working directory to the module search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print options.docs_output
print "Generating documentation..."
os.system('cd docs; make clean; make html')
if options.docs_output:
    os.system('rm -rf %s/*' % (options.docs_output, ))
    os.system('cp -r docs/.build/html/* %s/' % (options.docs_output, ))

# Remove settings_local if it exists
try:
    os.remove('example_projects/simple/settings_local.py')
except:
    pass

f = open('example_projects/simple/settings_local.py', 'w')
template = open('example_projects/simple/settings_local.template')
f.write(template.read())

f.write("""
TEST_RUNNER='xmlrunner.extra.djangotestrunner.run_tests'
TEST_OUTPUT_DESCRIPTIONS=True
DEBUG=False
""")

f.close()
template.close()

# Add paths of example projects
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/example_projects/simple')

from example_projects.simple import settings as project_settings

from django.core.management import setup_environ
setup_environ(project_settings)

from django.core import management
management.call_command('test')