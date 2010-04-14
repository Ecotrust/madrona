import random
import os
import datetime
import re    
import tempfile
from nc_mlpa import settings
from grass import Grass
import utilities as mmutil  
from models import *
from nc_mlpa.mlpa.models import *
from Layers import *
#from Layers import Layers

'''
Used to calculate summary statistics of a given mpa's impact on localized fishing
interests.  Uses grass to perform the calculations on Layers.  Much of the overall 
and study region level statistics are precalculated and stored in the database 
using the FishingImpactStats model.  Mpa level statistics are calculated at run-time.
'''
class Analysis:
    def __init__(self):
        self.SQ_MILES_IN_SQ_METER = 0.000000386102159
        self.SIG_DIGITS = 3
        #location under GRASS_ROOT to store grass mapsets
        self.MM_GRASS_LOCATION = 'mlpa_nc'
        #mapset under location for grass map layers
        self.MM_SRC_GRASS_MAPSET = 'PERMANENT'    
        # Source for fishing impact layers used by Grass for analysis.  
        self.FISHING_IMPACT_ANALYSIS_ROOT = settings.GIS_DATA_ROOT + 'analysis/'

        #Temporary names for intermediate grass analysis.  Can be reused each run.
        self.srMapName = 'studyRegion'               
        self.mpaVectorMapName = 'mpaVectorMap'          # mpa vector
        self.mpaRasterMapName = 'mpaRasterMap'          # mpa raster       
        self.srValueMaskMapName = 'srValueMaskMap'      # fishing value within study region 
        self.mpaValueMaskMapName = 'mpaValueMaskMap'    # fishing value within mpa
                
        self.grass = None        

    def setupGrass(self, temp_id=None):
        self.MM_DST_GRASS_MAPSET = temp_id
        grass = Grass(settings.GRASS_ROOT, self.MM_GRASS_LOCATION, self.MM_SRC_GRASS_MAPSET, self.MM_DST_GRASS_MAPSET)        
        self.MM_GRASS_RAST_PATH = grass.getRastPath()
        return grass                
    
       
    '''
    Driver for preloading and precalculating grass map layers and 
    overall/study region summary statistics.  This is invoked via
    the manage.py command defined in the management directory of
    this module
    '''    
    def preload(self):                      
        #Setup grass to use the base mapset, we're going to load it        
        self.grass = self.setupGrass()     
        self.__preloadStudyRegion()
        layers_list = GetAllLayers()
        for layer in layers_list:
            map = self.__preloadDb(layer)
            self.__preloadGrassMap(map)
            self.__preloadMapStats(map)

    '''
    Preload information about fishing impact map into DB
    '''
    def __preloadDb(self, layer):
        #Check for existing record
        maps = FishingImpactAnalysisMap.objects.filter(
            group_name=layer.group_name, 
            port_name=layer.port_name,
            species_name=layer.species_name
        )
        
        #If record already exists, update it
        if len(maps) > 0:
            map = maps[0]
            map.group_name = layer.group_name
            map.group_abbr = layer.group_abbr
            map.port_name = layer.port_name
            map.port_abbr = layer.port_abbr
            map.species_name = layer.species_name
            map.species_abbr = layer.species_abbr
            map.cell_size = layer.cell_size
            map.save()  
        #Otherwise create a new record                 
        else:
            map = FishingImpactAnalysisMap(
                group_name=layer.group_name,
                group_abbr=layer.group_abbr,
                port_name=layer.port_name,
                port_abbr=layer.port_abbr,
                species_name=layer.species_name,
                species_abbr=layer.species_abbr,
                cell_size=layer.cell_size 
            )
            map.save()   
            
        #Add Allowed Targets to AnalysisMap
        targets = layer.target_names
        for target in targets:
            allowed_target = AllowedTarget.objects.filter(name=target)
            if len(allowed_target) > 0:
                map.allowed_targets.add(allowed_target[0])
        map.save()
        
        #Map the new AnalysisMap to one or more allowed uses
        #Filter by fishing type
        allowed_uses = AllowedUse.objects.filter(
            purpose__name=layer.fishing_type
        )
        
        #Get methods for current species
        methods = layer.take_methods
        species_name = layer.species_name
                
        #Add Allowed Uses to AnalysisMap
        for method_name in methods:
            uses = allowed_uses.filter(method__name=method_name, target__name=species_name)
            for use in uses:
                map.allowed_uses.add(use)
            map.save() 
            
        return map       

    '''
    Load study region from DB into grass.
    '''
    def __preloadStudyRegion(self):
        #Output study region to shapefile 
        srPath = self.__srToShapefile()
        #Convert shapefile to grass vector map            
        self.grass.v_in_ogr(srPath, self.srMapName)
        #Convert study vector map to raster map
        self.grass.v_to_r(self.srMapName, self.srMapName, 1)          

    '''
    Preload a fishing impact map into grass for later use in analysis
    '''    
    def __preloadGrassMap(self, map):
        #Build path to fishing impact grids
        mapPath = self.FISHING_IMPACT_ANALYSIS_ROOT+map.group_abbr+'/'
        #Get name of current grid
        mapName = map.getFullName()
        #Getpath to grass raster map
        grassRasterPath = os.path.join(self.MM_GRASS_RAST_PATH,mapName)
        #Load fishing impact grid into Grass for later use
        if not os.path.exists(grassRasterPath):  
            self.grass.r_in_gdal(mapPath+map.getGridName(), mapName)   

    '''        
    Precalculates overall and study region level statistics and stores them in the database.               
    '''
    def __preloadMapStats(self, map):
        self.fishingMapName = map.getFullName()       # fishing value map            
        
        #Total fishing value.  Sums cell values in fishing map
        totalValue = self.grass.r_sum(self.fishingMapName)
        if totalValue is None:
            return None

        #Fishing value in study region.  Intersects fishing map with study regions and
        #sums remaining cells.
        self.grass.r_intersect(self.srValueMaskMapName, self.srMapName, self.fishingMapName)
        srValue = self.grass.r_sum(self.srValueMaskMapName)
        if srValue is None:
            return None

        # Total fishing area.  Makes all nonzero cells 1 and sums the values getting
        # the number of cells.  Use cell size to get area.
        (totalCells, totalArea) = self.grass.r_area(self.fishingMapName, map.cell_size)
        totalArea = totalArea * self.SQ_MILES_IN_SQ_METER
        
        # Fishing area in study area.  Uses previous fishing map intersected to study 
        # region, makes all nonzero cells 1 and sums the values getting number of cells.
        # Use cell size to get area.
        (srCells, srArea) = self.grass.r_area(self.srValueMaskMapName, map.cell_size)
        srArea = srArea * self.SQ_MILES_IN_SQ_METER
        
        # Create a new stats record.  If one already exists, update it.
        stats = FishingImpactStats.objects.filter(map__group_name=map.group_name, 
                                                  map__port_name=map.port_name,
                                                  map__species_name=map.species_name)
        
        #If record already exists, update it
        if len(stats) > 0:
            fi = stats[0]
            fi.totalCells=totalCells
            fi.srCells=srCells
            fi.totalArea=totalArea
            fi.srArea=srArea
            fi.totalValue=totalValue
            fi.srValue=srValue
            fi.save()  
        #Otherwise create a new record                 
        else:
            fi = FishingImpactStats(map=map,
                                    totalCells=totalCells,
                                    srCells=srCells,
                                    totalArea=totalArea,
                                    srArea=srArea,
                                    totalValue=totalValue,
                                    srValue=srValue)
            fi.save()                

    def __get_tmpMapsetName(self, mpa):
        timestamp = datetime.datetime.now().strftime('%m_%d_%y_%H%M')       
        temp_id = 'mpa'+str(mpa.id)+'_user'+str(mpa.user_id)+'_'+timestamp+'_'+str(mmutil.getRandInt())
        return temp_id
     
    def __generate_mpaRasterMap(self, mpa, tmpMapsetName):
        shapepath = self.__mpaToTempShapefile(mpa.id, tmpMapsetName)                                           
        #Convert shapefile to grass vector map
        mpaVectorName = self.mpaVectorMapName+str(mpa.id)
        self.grass.v_in_ogr(shapepath, mpaVectorName)
        #######################################################################################
        #import time
        #time.sleep(5)
        #required for whatever reason in order to produce correct results on my windows machine
        #NOT NEEDED on aws servers 
        #######################################################################################
        #Convert mpa vector map to raster map
        mpaRasterName = self.mpaRasterMapName+str(mpa.id)
        self.grass.v_to_r(mpaVectorName, mpaRasterName, 1)    
        return mpaRasterName
     
    '''
    Fishing impact analysis driver.  
    '''
    def run(self, mpa, layers):                        
        analResults = []
        #create unique mapset(?) name for this mpa
        tmpMapsetName = self.__get_tmpMapsetName(mpa)
        #add this mapset to grass
        self.grass = self.setupGrass(tmpMapsetName)  
        #Generate mpa raster map
        mpaRasterName = self.__generate_mpaRasterMap(mpa, tmpMapsetName)
        
        #run analysis on each layer/map/species
        for layer in layers:    
            #how to handle error type return values from __runAnal (-1, -2 values)
            analResult = self.__runAnal(mpa, layer, mpaRasterName)
            analResults.append(analResult)
        
        self.__removeTempShapefile(tmpMapsetName)
        self.grass.cleanup()
        
        return analResults  
             
    '''
    Performs a single grass analysis run.  Assumes that the source mapset has been
    preloaded with all of the necessary map layers for analysis.  Don't run this
    directly.  Use the analysis driver named 'run' and 
    
    Returns -1 if failed to retrieve precomputed overall and study region statistics
    Returns -2 if mpa analysis failed.
    '''
    def __runAnal(self, mpa, map, mpaRasterName):   
        self.fishingMapName = map.getFullName()       # fishing value map                            
        self.grass.copyMap('rast', self.fishingMapName)
        
        #Get precomputed map statistics
        stats = FishingImpactStats.objects.filter(map=map)
        if len(stats) < 1:
            return -1
        else:
            stats = stats[0]                            
         
        setPercsToZero = False
        #Get list of targets from map
        map_targets = map.allowed_targets.all()
        map_purpose = Layers.FISHING_TYPES[map.group_abbr]
        for map_target in map_targets:
            if len(mpa.allowed_uses.filter(target__name=map_target, purpose__name=map_purpose)) != 0:
                setPercsToZero = True
        
        #If there is an allowed use for this fishery, then no intersect is needed and resulting percentages should be 0.0
        if setPercsToZero:
            mpaPercOverallArea = 0.0
            mpaPercOverallValue = 0.0
        else:
            #Intersect mpa raster with fishing map
            self.grass.r_intersect(self.mpaValueMaskMapName, mpaRasterName, self.fishingMapName)   
            
            #Calculate percent area   
            (mpaCells, mpaArea) = self.grass.r_area(self.mpaValueMaskMapName, map.cell_size)
            mpaArea = mpaArea * self.SQ_MILES_IN_SQ_METER
            
            mpaPercOverallArea = mmutil.percentage(mpaArea,stats.totalArea)      
            
            #Calculate percent value
            mpaValue = self.grass.r_sum(self.mpaValueMaskMapName)
            if mpaValue is None:
                return -2                    
            
            mpaPercOverallValue = mmutil.percentage(mpaValue,stats.totalValue)     
      
        #Generate analysis result
        analResult = AnalysisResult(
            mpa.id,
            'mpa',
            map.group_name,
            map.port_name,
            map.species_name,
            mpaPercOverallArea,
            mpaPercOverallValue
        )
        
        return analResult        
    
    '''
    Given an mpa id and a full shapfile pathname (eg. /tmp/new_shapefile.shp)
    outputs the given mpa record to the specified file
    '''
    def __mpaToTempShapefile(self, mpa_id, temp_id):
        shp_filename = temp_id+'.shp'        
        shapepath = os.path.join(tempfile.gettempdir(),shp_filename)
        shp_query = 'select id, user_id, geometry_final from mlpa_mlpampa where id='+str(mpa_id)
        command = settings.PGSQL2SHP+" -u "+settings.DATABASE_USER+" -P '"+settings.DATABASE_PASSWORD+"' -f "+shapepath+" "+settings.DATABASE_NAME+' "'+shp_query+'"'
        os.system(command)
        return shapepath

    '''
    Outputs current study region to /tmp/study_region.shp)
    '''
    def __srToShapefile(self):
        shp_filename = 'study_region.shp' 
        shapepath = os.path.join(tempfile.gettempdir(),shp_filename)
        #the following query is specific on the server to id=4 as there are currently two Active study regions in the server-side db
        shp_query = 'select * from mm_study_region where active=TRUE'
        command = settings.PGSQL2SHP+" -u "+settings.DATABASE_USER+" -P '"+settings.DATABASE_PASSWORD+"' -f "+shapepath+" "+settings.DATABASE_NAME+' "'+shp_query+'"'
        os.system(command)
        return shapepath
    
    '''
    Removes a shape with the given name from the default temp directory 
    '''
    def __removeTempShapefile(self, name): 
        extensions = ['shp','shx','prj','dbf']
        for extension in extensions:
            filename = name+'.'+extension
            filePath = os.path.join(tempfile.gettempdir(),filename)
            if os.path.exists(filePath):
                os.remove(filePath)            
        return True         

