from django.db import models
from django.conf import settings
from lingcod.data_manager.models import DataLayer
import sys

def modules_in_module(module='lingcod',exclude_list=['views','urls']):
    """This will return a list of modules found in a given module while excluding
    modules whos name is in the exclude_list."""
    result = []
    mod = sys.modules[module]
    for key in dir(mod):
        try:
            if mod.__dict__[key].__class__.__name__ == 'module' and key not in exclude_list:
                key = '.'.join([module,key])
                try:
                    sys.modules[key]
                except KeyError:
                    pass
                else:
                    result.append(key)
                    
        except AttributeError:
            pass
    return result

def models_in_module(module):
    """Returns a list of models for a given module"""
    result = []
    mod = sys.modules[module]
    for key in dir(mod):
        try:
            if mod.__dict__[key].__class__.__name__ == 'ModelBase':
                result.append(key)
        except AttributeError:
            continue
            
    return result

def models_in_module_recursive(modules=settings.INSTALLED_APPS,exclude_django=True):
    """Returns a list of dicts with model names as keys and the module where they live as values for a given module"""
    # I'm going to re-write this so it's flexible.  I'm going to look for models recursively until I find them.
    result = {}
    new_modules = modules
    while new_modules:
        for module in modules:
            new_modules = modules_in_module(module)
            for new in new_modules:
                #new = '.'.join([module,new])
                if new not in modules:
                    modules.append(new)
    for module in modules:
        the_models = models_in_module(module)
        if the_models:
            for the_model in the_models:
                if not exclude_django or not module.startswith('django.'):
                    result[the_model] = module
        
    return result

def fields_in_model(the_model):
    result = [ f.name for f in the_model._meta.fields ]
    return result

def load_potential_targets(modules=settings.INSTALLED_APPS,keep_previous=False,geometry_models_only=True):
    """Find all the models in all the apps within the module (lingcod)
    and load their info into the PotentialTarget model and the 
    PotentialTargetField model.  If geometry_models_only is True,
    delete records where there is no potential target field named geometry."""
    if not keep_previous:
        PotentialTarget.objects.all().delete()
    result = models_in_module_recursive(modules)
    for k,v in result.items():
        pt = PotentialTarget(name=k,module_text=v)
        pt.save()
        for name in pt.field_name_list:
            ptf = PotentialTargetField(name=name,potential_target=pt)
            ptf.save()
        if geometry_models_only:
            pt.delete_if_no_geometry()
    
class PotentialTarget(models.Model):
    """docstring for PotentialTarget"""
    name = models.CharField(max_length=255)
    module_text = models.CharField(max_length=255)
    
    class Meta:
        ordering = ['name']
            
    def __unicode__(self):
        return '%s from %s' % (self.name,self.module_text)
        
    @property
    def the_model(self):
        """docstring for model"""
        return sys.modules[self.module_text].__getattribute__(self.name)
    
    @property
    def field_name_list(self):
        return fields_in_model(self.the_model)
        
    def delete_if_no_geometry(self):
        """Check if this target contains a field called geometry.  If not, delete it."""
        if 'geometry' not in self.field_name_list:
            self.delete()
        
    # def copy(self):
    #     dt = DataTarget(name=self.name,module_text=self.module_text)
    #     
# class DataTarget(PotentialTarget):
#     """This model will contain the information about where you want to put the data that comes out of a shapefile in the data_manager app"""

class PotentialTargetField(models.Model):
    name = models.CharField(max_length=255)
    potential_target = models.ForeignKey(PotentialTarget)
    
    def __unicode__(self):
        return self.name

class LoadSetup(models.Model):
    name = models.CharField(max_length=255,help_text='It probably makes sense to name this after the model that you\'re loading data to')
    target_model = models.ForeignKey(PotentialTarget,help_text='The django model that you are going to load data into.') 
    origin_data_layer = models.ForeignKey(DataLayer,help_text='The Data Manager Data Layer that you are going to load data from.')
    origin_field_choices = models.TextField(null=True,blank=True,help_text='List of available fields in the origin data layer.  You must save this load setup to populate this list.')
    origin_field = models.CharField(max_length=255,null=True,blank=True,help_text='The shapefile field that contains data you want to move to the target field.')
    geometry_only = models.BooleanField(default=True, help_text='If this is true, you don\'t need to specify to fields')
    target_field_choices = models.TextField(null=True,blank=True,help_text='List of attributes of the target model. You must save this setup to populate this field.')
    target_field = models.CharField(max_length=255,null=True,blank=True,help_text='Enter the field name that you want the attribute data to go into.')
    
    def __unicode__(self):
        return self.name
        
    def save(self):
        super(LoadSetup,self).save()
        self.origin_field_choices = self.origin_data_layer.latest_shapefile.field_info_str().replace('\n',',  ')
        self.target_field_choices = ', '.join( [ ptf.name for ptf in self.target_model.potentialtargetfield_set.all() ] )
        super(LoadSetup,self).save()
    
    def run_load_setup(self):
        self.origin_data_layer.latest_shapefile.load_to_model(self.target_model.the_model, self.geometry_only, self.origin_field, self.target_field)
        
    # class TargetField(models.Model):
    #     name = models.CharField(max_length=255)
    #     potential_target_field = models.ForeignKey(PotentialTargetField)
    #     
    #     def __unicode__(self):
    #         return '%s from %s' % (self.name, self.potential_target_field.name)
    