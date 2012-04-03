#!/usr/bin/env python
"""
Credits to Dane Springmeyer for this one (https://github.com/springmeyer)

Initial Steps
-------------
 * create ~./pypirc file with pypi user:pass
 * register package with: 'python setup.py register'

Release Steps
-------------
 * # Edit CHANGELOG.txt
 * # Increment 'VERSION' in madrona/version.py 
 * git commit
 * python deploy.py # to create sdist, upload, and create tag
 * git push --tags
"""

import sys
import time
from subprocess import call as subcall

app = 'madrona'
version = __import__(app).get_version()
debug = False

def call(cmd): 
  print " * ", cmd
  if debug:
      return
  try:
    response = subcall(cmd,shell=True)
    print
    time.sleep(1)
    if response < 0:
      sys.exit(response)
  except OSError, E:
    sys.exit(E)

def cleanup():
    call('sudo rm -rf *.egg* *.pyc dist/ build/')

def tag():
    call('git tag -a %s -m "tagging the %s release"' % (version,version))

def upload():
    call('python setup.py sdist upload')

def main():
    cleanup()
    tag()
    upload()
    cleanup()
    
if __name__ == '__main__':
    main()