'''
Acronyms:
    GEI - Gross Economic Impact
    GER - Gross Economic Revenue
    NEI - Net Economic Impact
    NER - Net Economic Revenue
'''        
class CommercialResultsByPort:
    def __init__(self, port, gross_impact, net_impact, species_list):
        self.port = port
        self.species_list = species_list
        self.GEI = gross_impact
        (self.GER, self.percGEI) = self.get_percentage_gross_impact()
        self.NEI = net_impact
        (self.total_costs, self.NER, self.percNEI) = self.get_percentage_net_impact()
        
    def get_percentage_gross_impact(self):
        from econ_analysis.models import CommercialGrossRevenue
        revenues = CommercialGrossRevenue.objects.filter(port__name=self.port)
        total_revenue = 0
        for rev in revenues:
            total_revenue += rev.gross_revenue
        return total_revenue, (self.GEI / total_revenue) * 100
    
    def get_percentage_net_impact(self):
        from econ_analysis.models import CommercialCosts, CommercialGrossRevenue
        total_costs = 0
        for species in self.species_list:
            revenue = CommercialGrossRevenue.objects.get(port__name=self.port, species__name=species)
            costs = CommercialCosts.objects.get(species__name=species)
            species_cost = revenue.gross_revenue * costs.percentage_costs / 100
            total_costs += species_cost
        baseline_net_revenue = self.GER - total_costs
        return total_costs, baseline_net_revenue, (self.NEI / baseline_net_revenue) * 100

