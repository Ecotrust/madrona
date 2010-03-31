import os
import settings

def GetSpeciesByGroup(group):
    species = []
    if group in ['Commercial']:
        specs = Layers.COMMERCIAL_METHODS.keys()
        specs.remove('eswd')
        specs.remove('sard')
    elif group in ['Commercial Passenger Fishing Vessel']:
        specs = Layers.REC_CPFV_METHODS.keys()
    elif group in ['Edible Seaweed']:
        specs = ['eswd']
    elif group in ['Recreational Dive']:
        specs = Layers.REC_DIV_METHODS.keys()
    elif group in ['Recreational Kayak']:
        specs = Layers.REC_KYK_METHODS.keys()
    elif group in ['Recreational Private Vessel']:
        specs = Layers.REC_PVT_METHODS.keys()
    else:
        raise Exception('invalid group sent to Layers.getSpeciesInGroup')
    for spec in specs:
        species.append(Layers.SPECIES_DISPLAY[spec])
    return species

def GetPortsByGroup(group):
    if group in ['com', 'Commercial']:
        return ['Crescent City', 'Trinidad', 'Eureka', 'Shelter Cove', 'Fort Bragg', 'Albion']
    if group in ['cpfv', 'Commercial Passenger Fishing Vessel']:
        return ['Crescent City', 'Trinidad', 'Eureka', 'Shelter Cove', 'Fort Bragg']
    if group in ['div', 'Recreational Dive']:
        return ['Crescent City', 'Trinidad', 'Eureka', 'Shelter Cove', 'Fort Bragg']
    if group in ['kyk', 'Recreational Kayak']:
        return ['Trinidad', 'Fort Bragg']
    if group in ['pvt', 'Recreational Private Vessel']:
        return ['Crescent City', 'Trinidad', 'Eureka', 'Shelter Cove', 'Fort Bragg']
    if group in ['swd', 'Edible Seaweed']:
        return ['Crescent City', 'Elk', 'Fort Bragg']
    raise Exception('invalid group sent to Layers.GetPortsInGroup')
    
def GetAllLayers():
    #should commercial surf perch (sphkl) be 'hook and line' or 'hook and line from shore'???
    #surf perch update....'hook and line' seems to be working on the server
    raster_path = os.path.join(settings.GIS_DATA_ROOT, 'analysis')
    layers = list()
    for group in Layers.GROUPS.keys():
        group_path = os.path.join(raster_path, group)
        for root, dirs, files in os.walk(group_path):
            for dir in dirs:
                tuple = dir.partition('_')
                species = tuple[0]
                port = tuple[2]
                group_name = Layers.GROUPS[group]
                group_abbr = group
                fishing_type = Layers.FISHING_TYPES[group]  
                if group_abbr == 'com':
                    take_methods = Layers.COMMERCIAL_METHODS[species]
                elif group_abbr == 'cpfv':
                    take_methods = Layers.REC_CPFV_METHODS[species]
                elif group_abbr == 'div':
                    take_methods = Layers.REC_DIV_METHODS[species]
                elif group_abbr == 'kyk':
                    take_methods = Layers.REC_KYK_METHODS[species]
                elif group_abbr == 'pvt':
                    take_methods = Layers.REC_PVT_METHODS[species]
                port_name = Layers.PORTS[port]
                port_abbr = port
                target_names = Layers.TARGETS[species]
                species_display_name = Layers.SPECIES_DISPLAY[species]
                species_abbr =  species
                layer = Layer(group_name, group_abbr, Layers.CELL_SIZE, fishing_type, take_methods, port_name, port_abbr, species_display_name, species_abbr, target_names)
                layers.append(layer)
                
    return layers
    
