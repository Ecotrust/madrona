#!/usr/bin/env python
from django.core import management
from django.template.defaultfilters import slugify
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

def append_to_file(infile, outfile, search_replace):
    infh = open(infile, 'r')
    outfh = open(outfile, 'a')
    for line in infh:
        out = line
        for s, r in search_replace.iteritems():
            out = out.replace(s,r)
        outfh.write(out)
    infh.close()
    outfh.close()

def camel_case(s, sep=' '):
    tl = []
    for t in s.split(sep):
        tl.append(t.title())
    return ''.join(tl)

def add_feature(ftype, name, app_slug, app_dir, all_features_list=None):
    class_name = camel_case(name)
    if ftype == 'folder':
        if not all_features_list:
            all_features_list = [name]
        all_features = ','.join(["('%s.models.%s')" % (app_slug, camel_case(f)) for f in all_features_list])
    else:
        all_features = ''

    search_replace = {
            '{{app}}': app_slug,
            '{{all_features}}': all_features,
            '{{model}}': class_name,
    }
    # Add to models
    infile = os.path.join(app_dir, "base", "_"+ftype+".models.py")
    outfile = os.path.join(app_dir, 'models.py')
    append_to_file(infile, outfile, search_replace)
    # Add to forms
    infile = os.path.join(app_dir, "base", "_"+ftype+".forms.py")
    outfile = os.path.join(app_dir, 'forms.py')
    append_to_file(infile, outfile, search_replace)
    # Add show template
    infile = os.path.join(app_dir, "base", "_"+ftype+".show.html")
    outdir = os.path.join(app_dir, '..', 'templates', slugify(class_name))
    os.makedirs(outdir)
    outfile = os.path.join(outdir, 'show.html')
    replace_file(infile, outfile, search_replace, remove=False)

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
    for p in conn_string.strip().split(" "):
        k,v = p.split("=")
        d[k] = v.replace("'","")
    return (d['host'], d['password'], d['dbname'], d['user'], d['port'])