'''
Acronyms:
    GEI - Gross Economic Impact
    GER - Gross Economic Revenue
    NEI - Net Economic Impact
    NER - Net Economic Revenue
'''   
class CommercialStudyRegionResults:
    def __init__(self, port_impacts):
        self.port_impacts = port_impacts
        (self.GER, self.costs, self.NER, self.GEI, self.NEI) = self.calculate_totals()
        (self.percGEI, self.percNEI) = self.calculate_percentages()
        
    def calculate_totals(self):
        GER = costs = NER = GEI = NEI = 0
        for p_impact in self.port_impacts:
            GER += p_impact.GER
            costs += p_impact.total_costs
            NER += p_impact.NER
            GEI += p_impact.GEI
            NEI += p_impact.NEI
        return GER, costs, NER, GEI, NEI
        
    def calculate_percentages(self):
        percGEI = (self.GEI / self.GER) * 100
        percNEI = (self.NEI / self.NER) * 100
        return percGEI, percNEI
  
'''
Acronyms:
    GEI - Gross Economic Impact
    GER - Gross Economic Revenue
    NEI - Net Economic Impact
    NER - Net Economic Revenue
'''         
class EmptyAnalysisResult:
    def __init__(self, group_name, port_name, species_name, type):
        self.group = group_name
        self.port = port_name
        self.species = species_name
        self.type = type
        self.percOverallArea = '---'
        self.percOverallValue = '---'
        self.percGEI = '---'
        self.percNEI = '---'
        