class Layers:
    CELL_SIZE = 250
    GROUPS = {'com': 'Commercial', 'cpfv': 'Commercial Passenger Fishing Vessel', 'div': 'Recreational Dive', 'kyk': 'Recreational Kayak', 'pvt': 'Recreational Private Vessel', 'swd': 'Edible Seaweed'}
    PORTS = {'all': 'Entire Study Region', 'ab': 'Albion', 'cc': 'Crescent City', 'ek': 'Eureka', 'el': 'Elk', 'fb': 'Fort Bragg', 'sc': 'Shelter Cove', 'td': 'Trinidad'}
    TARGETS = {'abal': ['red abalone'], 'achv': ['coastal pelagic finfish'], 'chal': ['California halibut'], 'dcrab': ['Dungeness crab'], 'dcrabt': ['Dungeness crab'], 'eswd': ['bull kelp', 'sea palm', 'canopy-forming algae'], 'herg': ['coastal pelagic finfish'], 'phal': ['Pacific halibut'], 'rckf': ['rockfishes'], 'rckpo': ['rockfishes'], 'rklc': ['rockfishes'], 'sal': ['salmon'], 'salt': ['salmon'], 'sard': ['coastal pelagic finfish'], 'shrmpt': ['coonstripe shrimp and spot prawn'], 'smtb': ['smelts'], 'sphkl': ['redtail surfperch'], 'urchd': ['urchin']} 
    FISHING_TYPES = {'com': 'commercial', 'cpfv': 'recreational', 'div': 'recreational', 'kyk': 'recreational', 'pvt': 'recreational', 'swd': 'commercial'}
    COMMERCIAL_SPECIES_DISPLAY = {'Anchovies': 'Anchovy/Sardine (Lampara Net)', 'Dungeness Crab': 'Dungeness Crab (Trap)', 'Pacific Herring': 'Herring (Seine)', 'Rockfish': 'Rockfish (Fixed Gear)', 'Salmon': 'Salmon (Troll)', 'Edible Seaweed': 'Seaweed (Hand Harvest)', 'Shrimp': 'Shrimp (Trap)', 'Smelt': 'Smelt (Brail - Dip Net)', 'Surf Perch': 'Surfperch (Hook and Line)', 'Urchin': 'Urchin (Dive)'}
    COMMERCIAL_METHODS = {'achv': ['round-haul net'], 'dcrabt': ['trap'], 'eswd': ['intertidal hand harvest'], 'herg': ['gillnet'], 'rklc': ['trap', 'hook and line'], 'salt': ['troll'], 'sard': ['round-haul net'], 'shrmpt': ['trap'], 'smtb': ['dip net'], 'sphkl': ['hook and line'], 'urchd': ['diving']}
    SPECIES_DISPLAY = {'abal': 'Abalone', 'achv': 'Anchovies', 'chal': 'California Halibut', 'dcrab': 'Dungeness Crab', 'dcrabt': 'Dungeness Crab', 'eswd': 'All Edible Seaweed Species', 'herg': 'Pacific Herring', 'phal': 'Pacific Halibut', 'rckf': 'Rockfish', 'rckpo': 'Rockfish', 'rklc': 'Rockfish', 'sal': 'Salmon', 'salt': 'Salmon', 'sard': 'Sardines', 'shrmpt': 'Shrimp', 'smtb': 'Smelt', 'sphkl': 'Surf Perch', 'urchd': 'Urchin'} 
    REC_CPFV_METHODS = {'chal': ['hook and line'], 'dcrab': ['trap'], 'phal': ['hook and line'], 'rckpo': ['hook and line'], 'sal': ['hook and line']}
    REC_DIV_METHODS = {'abal': ['free dive'], 'dcrab': ['dive'], 'rckf': ['spearfish']}
    REC_KYK_METHODS = {'sal': ['hook and line'], 'rckf': ['hook and line']}
    REC_PVT_METHODS = {'chal': ['hook and line'], 'dcrab': ['trap'], 'phal': ['hook and line'], 'rckf': ['hook and line'], 'sal': ['hook and line']}
    
    def previousgetAllLayers(self):
        #THE FOLLOWING IS FOR INITIAL TESTING ONLY...
        all_layers = list()
        
        layer = Layer('Commercial', 'com', Layers.CELL_SIZE, 'commercial', ['trap', 'hook and line'], 'Crescent City', 'cc', 'Rockfish', 'rklc', ['rockfishes'])
        all_layers.append(layer)
        layer = Layer('Edible Seaweed', 'swd', Layers.CELL_SIZE, 'commercial', ['intertidal hand harvest'], 'Crescent City', 'cc', 'All Edible Seaweed Species', 'eswd', ['bull kelp', 'sea palm', 'canopy-forming algae'])
        all_layers.append(layer)
        
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