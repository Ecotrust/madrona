from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
import os
import sys
import glob
import shutil
try:
    set
except NameError:
    from sets import Set as set # Python 2.3 fallback


class Command(BaseCommand):
    media_dirs = ['media']
    ignore_apps = ['django.contrib.admin']
    exclude = ['CVS', '.*', '*~']
    option_list = BaseCommand.option_list + (
        make_option('--media-root', default=settings.MEDIA_ROOT, dest='media_root', metavar='DIR',
            help="Specifies the root directory in which to collect media files."),
        make_option('-n', '--dry-run', action='store_true', dest='dry_run',
            help="Do everything except modify the filesystem."),
        make_option('-d', '--dir', action='append', default=media_dirs, dest='media_dirs', metavar='NAME',
            help="Specifies the name of the media directory to look for in each app."),
        make_option('-e', '--exclude', action='append', default=exclude, dest='exclude', metavar='PATTERNS',
            help="A space-delimited list of glob-style patterns to ignore. Use multiple times to add more."),
        make_option('-l', '--link', action='store_true', dest='link',
            help="Create a symbolic link to each file instead of copying.")
        )
    help = 'Collect media files into a single media directory.'
    
    def handle(self, *app_labels, **options):
        self.dry_run = options.get('dry_run', False)
        self.media_root = options.get('media_root', settings.MEDIA_ROOT)

        lingcod_media_dir = self.get_lingcod_dir()
        project_media_dir = self.get_project_dir()

        if self.dry_run:
            print "    DRY RUN! NO FILES WILL BE MODIFIED."

        self.copy_media_to_root(lingcod_media_dir)
        self.copy_media_to_root(project_media_dir)
    
        self.compile_media()

        self.remove_uncompressed_media()

        self.publish_media()

    def get_lingcod_dir(self):
        # We know lingcod/../media is relative to this file
        lingcod_media_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','..','media'))
        return lingcod_media_dir

    def get_project_dir(self):
        # We know project media is relative to the root_urlconf 
        from django.utils import importlib
        m = importlib.import_module(settings.ROOT_URLCONF)
        return os.path.realpath(os.path.join(os.path.dirname(m.__file__), '..', 'media'))

    def copy_media_to_root(self, source_dir):
        if self.dry_run:
            print "    This would copy %s to %s" % (source_dir, self.media_root)
            return

        print "    Copying %s to %s" % (source_dir, self.media_root)
        from distutils.dir_util import copy_tree
        copy_tree(source_dir, self.media_root)

        return
    
    def compile_media(self):
        if self.dry_run:
            print "    This would compile all the media assets in %s" % (self.media_root)
            return

        print "    Compiling media (not yet implemented)"
        return

    def remove_uncompressed_media(self):
        if self.dry_run:
            print "    This would remove the media assets that were alredy compiled/compressed"
            return

        print "    Removing uncompressed media (not yet implemented)"
        return
       
    def publish_media(self):
        if self.dry_run:
            print "    This would publish all the media in %s" % (self.media_root)
            return

        print "    Publishing media (not yet implemented)"
        return