'''
An AnalysisResult represents the result of running the impact analysis on a single Layer

Acronyms:
    GEI - Gross Economic Impact
    GER - Gross Economic Revenue
    NEI - Net Economic Impact
    NER - Net Economic Revenue

'''
class AnalysisResult:
    def __init__(self, id=None, type=None, group=None, port=None, species=None, percOverallArea=None, percOverallValue=None):
        self.mpa_id = None
        self.array_id = None
        self.type = type
        self.group = group
        self.port = port
        self.species = species
        
        if type == 'mpa':
            self.mpa_id = id  
            self.percOverallArea = percOverallArea
            self.percOverallValue = percOverallValue    #% of total fishing value captured by mpa
        else: #must be an array 
            self.array_id = id
            self.percGEI = percOverallValue
            if self.percGEI == '---':
                self.GEI = self.percNEI = self.NEI = '---'
            else:
                from econ_analysis.models import CommercialCosts, CommercialGrossRevenue
                if group == 'Commercial':
                    try:
                        revenue = CommercialGrossRevenue.objects.get(species__name=self.species, port__name=self.port)
                    except:
                        #WHAT TO DO IF QUERY IS EMPTY???
                        self.GEI = self.percNEI = self.NEI = '---'
                        return
                    gross_revenue = revenue.gross_revenue
                    costs = CommercialCosts.objects.get(species__name=self.species)
                    #what to do if costs query is empty or errors?
                    self.GEI = gross_revenue * self.percGEI / 100
                    (self.percNEI, self.NEI) = self.calculateNEI(gross_revenue, costs)
                elif group == 'Commercial Passenger Fishing Vessel':
                    try:
                        revenue = CPFVGrossRevenue.objects.get(port__name=self.port)
                    except:
                        #WHAT TO DO IF QUERY IS EMPTY or ERRORS???
                        self.GEI = self.percNEI = self.NEI = '---'
                        return
                    gross_revenue = revenue.gross_revenue
                    costs = CPFVCosts.objects.get(port__name=self.port)                  
                    #what to do if costs query is empty or errors?
                    self.GEI = gross_revenue * self.percGEI / 100
                    (self.percNEI, self.NEI) = self.calculateNEI(gross_revenue, costs)
                else:
                    self.GEI = self.percNEI = self.NEI = '---'
        
        
    def calculateNEI(self, gross_revenue, costs):
        BGER = gross_revenue
        total_costs = BGER * costs.percentage_costs / 100
        BNER = BGER - total_costs
        Fixed = costs.fixed
        Crew = costs.crew
        Fuel = costs.fuel
        
        GEI = self.GEI
        GER = BGER - GEI
        Fixed_Costs = BGER * Fixed / 100
        Variable_Costs = GER * (Crew + Fuel) / 100
        NER = GER - Fixed_Costs - Variable_Costs
        NEI = BNER - NER
        percNEI = NEI / BNER * 100
        
        return percNEI, NEI
        
