#!/usr/bin/env python
# encoding: utf-8
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
