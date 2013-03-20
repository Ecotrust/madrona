from django.db import models
from django.template.defaultfilters import slugify
from madrona.common.utils import cachemethod

class Theme(models.Model):
    display_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    header_image = models.CharField(max_length=255, blank=True, null=True)
    header_attrib = models.CharField(max_length=255, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.URLField(max_length=255, blank=True, null=True)
    factsheet_thumb = models.CharField(max_length=255, blank=True, null=True)
    factsheet_link = models.CharField(max_length=255, blank=True, null=True)
    # not really using these atm    
    feature_image = models.CharField(max_length=255, blank=True, null=True)
    feature_excerpt = models.TextField(blank=True, null=True)
    feature_link = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return unicode('%s' % (self.name))

    @property
    def learn_link(self):
        return '/learn/%s' % (self.name)
        
    @property
    @cachemethod("Theme_toDict_%(id)s")
    def toDict(self):
        layers = [layer.id for layer in self.layer_set.filter(is_sublayer=False).exclude(layer_type='placeholder')]
        themes_dict = {
            'id': self.id,
            'display_name': self.display_name,
            'name': self.name,
            'learn_link': self.learn_link,
            'layers': layers,
            'description': self.description
        }
        return themes_dict

class Layer(models.Model):
    TYPE_CHOICES = (
        ('XYZ', 'XYZ'),
        ('WMS', 'WMS'),
        ('ArcRest', 'ArcRest'),
        ('radio', 'radio'),
        ('checkbox', 'checkbox'),
        ('Vector', 'Vector'),
        ('placeholder', 'placeholder'),
    )
    name = models.CharField(max_length=100, help_text="Layer name (as it appears in the interface)")
    layer_type = models.CharField(max_length=50, choices=TYPE_CHOICES, help_text="Layer type")
    url = models.CharField(max_length=255, null=True)
    arcgis_layers = models.CharField(max_length=255, blank=True, null=True)
    subdomains = models.CharField(max_length=255, blank=True, null=True)
    sublayers = models.ManyToManyField('self', blank=True, null=True, help_text="Select the PARENT layer (which should be checkbox or radio type). Be sure to also check is_sublayer.")
    themes = models.ManyToManyField("Theme", null=True)
    is_sublayer = models.BooleanField(default=False)
    legend = models.CharField(max_length=255, blank=True, null=True, help_text="URL to legend image")
    legend_title = models.CharField(max_length=255, blank=True, null=True)
    legend_subtitle = models.CharField(max_length=255, blank=True, null=True)
    utfurl = models.CharField(max_length=255, blank=True, null=True)
    default_on = models.BooleanField(default=False, help_text="Should layer appear initially on load?")
    
    #tooltip
    description = models.TextField(blank=True, null=True)
    
    #data description (updated fact sheet) (now the Learn pages)
    data_overview = models.TextField(blank=True, null=True)
    data_status = models.CharField(max_length=255, blank=True, null=True)
    data_source = models.CharField(max_length=512, blank=True, null=True)
    data_notes = models.TextField(blank=True, null=True)
    
    #data catalog links    
    bookmark = models.CharField(max_length=755, blank=True, null=True)
    map_tiles = models.CharField(max_length=255, blank=True, null=True)
    kml = models.CharField(max_length=255, blank=True, null=True)
    data_download = models.CharField(max_length=255, blank=True, null=True)
    learn_more = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.CharField(max_length=255, blank=True, null=True)
    fact_sheet = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=512, blank=True, null=True)
    thumbnail = models.URLField(max_length=255, blank=True, null=True)
    
    #geojson javascript attribution
    EVENT_CHOICES = (
        ('click', 'click'),
        ('mouseover', 'mouseover')
    )
    attribute_title = models.CharField(max_length=255, blank=True, null=True)
    attribute_fields = models.ManyToManyField('AttributeInfo', blank=True, null=True)
    compress_display = models.BooleanField(default=False)
    attribute_event = models.CharField(max_length=35, choices=EVENT_CHOICES, default='click')
    lookup_field = models.CharField(max_length=255, blank=True, null=True)
    lookup_table = models.ManyToManyField('LookupInfo', blank=True, null=True)
    vector_color = models.CharField(max_length=7, blank=True, null=True)
    vector_fill = models.FloatField(blank=True, null=True)
    vector_graphic = models.CharField(max_length=255, blank=True, null=True)
    opacity = models.FloatField(default=.5, blank=True, null=True)
    
    def __unicode__(self):
        return unicode('%s' % (self.name))

    @property
    def themes_string(self):
        return ', '.join([x.display_name for x in self.themes.all()])

    @property
    def calculate_url(self):
        if self.subdomains:
            urls = []
            for sd in self.subdomains.split(","):
                urls.append(self.url.replace("${s}",sd))
            return urls
        else:
            return self.url

    @property
    def is_parent(self):
        return self.sublayers.all().count() > 0 and not self.is_sublayer
    
    @property
    def parent(self):
        if self.is_sublayer:
            return self.sublayers.all()[0]
        return self
    
    @property
    def slug(self):
        return slugify(self.name)

    @property
    def data_overview_text(self):
        if not self.data_overview and self.is_sublayer:
            return self.parent.data_overview
        else:
            return self.data_overview
        
    @property
    def data_source_text(self):
        if not self.data_source and self.is_sublayer:
            return self.parent.data_source
        else:
            return self.data_source
        
    @property
    def data_notes_text(self):
        if not self.data_notes and self.is_sublayer:
            return self.parent.data_notes
        else:
            return self.data_notes
    
    @property
    def bookmark_link(self):
        if not self.bookmark and self.is_sublayer and self.parent.bookmark:
            return self.parent.bookmark.replace('<layer_id>', str(self.id))
        else:
            return self.bookmark
    
    @property
    def data_download_link(self):
        if self.data_download and self.data_download.lower() == 'none':
            return None
        if not self.data_download and self.is_sublayer:
            return self.parent.data_download
        else:
            return self.data_download
        
    @property
    def metadata_link(self):
        if self.metadata and self.metadata.lower() == 'none':
            return None
        if not self.metadata and self.is_sublayer:
            return self.parent.metadata
        else:
            return self.metadata
        
    @property
    def source_link(self):
        if self.source and self.source.lower() == 'none':
            return None
        if not self.source and self.is_sublayer:
            return self.parent.source
        else:
            return self.source
        
    @property
    def learn_link(self):
        if self.learn_more:
            return self.learn_more
        else:
            return None
        """
        # TODO 
        else:
            try:
                theme = self.themes.all()[0]  
            except IndexError:
                return ""
            return "%s#%s" %(theme.learn_link, self.slug)
        """
        
    @property
    def description_link(self):
        theme_name = self.themes.all()[0].name
        return '/learn/%s#%s' % (theme_name, self.slug)
        
    @property
    def tooltip(self):
        if self.description and self.description.strip() != '':
            return self.description
        elif self.parent.description and self.parent.description.strip() != '':
            return self.parent.description
        else:
            return None
            
    @property
    def serialize_attributes(self):
        return {'title': self.attribute_title, 
                'compress_attributes': self.compress_display,
                'event': self.attribute_event,
                'attributes': [{'display': attr.display_name, 'field': attr.field_name, 'precision': attr.precision} for attr in self.attribute_fields.all().order_by('order')]}
    
    @property
    def serialize_lookups(self):
        return {'field': self.lookup_field, 
                'details': [{'value': lookup.value, 'color': lookup.color, 'dashstyle': lookup.dashstyle, 'fill': lookup.fill, 'graphic': lookup.graphic} for lookup in self.lookup_table.all()]}
    

    @property
    @cachemethod("Layer_toDict_%(id)s")
    def toDict(self):
        sublayers = [
            {
                'id': layer.id,
                'name': layer.name,
                'type': layer.layer_type,
                'url': layer.calculate_url,
                'arcgis_layers': layer.arcgis_layers,
                'utfurl': layer.utfurl,
                'parent': self.id,
                'legend': layer.legend,
                'legend_title': layer.legend_title,
                'legend_subtitle': layer.legend_subtitle,
                'description': layer.tooltip,
                'learn_link': layer.learn_link,
                'attributes': layer.serialize_attributes,
                'lookups': layer.serialize_lookups,
                'color': layer.vector_color,
                'fill_opacity': layer.vector_fill,
                'graphic': layer.vector_graphic,
                'data_source': layer.data_source,
                'opacity': layer.opacity
            } 
            for layer in self.sublayers.all()
        ]
        layers_dict = {
            'id': self.id,
            'name': self.name,
            'type': self.layer_type,
            'url': self.calculate_url,
            'arcgis_layers': self.arcgis_layers,
            'utfurl': self.utfurl,
            'subLayers': sublayers,
            'legend': self.legend,
            'legend_title': self.legend_title,
            'legend_subtitle': self.legend_subtitle,
            'description': self.description,
            'learn_link': self.learn_link,
            'attributes': self.serialize_attributes,
            'lookups': self.serialize_lookups,
            'default_on': self.default_on,
            'color': self.vector_color,
            'fill_opacity': self.vector_fill,
            'graphic': self.vector_graphic,
            'data_source': self.data_source,
            'opacity': self.opacity
        }
        return layers_dict

    class Meta:
        ordering = ['name']

