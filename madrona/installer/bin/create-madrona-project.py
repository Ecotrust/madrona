#!/usr/bin/env python
from django.core import management
from random import choice
import sys
import os
import shutil
import re
from distutils.dir_util import copy_tree
import optparse
import psycopg2
import madrona

def replace_file(infile, outfile, search_replace, remove=True):
    infh = open(infile, 'r')
    outfh = open(outfile, 'w')
    for line in infh:
        out = line
        for s, r in search_replace.iteritems():
            out = out.replace(s,r)
        outfh.write(out)
    infh.close()
    outfh.close()
    if remove:
        os.remove(infile)

def check_db_connection(conn_string):
    print "Connecting to database\n ->%s" % (conn_string)
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute("SELECT PostGIS_Version();")
        records = cursor.fetchone()
        print "Connected! (postgis version ", records[0], ")\n"
        return True
    except psycopg2.ProgrammingError:
        sys.exit("""Database does not have postgis installed
        Try http://postgis.refractions.net/documentation/manual-svn/postgis_installation.html#create_new_db
        """)
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
    conn.close()
    return True

def parse_conn(conn_string):
    d = {'host': 'localhost',
        'password': '',
        'dbname': '',
        'user': 'postgres',
        'port': '5432'}
    for p in conn_string.split(" "):
        k,v = p.split("=")
        d[k] = v.replace("'","")
    return (d['host'], d['password'], d['dbname'], d['user'], d['port'])