def main():
    parser = optparse.OptionParser(
            usage="""create-madrona-project.py [options] -p <project> -a <app> -d <project.examle.com> -c <postgres_connection>
            
  Example:
    create-madrona-project.py \\
        --project "My Project" \\
        --app testapp \\
        --domain "192.168.1.111:8080" \\
        --connection "dbname='example' user='postgres' " \\
        --studyregion "SRID=4326;POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))" \\
        --aoi "My Areas"  \\
        --aoi "My Other Areas"  \\
        --poi "Points of interest"  \\
        --loi "Pipelines"  \\
        --folder "Folder for Areas"  \\
        --kml "Global Marine|http://ebm.nceas.ucsb.edu/GlobalMarine/kml/marine_model.kml" """)
    parser.add_option('-p', '--project', help='Name of django project', action='store', 
            dest='project_name', type='string')
    parser.add_option('-a', '--app', help='Name of django application', action='store', 
            dest='app_name', type='string')
    parser.add_option('-d', '--domain', help='Full domain name of server', action='store', 
            dest='domain', type='string')
    parser.add_option('-c', '--connection', help='Full connection string to existing postgis db', action='store', 
            dest='conn_string', type='string')

    # Optional
    parser.add_option('-o', '--outdir', help='Output/destination directory (default = "./<project_name>/")', action='store', 
            dest='dest_dir', type='string', default='')
    parser.add_option('-s', '--srid', help='Database spatial reference ID (default = 3857)', action='store', 
            dest='dbsrid', type='string', default='3857')
    parser.add_option('-r', '--studyregion', help='Study region shape (ewkt string or path to shapefile)', action='store', 
            dest='studyregion', type='string', default=None)
    parser.add_option('-w', '--folder', help="Folder", action='append',
            dest='folders', type='string', default=[])
    parser.add_option('-x', '--aoi', help="Area/Polygon Feature", action='append', 
            dest="aois", type='string', default=[])
    parser.add_option('-y', '--loi', help="Line Feature", action='append', 
            dest="lois", type='string', default=[])
    parser.add_option('-z', '--poi', help="Point Feature", action='append', 
            dest="pois", type='string', default=[])
    parser.add_option('-k', '--kml', help="KML URL", action='append', 
            dest="kmls", type='string')
    parser.add_option('-u', '--superuser', help="create default superuser (madrona/madrona) ... NOT SECURE! ", action='store_true', 
            dest="superuser", default=False)
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
    
    # Features
    aois = opts.aois
    lois = opts.lois
    pois = opts.pois
    folders = opts.folders

    # Some default features if nothing was specified
    if not aois and not lois and not pois:
        aois = ['Area of Interest']
    if not opts.folders:
        folders = ['Folder']

    studyregion = opts.studyregion
    if studyregion:
        # write to initial_data as a madrona.studyregion model?
        pass

    kmls = opts.kmls
    if not kmls:
        kmls = ["Global Marine|http://ebm.nceas.ucsb.edu/GlobalMarine/kml/marine_model.kml",]

    project_slug = slugify(opts.project_name).replace('-', '')
    app_slug = slugify(opts.app_name).replace('-','')
    check_db_connection(opts.conn_string)
    source_dir = os.path.join(os.path.dirname(madrona.__file__),'installer','files')
    if opts.dest_dir == '':
        dest_dir = os.path.abspath(os.path.join('.', project_slug))
    else:
        dest_dir = os.path.abspath(opts.dest_dir)

    if os.path.exists(dest_dir):
        raise Exception("%s already exists." % dest_dir)

    print " * copy template from %s to %s" % (source_dir, dest_dir)
    copy_tree(source_dir, dest_dir)

    print " * creating public KML doc"
    outkml = os.path.join(dest_dir, 'media', 'layers', 'uploaded-kml', 'public.kml')
    fh = open(outkml,'w')
    fh.write("""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
    <Document>
        <name>Base KML Data</name>
        <visibility>0</visibility>
        <open>1</open>
    """)

    for kml in kmls:
        try:
            layername, url = kml.strip().split('|')
        except:
            url = kml.strip()
            from urlparse import urlparse
            from posixpath import basename
            parsed = urlparse(url)
            layername = basename(parsed.path)
            names = re.split('[ ._-]', layername)
            layername = ' '.join([x.title() for x in names if x.lower() not in ['kml','kmz']])
            print layername

        link = """
        <NetworkLink id="%s">
            <name>%s</name>
            <visibility>0</visibility>
            <Link>
            <href>%s</href>
            </Link>
        </NetworkLink>
        """ % (slugify(layername), layername, url)
        fh.write(link)

    fh.write("""</Document></kml>""")
    fh.close()

    print " * Rename project and app files"
    old_project_dir = os.path.join(dest_dir, '_project')
    project_dir = os.path.join(dest_dir, project_slug)
    os.rename(old_project_dir, project_dir)

    old_app_dir = os.path.join(project_dir, '_app')
    app_dir = os.path.join(project_dir, app_slug)
    os.rename(old_app_dir, app_dir)

    print " * Adjust forms.py and models.py"
    all_features_list = []
    for aoi in aois:
        add_feature('aoi', aoi, app_slug, app_dir)
        all_features_list.append(aoi)
    for loi in lois:
        add_feature('loi', loi, app_slug, app_dir)
        all_features_list.append(loi)
    for poi in pois:
        add_feature('poi', poi, app_slug, app_dir)
        all_features_list.append(poi)

    for folder in folders:
        all_features_list.append(folder)
        add_feature('folder', folder, app_slug, app_dir, all_features_list)

    print " * Adjust settings"
    infile = os.path.join(project_dir, '_settings.py')
    outfile = os.path.join(project_dir, 'settings.py')
    search_replace = {
            '{{project}}': opts.project_name,
            '{{project_slug}}': project_slug,
            '{{app}}': app_slug,
            '{{srid}}': opts.dbsrid
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
            '{{project}}': opts.project_name,
            '{{project_slug}}': project_slug,
            '{{domain}}': opts.domain,
            '{{root}}': dest_dir
    }
    replace_file(infile, outfile, search_replace)

    infile = os.path.join(dest_dir, 'deploy', 'vhost.nginx')
    outfile = os.path.join(dest_dir, 'deploy', opts.domain + "-nginx")
    search_replace = {
            '{{project}}': opts.project_name,
            '{{project_slug}}': project_slug,
            '{{domain}}': opts.domain,
            '{{root}}': dest_dir
    }
    replace_file(infile, outfile, search_replace)

    # gitignore
    infile = os.path.join(dest_dir, '_.gitignore')
    outfile = os.path.join(dest_dir, '.gitignore')
    search_replace = {
            '{{project}}': opts.project_name,
            '{{project_slug}}': project_slug,
    }
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
            '{{project}}': opts.project_name,
            '{{project_slug}}': project_slug,
            '{{pyversion}}': pyver,
            '{{root}}': dest_dir
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

    os.chdir(dest_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    old_sys_path = sys.path
    sys.path = [project_dir]
    sys.path.extend(old_sys_path)
    import settings

    print " * syncing database"
    syncdb = ['manage.py','syncdb','--noinput']
    management.execute_manager(settings, syncdb)

    print " * migrating data models"
    management.execute_manager(settings, ['manage.py','migrate'])
    # run again to get initial_data.json loaded
    management.execute_manager(settings, syncdb)

    print " * creating superuser"
    if opts.superuser:
        management.execute_manager(settings, ['manage.py','createsuperuser',
            '--username=madrona', '--email=madrona@ecotrust.org', '--noinput'])
        from django.contrib.auth.models import User
        m_user = User.objects.get(username="madrona")
        m_user.set_password('madrona')
        m_user.save()

        # have to have a user to post a news item
        from madrona.news.models import Entry, Tag
        t = Tag.objects.create(name="Welcome")
        t.save()
        title = "Welcome to " + opts.project_name[:38] # stay under 50 char
        e = Entry.objects.create(title=title, 
            body="""This application was automatically created by the 
        Madrona App Generator (see <code>create-madrona-app.py</code>). 
        If you're an adminstrator of the site and would like to customize it, 
        please see the <a href='http://ecotrust.github.com/madrona/docs/tutorial.html' 
        target='_blank'>tutorial</a>.""", 
            author=m_user)
        e.tags.add(t)
        e.save()

    print " * installing media"
    management.execute_manager(settings, ['manage.py','install_media'])

    print " * enabling sharing "
    management.execute_manager(settings, ['manage.py','enable_sharing'])

    print " * site setup "
    management.execute_manager(settings, ['manage.py','site', opts.domain])

    print " * installing cleangeometry"
    management.execute_manager(settings, ['manage.py','install_cleangeometry'])

    print " * installing studyregion"
    if opts.studyregion:
        management.execute_manager(settings, ['manage.py','create_study_region', opts.studyregion, '--name', opts.app_name])

    try:
        port = int(opts.domain.split(':')[-1])
    except:
        port = 80

    
    print """
******************************
SUCCESS
    cd %s/%s
    python manage.py runserver 0.0.0.0:%d
""" % (project_slug, project_slug, port)

    if opts.superuser:
        print "    # Note that a django superuser was created with user/pass of madrona/madrona"
    else:
        print "    # You also need to create a user to log in initially\n    python manage.py createsuperuser --username=<USER> --email=<EMAIL>"

if __name__ == "__main__":
    main()