class AttributeInfo(models.Model):
    display_name = models.CharField(max_length=255, blank=True, null=True)
    field_name = models.CharField(max_length=255, blank=True, null=True)
    precision = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(default=1)
    
    def __unicode__(self):
        return unicode('%s' % (self.field_name)) 
    
class LookupInfo(models.Model):
    DASH_CHOICES = (
        ('dot', 'dot'),
        ('dash', 'dash'),
        ('dashdot', 'dashdot'),
        ('longdash', 'longdash'),
        ('longdashdot', 'longdashdot'),
        ('solid', 'solid')
    )
    value = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)
    dashstyle = models.CharField(max_length=11, choices=DASH_CHOICES, default='solid')
    fill = models.BooleanField(default=False)
    graphic = models.CharField(max_length=255, blank=True, null=True)
    
    def __unicode__(self):
        return unicode('%s' % (self.value)) 


class DataNeed(models.Model):
    name = models.CharField(max_length=100)
    archived = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    expected_date = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    themes = models.ManyToManyField("Theme", blank=True, null=True)

    @property
    def html_name(self):
        return self.name.lower().replace(' ', '-')
    
    def __unicode__(self):
        return unicode('%s' % (self.name))

# When Layer or Theme changes, invalidate any caches
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch.dispatcher import receiver
from django.core.cache import cache

@receiver(post_save, sender=Layer)
@receiver(post_delete, sender=Layer)
def _clear_layer_cache(sender, instance, **kwargs):
    key = "Layer_toDict_%(id)s" % instance.__dict__
    cache.delete(key)
    for theme in Theme.objects.all():
        cache.delete("Theme_toDict_%s" % theme.id) 

@receiver(m2m_changed, sender=Layer.sublayers.through)
def _clear_layer_m2m_cache(sender, instance, **kwargs):
    # make sure we follow any m2m relationships
    for x in instance.sublayers.all():
        key = "Layer_toDict_%(id)s" % x.__dict__
        cache.delete(key)
    for theme in Theme.objects.all():
        cache.delete("Theme_toDict_%s" % theme.id) 

@receiver(post_save, sender=Theme)
@receiver(post_delete, sender=Theme)
def _clear_theme_cache(sender, instance, **kwargs):
    key = "Theme_toDict_%(id)s" % instance.__dict__
    cache.delete(key)
