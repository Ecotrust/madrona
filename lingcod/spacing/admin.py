from django.contrib.gis import admin
from lingcod.spacing.models import *
from lingcod.spacing.views import create_pickled_graph_from_all_land as create_graph
from django.conf.urls.defaults import patterns, url

class SpacingPointAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(SpacingPoint,SpacingPointAdmin)

class LandAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(Land,LandAdmin)

class PickledGraphAdmin(admin.GeoModelAdmin):
    def get_urls(self):
        urls = super(PickledGraphAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^regenerate/$', self.admin_site.admin_view(create_graph), name='regenerate_pickledgraph')
        )
        return my_urls + urls
admin.site.register(PickledGraph,PickledGraphAdmin)