def main():
    parser = optparse.OptionParser(
            usage="create-madrona-project.py [options] -p <project> -a <app> -d <project.examle.com>")
    parser.add_option('-p', '--project', help='Name of django project', action='store', 
            dest='project_name', type='string')
    parser.add_option('-a', '--app', help='Name of django application', action='store', 
            dest='app_name', type='string')
    parser.add_option('-d', '--domain', help='Full domain name of server', action='store', 
            dest='domain', type='string')
    parser.add_option('-c', '--connection', help='Full connection string to existing postgis db', action='store', 
            dest='conn_string', type='string')
    parser.add_option('-o', '--outdir', help='Output/destination directory (default = ".")', action='store', 
            dest='dest_dir', type='string', default='.')
    parser.add_option('-s', '--srid', help='Database spatial reference ID (default = 3857)', action='store', 
            dest='dbsrid', type='string', default='3857')
    (opts, args) = parser.parse_args()

    if not opts.project_name:
        parser.print_help()
        parser.error("Please specify the project name")
    if not opts.app_name:
        parser.print_help()
        parser.error("Please specify the app name")
    if not opts.domain:
        parser.print_help()
        parser.error("Please specify the full domain name")
    if not opts.conn_string:
        parser.print_help()
        parser.error("Please specify the full database connection string. \nex:\n   -c \"host='localhost' dbname='my_database' user='my_user' password='secret'\"")

    check_db_connection(opts.conn_string)
    source_dir = os.path.join(os.path.dirname(madrona.__file__),'installer','files')
    dest_dir = os.path.abspath(opts.dest_dir)
    print " * copy template from %s to %s" % (source_dir, dest_dir)
    copy_tree(source_dir,dest_dir)

    print " * Rename project and app files"
    old_project_dir = os.path.join(dest_dir, '_project')
    project_dir = os.path.join(dest_dir, opts.project_name)
    os.rename(old_project_dir, project_dir)

    old_app_dir = os.path.join(project_dir, '_app')
    app_dir = os.path.join(project_dir, opts.app_name)
    os.rename(old_app_dir, app_dir)

    print " * Adjust settings"
    infile = os.path.join(project_dir, '_settings.py')
    outfile = os.path.join(project_dir, 'settings.py')
    search_replace = {
            '_project': opts.project_name,
            '_app': opts.app_name,
            '_srid': opts.dbsrid
    }
    replace_file(infile, outfile, search_replace)

    print " * Generating secret key"
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = ''.join([choice(chars) for i in range(50)])
    lsfh = open(os.path.join(project_dir, 'settings_local.py'),'w')
    lsfh.write("""
SECRET_KEY = '%s'
""" % secret_key)
    lsfh.close()

    print " * Adjust deployment files, etc."
    infile = os.path.join(dest_dir, 'deploy', 'vhost.apache')
    outfile = os.path.join(dest_dir, 'deploy', opts.domain + "-apache")
    search_replace = {
            '_project': opts.project_name,
            '_domain': opts.domain,
            '_root': dest_dir
    }
    replace_file(infile, outfile, search_replace)

    infile = os.path.join(dest_dir, 'deploy', 'vhost.nginx')
    outfile = os.path.join(dest_dir, 'deploy', opts.domain + "-nginx")
    search_replace = {
            '_project': opts.project_name,
            '_domain': opts.domain,
            '_root': dest_dir
    }
    replace_file(infile, outfile, search_replace)

    # gitignore
    infile = os.path.join(dest_dir, '_.gitignore')
    outfile = os.path.join(dest_dir, '.gitignore')
    search_replace = {'_project': opts.project_name}
    replace_file(infile, outfile, search_replace)

    # wsgi
    infile = os.path.join(dest_dir, 'deploy', '_wsgi.py')
    outfile = os.path.join(dest_dir, 'deploy', 'wsgi.py')
    import sys
    vi = sys.version_info
    try:
        major = vi.major
        minor = vi.minor
    except AttributeError:
        major = vi[0]
        minor = vi[1]

    pyver = '%d.%d' % (major, minor) 
    search_replace = {
            '_project': opts.project_name,
            '_pyversion': pyver,
            '_root': dest_dir
    }
    replace_file(infile, outfile, search_replace)

    # db settings
    lsfh = open(os.path.join(project_dir, 'settings_local.py'),'a')
    host, passwd, name, user, port = parse_conn(opts.conn_string)
    lsfh.write("""
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'PORT': '%s',
        'HOST': '%s',
        'PASSWORD': '%s',
        'NAME': '%s',
        'USER': '%s',
    }
}
""" % (port, host, passwd, name, user))

    # while we're at it, write more stuff out
    lsfh.write("""
LOG_FILE = "%s"
# The following Google key is for localhost:
####### CHANGE ME !!!!!!!!!
GOOGLE_API_KEY = 'R$3jifj)(#jf,m.eapnisivwmaz2gDhT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSLaQmJjJuOq03hTEjc-cNV8eegYg'

MEDIA_ROOT = '%s/mediaroot/'
MEDIA_URL = 'http://%s/media/'
STATIC_URL = 'http://%s/media/'
""" % (os.path.join(dest_dir, 'logs', 'app.log'),
       dest_dir, opts.domain, opts.domain))

    lsfh.close()

    os.chdir(opts.project_name)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    old_sys_path = sys.path
    sys.path = [project_dir]
    sys.path.extend(old_sys_path)
    import settings

    print " * syncing database"
    management.execute_manager(settings, ['manage.py','syncdb'])

    print " * migrating data models"
    management.execute_manager(settings, ['manage.py','migrate'])

    print " * installing media"
    management.execute_manager(settings, ['manage.py','install_media'])

    print " * enabling sharing "
    management.execute_manager(settings, ['manage.py','enable_sharing'])

    print " * site setup "
    management.execute_manager(settings, ['manage.py','site',opts.domain])

    print " * installing cleangeometry"
    management.execute_manager(settings, ['manage.py','install_cleangeometry'])

    print """
******************************
SUCCESS

Next steps:

    1. set permissions on mediaroot
        sudo chgrp -R www-data ./mediaroot && sudo chmod -R 775 ./mediaroot
    
    2. Deploy 
        sudo cp ./deploy/%s-apache /etc/apache2/sites-available && sudo a2ensite %s-apache

    3. Check the site into git or other version control system
    
    4. Run tests 
        sudo manage.py test
""" % (opts.domain, opts.domain)

if __name__ == "__main__":
    main()
