from django.db.models import Manager

class FishingImpactAnalysisMapManager(Manager):
    '''
    Given a user group and port/county name (home) returns a list of Layers, one for
    each species fished in the port/county for the user group.  Used for analysis
    '''
    def getSubset(self, group_req, port_req, species_req=None):
        maps = self.get_query_set()
        maps = maps.filter(group_name=group_req, port_name=port_req)
        if species_req:
            maps = maps.filter(species_name=species_req)
        return maps