import re
import sys
import os
import time
import shutil
import subprocess
from lingcod.common.utils import get_logger
log = get_logger()

DJANGO = True
try:
    from django.conf import settings
except ImportError:
    # not in a django env
    DJANGO = False


'''
Sets up a grass environment in the current running process.  Allows grass commands
to be run in a shell environment.  Optimally grass python bindings would be used in the
future once they become more stable and full-featured

Grass is not thread-safe, see http://grass.osgeo.org/wiki/Parallel_GRASS_jobs
Because of this there can be issues with race conditions while working within
the same mapset with more than one process.  The solution is to create a new
mapset for each analysis run, copy the necessary maps into the new mapset,
run the analysis, and then remove the mapset when you're done. 

@author: Tim Welch, Ecotrust 2009
@author: Matthew Perry, Ecotrust 2011
Concepts taken from the PyWPS project.

Example usage (django): 
    g = Grass('mlpa_sc')
    result = g.run('r.info soilmoisture')

    # Django Settings:
    #    GRASS_GISBASE = '/usr/local/grass-6.4.1RC2'
    #    GRASS_GISDBASE = '/home/grass'

Example usage (outside django):
    g = Grass('mlpa_sc', gisdbase="/home/grass", gisbase="/usr/local/grass-6.4.1RC2")
    result = g.run('r.info soilmoisture')

'''


