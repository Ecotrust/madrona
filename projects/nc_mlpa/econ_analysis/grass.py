import re
import sys
from socket import gethostname
import os
import shutil
import settings

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
Concepts taken from the PyWPS project.

Example usage: Grass('/home/you/GRASSROOT','mlpa_sc','PERMANENT', 'name_of_unique_tmp_mapset')
'''
class Grass:
    '''
    If being used to load the source mapset then tmpMapset should be None.  Otherwise
    it's assumed you're going to run some commands.  In that case  
    srcMapset should already exist and be preloaded with all of the necessary map
    layers for analysis.  tmpMapset should be a unique name since multiple analysis
    runs may be executing at the same time.
    '''
    def __init__(self, gisdbase, location, srcMapset, tmpMapset=None):
        self.gisdbase = gisdbase
        self.location = location
        self.srcMapset = srcMapset
        self.tmpMapset = tmpMapset
        self.templateMapset = 'mm_template_mapset'
                
        self.locationPath = os.path.join(gisdbase,location)
        self.srcMapsetPath = os.path.join(self.locationPath,srcMapset)
        self.templatePath = os.path.join(self.locationPath,self.templateMapset)
        self.grassRcFile = os.path.join(gisdbase,"mm_grass6rc")  

        if tmpMapset is None:
            self.curMapset = srcMapset
            self.setupSrcGrassEnv()
        else:
            self.curMapset = tmpMapset
            self.tmpMapsetPath = os.path.join(self.locationPath,tmpMapset)                        
            self.setupTmpGrassEnv()                                                             

        #Turn on verbose debug output  
        #self.runCmd('g.gisenv set=DEBUG=3') 

    '''
    Setup grass environment to use the base mapset as the current mapset.   
    grassenv settings are system specific. To get these values start a 
    grass shell and echo the environment variables to get the necessary 
    values.  eg.  >grass64 ; >echo $GISBASE
    '''
    def setupSrcGrassEnv(self):
        grassenv = {
            'HOME' : settings.GRASS_TMP,
            'PATH' : settings.GRASS_PATH,
            'GRASS_VERSION' : settings.GRASS_VERSION,
            'GISBASE': settings.GRASS_GISBASE,
            'LD_LIBRARY_PATH' : settings.GRASS_LIB_PATH,                        
            'LOCATION_NAME' : self.location,
            'MAPSET' : self.srcMapset,
            'GISDBASE' : self.gisdbase,
            'GRASS_GUI' : 'text',
            'GIS_LOCK' : str(os.getpid())
        }
        
        for key in grassenv.keys():
            self.setEnv(key, grassenv[key])

        os.chdir(self.locationPath)
        self.writeGrassRc() 
        
    '''
    Setup grass environment to use a temporary mapset as the current mapset.
    Base maps can be used from the src mapset as it will be in your
    mapset path, but results will go to the temporary mapset.     
    grassenv settings are system specific. To get these values start a 
    grass shell and echo the environment variables to get the necessary 
    values.  eg.  >grass64 ; >echo $GISBASE
    '''
    def setupTmpGrassEnv(self):
        grassenv = {
            'HOME' : settings.GRASS_TMP,
            'PATH' : settings.GRASS_PATH,
            'GRASS_VERSION' : settings.GRASS_VERSION,
            'GISBASE': settings.GRASS_GISBASE,
            'LD_LIBRARY_PATH' : settings.GRASS_LIB_PATH,
            'LOCATION_NAME' : self.location,
            'MAPSET' : self.tmpMapset,
            'GISDBASE' : self.gisdbase,
            'GRASS_GUI' : 'text',
            'GIS_LOCK' : str(os.getpid())
        }
        
        for key in grassenv.keys():
            self.setEnv(key, grassenv[key])

        #Create temporary space for current analysis run
        self.createTempMapset()     
        #Change to the directory with the RC file      
        os.chdir(self.locationPath)        
        #Output a new rc file, overwriting any old ones
        self.writeGrassRc()                    

    '''
    Create a temporary mapset
    '''
    def createTempMapset(self):
        #Copy mapset template
        if not os.path.exists(self.tmpMapsetPath):
            shutil.copytree(self.templatePath, self.tmpMapsetPath)

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
    
    '''
    Runs grass command.  
    Example usage: runCmd('r.los in=elevation.dem out=los coord=10,10')
    '''
    def runCmd(self, cmd, showOutput=False):
        result = None
        try:
            import os
            if showOutput:
                print "Running Grass Command: %s" %cmd
                os.system(cmd)
            else:
                result = os.popen(cmd).read()
        except Exception,e :
            raise Exception("Could not perform command [%s]: %s" % (cmd,e))
        return result     
         
    ############ Shortcut Commands ############
    
    '''
    Copy a vector map from the base mapset to the temporary mapset
    '''
    def copyMap(self, type, mapName):
        #command = "g.copy %s='%s@%s',%s" % (type, mapName, self.srcMapset, mapName)
        command = "g.copy %s=%s@%s,%s" % (type, mapName, self.srcMapset, mapName)
        self.runCmd(command)
    
    '''
    Input a vector ogr datasource (input) and save as a grass vector map (output) 
    '''
    def v_in_ogr(self, input, output):
        command = 'v.in.ogr -o dsn=%s output=%s --overwrite' % (input, output)
        self.runCmd(command)

    '''
    Input a raster ogr datasource (input) and save as a grass raster map (output) 
    '''
    def r_in_gdal(self, input, output):
        command = 'r.in.gdal -o input=%s output=%s --overwrite' % (input, output)
        self.runCmd(command)
    
    '''
    Calculates the sum of all cell values where input is the map name
    '''
    def r_sum(self, input):
        value = 0.0
        valueResult = self.runCmd('r.sum '+input)
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
        self.runCmd(maskCmd)
        
        #Calculate total fishing area
        area = 0.0
        cells = 0
        areaResult = self.runCmd('r.sum maskMap')
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
        self.runCmd(intersectCmd)
    
    '''
    Converts vMap a vector map, to rMap a raster map.  Where vectors overlap, raster cells
    are given the value of val
    '''
    def v_to_r(self, vMap, rMap, val):
        command = 'v.to.rast use=val value=%s in=%s out=%s --overwrite' % (val, vMap, rMap)
        self.runCmd(command)        

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
        self.runCmd(command)
