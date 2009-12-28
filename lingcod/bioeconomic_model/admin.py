from django.contrib.gis import admin
from lingcod.bioeconomic_model.models import *

class OrganismParametersAdmin(admin.ModelAdmin):
    fieldsets = ( (None, {'fields': ('organism','length_units',('habitat','habitat_references'),('range','range_references'),('biogeography','biogeography_references'),('pelagic_larval_duration','pelagic_larval_duration_references'),
              ('spawn_start','spawn_start_references'),('spawn_end','spawn_end_references'),('home_range','home_range_references'),('asymtotic_length','asymtotic_length_references'),
              ('instantaneous_growth', 'instantaneous_growth_references'),('age_at_length_zero','age_at_length_zero_references'),('c_one','c_one_references'),('c_two','c_two_references'),
              ('age_at_maturity','age_at_maturity_references'),('age_first_fished','age_first_fished_references'),('maximum_age','maximum_age_references'),
              ('natural_mortality','natural_mortality_references'),('compensation_ratio','compensation_ratio_references'),) } ), )
    filter_horizontal = ('habitat_references','range_references','biogeography_references','pelagic_larval_duration_references',
              'spawn_start_references','spawn_end_references','home_range_references','asymtotic_length_references',
              'instantaneous_growth_references','age_at_length_zero_references','c_one_references','c_two_references',
              'age_at_maturity_references','age_first_fished_references','maximum_age_references',
              'natural_mortality_references','compensation_ratio_references',)

admin.site.register(Organism)
admin.site.register(Habitat)

class ExtentAdmin(admin.GeoModelAdmin):
    pass

class StudyRegionAdmin(admin.GeoModelAdmin):
    pass

admin.site.register(Extent,ExtentAdmin)
admin.site.register(Reference)
admin.site.register(LengthUnit)
admin.site.register(OrganismParameters,OrganismParametersAdmin)
admin.site.register(OrganizationScheme)
admin.site.register(StudyRegion, StudyRegionAdmin)