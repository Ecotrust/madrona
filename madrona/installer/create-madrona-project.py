#!/usr/bin/env python
from django.core import management
from random import choice
import sys
import os
import shutil
import re
from distutils.dir_util import copy_tree
import optparse


def main():
    parser = optparse.OptionParser()
    parser.add_option('-d', '--dest', help='Destination directory', action='store', 
            dest='dest_dir', type='string', default='.')
    parser.add_option('-p', '--project', help='Name of django project', action='store', 
            dest='project_name', type='string')
    parser.add_option('-a', '--app', help='Name of django application', action='store', 
            dest='app_name', type='string')
    parser.add_option('-s', '--srid', help='Database spatial reference ID', action='store', 
            dest='dbsrid', type='string', default='3857')
    (opts, args) = parser.parse_args()

    if not opts.project_name:
        print "Please specify the project name\nexample:\n   python %s -p myproject" % sys.argv[0]
        exit(-1)
    if not opts.app_name:
        print "Please specify the app name\nexample:\n   python %s -a myapp" % sys.argv[0]
        exit(-1)

    source_dir = os.path.join(os.path.dirname(__file__),'files')
    dest_dir = os.path.abspath(opts.dest_dir)
    print " Step 1 of 4: copy template from %s to %s" % (source_dir, dest_dir)
    copy_tree(source_dir,dest_dir)

    print " Step 2 of 4: Rename project and app files"
    old_project_dir = os.path.join(dest_dir, '_project')
    project_dir = os.path.join(dest_dir, opts.project_name)
    os.rename(old_project_dir, project_dir)

    old_app_dir = os.path.join(project_dir, '_app')
    app_dir = os.path.join(project_dir, opts.app_name)
    os.rename(old_app_dir, app_dir)

    print " Step 3 of 4: Adjust settings"
    infh = open( os.path.join(project_dir, '_settings.py'), 'r')
    outfh = open( os.path.join(project_dir, 'settings.py'), 'w')
    search_replace = {
            '_project': opts.project_name,
            '_app': opts.app_name,
            '_srid': opts.dbsrid
    }
    for line in infh:
        out = line
        for s, r in search_replace.iteritems():
            out = out.replace(s,r)
        outfh.write(out)
    infh.close()
    outfh.close()
    os.remove(os.path.join(project_dir, '_settings.py'))

    print "Generating secret key"
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = ''.join([choice(chars) for i in range(50)])
    lsfh = open(os.path.join(project_dir, 'settings_local.py'),'w+')
    lsfh.write("""
SECRET_KEY = '%s'
""" % secret_key)
    lsfh.close()

    print " Step 4 of 4: Adjust deployment files, etc."

if __name__ == "__main__":
    main()
