from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
import os

class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--ext', action='store', dest='ext', default=None,
            help="Extension to be used for rasters in folder."),
        make_option('--dirpath', action='store', dest='dirpath',
            help="Denotes directory location."),
        make_option('--filepath', action='store', dest='filepath',
            help="Denotes file location."),
        make_option('--storepath', action='store', dest='storepath',
            help="Denotes alternate directory path."),
        make_option('--name', action='store', dest='name', default=None,
            help="Name given to raster dataset (only used for --filepath uploads)."),
        make_option('--type', action='store', dest='type', default='continuous',
            help="Type assigned to raster dataset (used for both --filepath and --dirpath uploads)."),
        make_option('--force', action='store_true', dest='force', default=False,
            help="Force raster dataset upload even if filepath does not exist."),
        make_option('--prefix', action='store', dest='prefix', default='',
            help="String that is prepended to the name field of each rasterdataset found in the directory path."),
    )
    help = """Populates the raster_stats_rasterdataset model with rasters

    Use the --dirpath with --ext option when providing a directory of rasters
    
        python manage.py update_rasterdatasets --dirpath path_to_rasters/raster_dir --ext .tif
        
    Use -ext grid when using ESRI Grid raster types
        
        python manage.py update_rasterdatasets --dirpath path_to_rasters/raster_dir --ext grid 
        
    Use the --filepath option (without the --ext option) when providing a path to a single file
        
        python manage.py update_rasterdatasets --filepath path_to_rasters/raster_dir/my_raster.tif
        
    The --force option can be used with the --filepath option for times when the filepath does not actually exist on your system
    
        python manage.py update_rasterdatasets --filepath path_to_rasters/raster_dir/my_raster.tif --force 
        
    Use the --name option with the --filepath option to provide a name value to the RasterDataset
    
        python manage.py update_rasterdatasets --filepath path_to_rasters/raster_dir/my_raster.tif --name "my favorite raster"
        
    Use the --type option with either the --filepath or the --dirpath options to denote raster type (default is 'continuous')
    
        python manage.py update_rasterdatasets --filepath path_to_rasters/raster_dir/my_raster.tif --name "my favorite raster" --type "continuous"
        
    The --storepath option can be used as an alternative filepath value.  Generally used with --dirpath, the value of this option will be joined with the filenames to create new filepaths used when creating the RasterDataset
    
        python manage.py update_rasterdatasets --dirpath path_to_rasters/raster_dir --ext .tif --storepath server_path/raster_dir
    
    The --prefix option can be used in conjunction with --dirpath to prepend a string to the raster names
    
        python manage.py update_rasterdatasets --dirpath path_to_rasters/raster_dir --ext .tif --prefix my_
    
    NOTE:  The RasterDataset model expects absolute paths.  Absolute paths will be stored regardless of whether filepath or dirpath is absolute or relative.
    NOTE:  This function is not recursive, it loads only rasters found in the immediate directory 
    
    """
    args = '[ext, dirpath, filepath, name, type, force, storepath, prefix]'
    
    def handle(self, **options):
        from lingcod.raster_stats.models import RasterDataset
        ext = options.get('ext')
        dirpath = options.get('dirpath')
        filepath = options.get('filepath')
        name = options.get('name')
        type = options.get('type')
        force = options.get('force')
        storepath = options.get('storepath')
        prefix = options.get('prefix')
        print 
        print
        try:
            if filepath:
                if name is None:
                    path, filename = os.path.split(filepath)
                    name = filename
                if os.path.exists(filepath) or force:
                    if storepath:
                        path = os.path.join(storepath, name)
                    else:
                        path = os.path.join(filepath, name)
                    abspath = os.path.abspath(path)
                    RasterDataset.objects.create(name=prefix+name, filepath=abspath, type=type)
                else:
                    print 'Filepath: %s does not exist' %filepath
                    raise
            elif dirpath:
                if ext is None:
                    print "The --ext option is required for --dirpath uploads."
                    raise
                if not os.path.exists(dirpath):
                    print 'Dirpath: %s does not exist' %dirpath
                    raise
                for content in os.listdir(dirpath):
                    if ext == 'grid':
                        filepath = os.path.join(dirpath, content)
                        if os.path.isdir(filepath):
                            if 'log' in os.listdir(filepath) and any('.adf' in filename for filename in os.listdir(filepath)):
                                name = content
                                if storepath:
                                    path = os.path.join(storepath, name)
                                else:
                                    path = os.path.join(filepath)
                                abspath = os.path.abspath(path)
                                RasterDataset.objects.create(name=prefix+name, filepath=abspath, type=type)
                    else:
                        root, file_extension = os.path.splitext(content)
                        if file_extension == ext or file_extension.replace('.','') == ext:
                            name = content
                            if storepath:
                                path = os.path.join(storepath, name)
                            else:
                                path = os.path.join(dirpath, name)
                            abspath = os.path.abspath(path)
                            RasterDataset.objects.create(name=prefix+name, filepath=abspath, type=type)
            else:
                print "Either --filepath or --dirpath is required."
                raise
                
        except Exception as inst:
            print 'No rasterdatasets were loaded.'