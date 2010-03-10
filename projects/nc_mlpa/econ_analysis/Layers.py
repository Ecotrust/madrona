import os
import settings

class Layers:
    def __init__(self):
        self.CELL_SIZE = 250
        
    def getAllLayers(self):
        #might want to move dictionaries to __init__
        #might be able to simply capitalize the values for better display
        groups = {'com': 'Commercial', 'cpfv': 'Commercial Passenger Fishing Vessel', 'div': 'Recreational Dive', 'kyk': 'Recreational Kayak', 'pvt': 'Recreational Private Vessel', 'swd': 'Edible Seaweed'}
        fishing_types = {'com': 'commercial', 'cpfv': 'recreational', 'div': 'recreational', 'kyk': 'recreational', 'pvt': 'recreational', 'swd': 'commercial'}
        ports = {'all': 'Entire Study Region', 'ab': 'Albion', 'cc': 'Crescent City', 'ek': 'Eureka', 'el': 'Elk', 'fb': 'Fort Bragg', 'sc': 'Shelter Cove', 'td': 'Trinidad'}
        species_display = {'abal': 'Abalone', 'achv': 'Anchovies', 'chal': 'California Halibut', 'dcrab': 'Dungeness crab', 'dcrabt': 'Dungeness crab', 'eswd': 'All Edible Seaweed Species', 'herg': 'Pacific Herring', 'phal': 'Pacific Halibut', 'rckf': 'Rockfish', 'rckpo': 'Rockfish', 'rklc': 'Rockfish', 'sal': 'Salmon', 'salt': 'Salmon', 'sard': 'Sardines', 'shrmpt': 'Shrimp', 'smtb': 'Smelt', 'sphkl': 'Surf Perch', 'urchd': 'Urchin'} 
        targets = {'abal': ['red abalone'], 'achv': ['coastal pelagic finfish'], 'chal': ['California halibut'], 'dcrab': ['Dungeness crab'], 'dcrabt': ['Dungeness crab'], 'eswd': ['bull kelp', 'sea palm', 'canopy-forming algae'], 'herg': ['coastal pelagic finfish'], 'phal': ['Pacific halibut'], 'rckf': ['rockfishes'], 'rckpo': ['rockfishes'], 'rklc': ['rockfishes'], 'sal': ['salmon'], 'salt': ['salmon'], 'sard': ['coastal pelagic finfish'], 'shrmpt': ['coonstripe shrimp and spot prawn'], 'smtb': ['smelts'], 'sphkl': ['redtail surfperch'], 'urchd': ['urchin']} 
        #should commercial surf perch (sphkl) be 'hook and line' or 'hook and line from shore'???
        #using 'hook and line from shore' in original getAllLayers and results generated were not in agreement with SAT
        #maybe start with 'hook and line' here, and change later if that doens't line up
        #might want to bring this to someone's attention though if 'hook and line' works but 'hook and line from shore does not'
        #answer might lie in which instance do the stats line up 
        commercial_methods = {'achv': ['round-haul net'], 'dcrabt': ['trap'], 'eswd': ['intertidal hand harvest'], 'herg': ['gillnet'], 'rklc': ['trap', 'hook and line'], 'salt': ['troll'], 'sard': ['round-haul net'], 'shrmpt': ['trap'], 'smtb': ['dip net'], 'sphkl': ['hook and line'], 'urchd': ['diving']}
        rec_cpfv_methods = {'chal': ['hook and line'], 'dcrab': ['trap'], 'phal': ['hook and line'], 'rckpo': ['hook and line'], 'sal': ['hook and line']}
        rec_div_methods = {'abal': ['free dive'], 'dcrab': ['dive'], 'rckf': ['spearfish']}
        rec_kyk_methods = {'sal': ['hook and line'], 'rckf': ['hook and line']}
        rec_pvt_methods = {'chal': ['hook and line'], 'dcrab': ['trap'], 'phal': ['hook and line'], 'rckf': ['hook and line'], 'sal': ['hook and line']}
        
        raster_path = os.path.join(settings.GIS_DATA_ROOT, 'analysis')
        layers = list()
        for group in groups.keys():
            group_path = os.path.join(raster_path, group)
            for root, dirs, files in os.walk(group_path):
                for dir in dirs:
                    tuple = dir.partition('_')
                    species = tuple[0]
                    port = tuple[2]
                    group_name = groups[group]
                    group_abbr = group
                    cell_size = self.CELL_SIZE
                    fishing_type = fishing_types[group]  
                    if fishing_type == 'commercial':
                        take_methods = commercial_methods[species]
                    else:
                        take_methods = vars()['rec_'+group+'_methods'][species]
                    port_name = ports[port]
                    port_abbr = port
                    target_names = targets[species]
                    species_display_name = species_display[species]
                    species_abbr =  species
                    layer = Layer(group_name, group_abbr, cell_size, fishing_type, take_methods, port_name, port_abbr, species_display_name, species_abbr, target_names)
                    layers.append(layer)
                    #print 'Layer(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' %(group_name, group_abbr, cell_size, fishing_type, take_methods, port_name, port_abbr, species_name, species_display_name, species_abbr)                    
                    
        return layers
        
    
    def previousgetAllLayers(self):
        #THE FOLLOWING IS FOR INITIAL TESTING ONLY...
        #WILL EVENTUALLY REPLACE THE FOLLOWING TEST CODE WITH AN ALGORITHM FOR BUILDING all_layers BY WALKING THROUGH 
        #THE raster_origs DIRECTORY COMMERCIAL FISHERIES
        
        all_layers = list()
        
        layer = Layer('Commercial', 'com', self.CELL_SIZE, 'commercial', ['trap', 'hook and line'], 'Crescent City', 'cc', 'Rockfish', 'rklc', ['rockfishes'])
        all_layers.append(layer)
        '''
        layer = Layer('Commercial', 'com', self.CELL_SIZE, 'commercial', ['hook and line from shore'], 'Crescent City', 'cc', 'Surfperch', 'sphkl', ['redtail surfperch'])
        all_layers.append(layer)
        layer = Layer('Commercial', 'com', self.CELL_SIZE, 'commercial', ['trap', 'hook and line'], 'Trinidad', 'td', 'Rockfish', 'rklc', ['rockfishes'])
        all_layers.append(layer)
        layer = Layer('Commercial', 'com', self.CELL_SIZE, 'commercial', ['trap', 'hook and line'], 'Eureka', 'ek', 'Rockfish', 'rklc', ['rockfishes'])
        all_layers.append(layer)
        layer = Layer('Commercial', 'com', self.CELL_SIZE, 'commercial', ['gillnet'], 'Eureka', 'ek', 'Pacific Herring', 'herg', ['coastal pelagic finfish'])
        all_layers.append(layer)
        '''
        layer = Layer('Edible Seaweed', 'swd', self.CELL_SIZE, 'commercial', ['intertidal hand harvest'], 'Crescent City', 'cc', 'All Edible Seaweed Species', 'eswd', ['bull kelp', 'sea palm', 'canopy-forming algae'])
        all_layers.append(layer)
        
        #RECREATIONAL FISHERIES
        #BEFORE PRELOADING DATA CHANGE getGridName/getFullName USES IN Analysis.py TO REFLECT ORIGINAL Analysis.py
        '''
        layer = Layer('Commercial Passenger Fishing Vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Crescent City', 'cc', 'Rockfish', 'rckpo', ['rockfishes'])
        all_layers.append(layer)
        layer = Layer('Commercial Passenger Fishing Vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Trinidad', 'td', 'Pacific Halibut', 'phal', ['Pacific halibut'])
        all_layers.append(layer)
        layer = Layer('Commercial Passenger Fishing Vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Trinidad', 'td', 'Rockfish', 'rckpo', ['rockfishes'])
        all_layers.append(layer)
        layer = Layer('Commercial Passenger Fishing Vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Eureka', 'ek', 'Pacific Halibut', 'phal', ['Pacific halibut'])
        all_layers.append(layer)
        layer = Layer('Commercial Passenger Fishing Vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Eureka', 'ek', 'Rockfish', 'rckpo', ['rockfishes'])
        all_layers.append(layer)
        layer = Layer('Commercial Passenger Fishing Vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Shelter Cove', 'sc', 'Pacific Halibut', 'phal', ['Pacific halibut'])
        all_layers.append(layer)
        '''
        return all_layers

'''
A Layer represents a single fishing value layer which represents the
fishing value for a given species, by fisherman out of a given port/county
in a given fisherman user group.
'''
class Layer:
    def __init__(self, gn, ga, gcs, ft, tm, pn, pa, sn, sa, tn):
        self.group_name = gn
        self.group_abbr = ga
        self.cell_size = gcs
        self.fishing_type = ft
        self.take_methods = tm   
        self.port_name = pn
        self.port_abbr = pa
        self.species_name = sn
        self.species_abbr = sa      
        self.target_names = tn