class Grass:
    '''
    If being used to load the source mapset then tmpMapset should be None or False.  
    If you're running any commands with outputs, use tmpMapset=True (autogenerates 
      tmpMapset name) or specify a unique name.
    autoclean=True/False determines if tmpMapset gets deleted at Grass.__del__()
    gisdbase and gisbase should be set in django settings or overriden with kwargs
    '''
    def __init__(self, location, srcMapset='PERMANENT', tmpMapset=True, 
                 gisdbase=None, gisbase=None, autoclean=True):
        self.autoclean = autoclean
        self.verbose = False
            
        self.location = location
        if tmpMapset == True:
            # unique name not specified, autogenerate it
            self.tmpMapset = 'tmpmapset_%s_%s' % (srcMapset, str(time.time()))
        elif tmpMapset:
            self.tmpMapset = tmpMapset
        self.srcMapset = srcMapset
        self.templateMapset = 'mm_template_mapset'
                
        if DJANGO and not gisdbase:
            self.gisdbase = settings.GRASS_GISDBASE
        else:
            self.gisdbase = gisdbase
        if DJANGO and not gisbase:
            self.gisbase = settings.GRASS_GISBASE
        else:
            self.gisbase = gisbase

        self.locationPath = os.path.join(self.gisdbase, self.location) #mlpa_nc
        self.tmpMapsetPath = os.path.join(self.locationPath, self.tmpMapset)    
        self.srcMapsetPath = os.path.join(self.locationPath, self.srcMapset) #PERMANENT   
        self.templatePath = os.path.join(self.locationPath, self.templateMapset) #mm_template_mapset

        if not tmpMapset:
            self.curMapset = srcMapset
            self.grassRcFile = os.path.join(gisdbase, "mm_grass6rc")  
            self.setupTmpGrassEnv(mktmp=False)
        else:
            self.curMapset = self.tmpMapset
            self.grassRcFile = os.path.join(self.tmpMapsetPath, "mm_grass6rc")  
            self.setupTmpGrassEnv()                                                             

        #Turn on verbose debug output  
        #self.runCmd('g.gisenv set=DEBUG=3') 

    def __del__(self):
        if self.autoclean:
            self.cleanup()

    def __repr__(self):
        if self.tmpMapset:
            return u'Grass instance at temporary mapset %s (%s)' % (self.tmpMapset, self.gisdbase)
        else:
            return u'Grass instance at permanent mapset %s' % self.srcMapsetPath

    @property
    def revision(self):
        rev = self.run('g.version -r')
        for line in rev.split("\n"):
            parts = line.split(":")
            parts = [p.strip() for p in parts]
            if parts[0].lower() == "revision":
                return int(parts[1])
        return None

    @property
    def grass_tmp(self):
        try:
            return settings.GRASS_TMP
        except:
            return '/tmp'

    @property
    def grass_path(self):
        try:
            return settings.GRASS_PATH
        except:
            return '%(GRASS)s/bin:%(GRASS)s/scripts:/usr/local/sbin:/usr/local/bin:' \
                   '/usr/sbin:/usr/bin:/sbin:/bin' % {'GRASS': self.gisbase}

    @property
    def grass_version(self):
        try:
            return settings.GRASS_VERSION
        except:
            try:
                return self.gisbase.split('-')[1].replace('/','')
            except:
                return "6.4.1"

    @property
    def grass_lib_path(self):
        try:
            return settings.GRASS_LIB_PATH
        except:
            return '%s/lib' % self.gisbase

    '''
    Setup grass environment to use a temporary mapset as the current mapset.
    Base maps can be used from the src mapset as it will be in your
    mapset path, but results will go to the temporary mapset.     
    grassenv settings are system specific. To get these values start a 
    grass shell and echo the environment variables to get the necessary 
    values.  eg.  >grass64 ; >echo $GISBASE
    '''
    def setupTmpGrassEnv(self, mktmp=True):
        grassenv = {
            'HOME' : self.grass_tmp,
            'PATH' : self.grass_path,
            'GRASS_VERSION' : self.grass_version,
            'GISBASE': self.gisbase,
            'LD_LIBRARY_PATH' : self.grass_lib_path,                        
            'LOCATION_NAME' : self.location,
            'MAPSET' : self.srcMapset,
            'GISDBASE' : self.gisdbase,
            'GRASS_GUI' : 'text',
            'GIS_LOCK' : str(os.getpid()),
            'GISRC' : self.grassRcFile        
        }
        
        for key in grassenv.keys():
            self.setEnv(key, grassenv[key])

        #Create temporary space for current analysis run
        if mktmp:
            self.createTempMapset()     
        #Change to the directory with the RC file      
        os.chdir(self.locationPath)        
        #Output a new rc file, overwriting any old ones
        self.writeGrassRc()                    
        return grassenv

    '''
    Create a temporary mapset
    '''
    def createTempMapset(self):
        if not os.path.exists(self.tmpMapsetPath):
            if os.path.exists(self.templatePath):
                # use template mapset directory if available
                shutil.copytree(self.templatePath, self.tmpMapsetPath)
            else:
                # .. otherwise create the bare minimum file structure
                os.mkdir(self.tmpMapsetPath)
                shutil.copyfile(
                        os.path.join(self.srcMapsetPath, 'DEFAULT_WIND'),
                        os.path.join(self.tmpMapsetPath, 'DEFAULT_WIND'))
                shutil.copyfile(
                        os.path.join(self.srcMapsetPath, 'WIND'),
                        os.path.join(self.tmpMapsetPath, 'WIND'))
                myname = open(os.path.join(self.tmpMapsetPath, 'MYNAME'),'w')
                myname.write(self.tmpMapset)
                myname.close()

    '''
    Cleanup disk such as temporary mapset
    '''
    def cleanup(self):
        if self.tmpMapset:
            shutil.rmtree(self.tmpMapsetPath)

    '''
    Output grassrc file used by Grass.  Set to use the current mapset
    '''
    def writeGrassRc(self):
        gisrc = open(self.grassRcFile,"w")
        gisrc.write("LOCATION_NAME: %s\n" % (self.location))
        gisrc.write("MAPSET: %s\n" % (self.curMapset))
        gisrc.write("DIGITIZER: none\n")
        gisrc.write("GISDBASE: %s\n" % (self.gisdbase))
        gisrc.write("OVERWRITE: 1\n")
        gisrc.write("GRASS_GUI: text\n")
        gisrc.close()        
        os.environ['GISRC'] = self.grassRcFile        
            
    '''
    Set a single environment variable to the given value
    '''
    def setEnv(self, key,value):
        origValue = os.getenv(key)
        #if origValue:
        #    value  += ":"+origValue
        os.putenv(key,value)
        os.environ[key] = value
        return
    
    '''
    Returns the raster path for the current mapset
    '''
    def getRastPath(self):
        return self.gisdbase+self.location+'/'+self.curMapset+'/cell/'        
    
    def run(self, cmd, nice=None):
        if nice:
            cmd = 'nice -n %d %s' % (nice,cmd)
        if self.verbose:
            log.debug(cmd)
        proc = subprocess.Popen(cmd, shell=True,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    env=self.setupTmpGrassEnv(),)
        out, err = proc.communicate()
        returncode = proc.returncode
        
        if returncode != 0:
            raise Exception("\nCommand failed with return code %s: \n %s \n %s" % (returncode, cmd, err))
        elif err and self.verbose:
            log.debug(err)
        return out    
         
    ############ Shortcut Commands ############
    
    '''
    Copy a vector map from the base mapset to the temporary mapset
    '''
    def copyMap(self, type, mapName):
        command = "g.copy %s=%s@%s,%s" % (type, mapName, self.srcMapset, mapName)
        self.run(command)
    
    '''
    Input a vector ogr datasource (input) and save as a grass vector map (output) 
    '''
    def v_in_ogr(self, input, output):
        command = 'v.in.ogr -o dsn=%s output=%s' % (input, output)
        self.run(command)

    '''
    Input a raster ogr datasource (input) and save as a grass raster map (output) 
    '''
    def r_in_gdal(self, input, output):
        command = 'r.in.gdal -o input=%s output=%s' % (input, output)
        self.run(command)
    
    '''
    Calculates the sum of all cell values where input is the map name
    '''
    def r_sum(self, input):
        value = 0.0
        valueResult = self.run('r.sum '+input)
        valueList = re.split('SUM = ', valueResult)
        if len(valueList) > 0:
            value = float(valueList[1])
            return value
        else:
            return None

    '''
    Calculate the area of a given raster (positive value cells) where input is the name
    of the map layer and cell_size is the width of each square cell in the raster
    '''
    def r_area(self, input, cell_size):
        #Change all value cells to 1 for counting
        maskCmd = 'r.mapcalc "maskMap=if(%s, 1)"' % (input)
        self.run(maskCmd, nice=1)
        
        #Calculate total fishing area
        area = 0.0
        cells = 0
        areaResult = self.run('r.sum maskMap')
        areaList = re.split('SUM = ', areaResult)
        if len(areaList) > 0:
            cells = float(areaList[1])
            area = self.__areaOfCells(cells, cell_size)
            return (cells, area)
        else:
            return None        

    '''
    Intersect raster map m1 with m2, storing the cell value of m2 in the resulting raster
    '''
    def r_intersect(self, result, m1, m2):
        intersectCmd = 'r.mapcalc "%s=if(%s,%s)"' % (result, m1, m2)
        self.run(intersectCmd, nice=1)
    
    '''
    Converts vMap a vector map, to rMap a raster map.  Where vectors overlap, raster cells
    are given the value of val
    '''
    def v_to_r(self, vMap, rMap, val):
        command = 'v.to.rast use=val value=%s in=%s out=%s' % (val, vMap, rMap)
        self.run(command, nice=1)        

    '''
    Calculates area where numCells is the number of square cells composing the area
    and cell_size is the width of the square cell
    '''
    def __areaOfCells(self, numCells, cell_size):
        return numCells * (cell_size * cell_size)

    '''
    Removes a grass map layer where type is the layer type 'vect' or 'rast' and layers
    is the name of the map layer
    '''
    def g_remove(self, type, layer):
        command = 'g.remove %s=%s' % (type,layer)
        self.run(command)

    '''
    returns a dict of available raster and vector datasets as a python list
    '''
    def list(self):
        cmd = 'g.mlist type=rast'
        rasts = self.run(cmd)
        cmd = 'g.mlist type=vect'
        vects = self.run(cmd)
        return {'rast': rasts.split(), 'vect': vects.split()}

