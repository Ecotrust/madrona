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
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, cwd)

print options.docs_output
print "Generating documentation..."
os.system('cd %s; make clean; make html' % os.path.join(cwd,'..','docs'))
print "Pylint..."
os.system('pylint -f html madrona > %s' % os.path.join(cwd,'..','docs','.build','html','pylint.html'))
if options.docs_output:
    src = os.path.join(cwd,'..','docs','.build','html','*')
    os.system('cp -r %s %s' % (src ,options.docs_output, ))
    print "Docs copied to %s" % options.docs_output

    if options.jar:
        print "Generating javascript documentation"
        c = 'java -jar %s/jsrun.jar %s/app/run.js -a -t=%s/templates/jsdoc media/common/js -r=10 -d=%s/jsdocs' % (options.jar, options.jar, options.jar, options.docs_output, )
        print c
        os.system(c)
