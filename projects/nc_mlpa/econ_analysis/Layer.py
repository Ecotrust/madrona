class Layers:
    def __init__(self):
        self.CELL_SIZE = 250
        
    def getAllLayers(self):
        #THE FOLLOWING IS FOR INITIAL TESTING ONLY...
        #WILL EVENTUALLY REPLACE THE FOLLOWING TEST CODE WITH AN ALGORITHM FOR BUILDING all_layers BY WALKING THROUGH 
        #THE raster_origs DIRECTORY COMMERCIAL FISHERIES
        
        all_layers = list()
        
        layer = Layer('commercial', 'com', self.CELL_SIZE, 'commercial', ['trap'], 'Entire Study Region', 'all', 'Dungeness crab', 'dcrabt')
        all_layers.append(layer)
        layer = Layer('commercial', 'com', self.CELL_SIZE, 'commercial', ['trap', 'hook and line'], 'Crescent City', 'cc', 'rockfishes', 'rklc')
        all_layers.append(layer)
        layer = Layer('commercial', 'com', self.CELL_SIZE, 'commercial', ['hook and line from shore'], 'Crescent City', 'cc', 'redtail surfperch', 'sphkl')
        all_layers.append(layer)
        layer = Layer('commercial', 'com', self.CELL_SIZE, 'commercial', ['trap', 'hook and line'], 'Trinidad', 'td', 'rockfishes', 'rklc')
        all_layers.append(layer)
        layer = Layer('commercial', 'com', self.CELL_SIZE, 'commercial', ['trap', 'hook and line'], 'Eureka', 'ek', 'rockfishes', 'rklc')
        all_layers.append(layer)
        layer = Layer('commercial', 'com', self.CELL_SIZE, 'commercial', ['gillnet'], 'Eureka', 'ek', 'coastal pelagic finfish', 'herg')
        all_layers.append(layer)
        
        #RECREATIONAL FISHERIES
        #BEFORE PRELOADING DATA CHANGE getGridName/getFullName USES IN Analysis.py TO REFLECT ORIGINAL Analysis.py
        
        layer = Layer('commercial passenger fishing vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Crescent City', 'cc', 'rockfishes', 'rckpo')
        all_layers.append(layer)
        layer = Layer('commercial passenger fishing vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Trinidad', 'td', 'Pacific halibut', 'phal')
        all_layers.append(layer)
        layer = Layer('commercial passenger fishing vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Trinidad', 'td', 'rockfishes', 'rckpo')
        all_layers.append(layer)
        layer = Layer('commercial passenger fishing vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Eureka', 'ek', 'Pacific halibut', 'phal')
        all_layers.append(layer)
        layer = Layer('commercial passenger fishing vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Eureka', 'ek', 'rockfishes', 'rckpo')
        all_layers.append(layer)
        layer = Layer('commercial passenger fishing vessel', 'cpfv', self.CELL_SIZE, 'recreational', ['hook and line'], 'Shelter Cove', 'sc', 'Pacific halibut', 'phal')
        all_layers.append(layer)
        
        return all_layers

'''
A Layer represents a single fishing value layer which represents the
fishing value for a given species, by fisherman out of a given port/county
in a given fisherman user group.
'''
class Layer:
    def __init__(self, gn, ga, gcs, ft, tm, pn, pa, sn, sa):
        self.group_name = gn
        self.group_abbr = ga
        self.cell_size = gcs
        self.fishing_type = ft
        self.take_methods = tm   
        self.port_name = pn
        self.port_abbr = pa
        self.species_name = sn
        self.species_abbr = sa          