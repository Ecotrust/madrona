from django.db.models import Manager

class FishingImpactAnalysisMapManager(Manager):
    '''
    Given a user group and port/county name (home) returns a list of Layers, one for
    each species fished in the port/county for the user group.  Used for analysis
    '''
    def getSubset(self, group, port=None, species=None):
        maps = self.get_query_set()
        maps = maps.filter(group_name=group)
        if port:
            maps = maps.filter(port_name=port)
        if species:
            maps = maps.filter(species_name=species)
        return maps