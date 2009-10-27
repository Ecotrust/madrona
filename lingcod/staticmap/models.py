from django.contrib.gis.db import models

class MapConfig(models.Model):
    """Model used for representing a map (ie a collection of styled map layers)

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================

        ``mapname``             Name of the map. Will be refered to by URL so 
                                use http friendly names (no spaces, slashes, etc)
        
        ``mapfile``             Mapnik xml configuration file that defines data 
                                sources and styles. All paths within xml must be 
                                relative to media/staticmap/
                                
        ``default_x1``          LL X coordinate

        ``default_y1``          LL Y coordinate

        ``default_x2``          UR X coordinate

        ``default_y2``          UR Y coordinate

        ``default_width``       Default image width (pixels)

        ``default_height``      Default image height (pixels)
        ======================  ==============================================
"""   
    
    def __unicode__(self):
        return u"%s" % (self.mapfile)
    
    mapname = models.CharField(max_length=50,unique=True)
    mapfile = models.FileField(upload_to='staticmap/', help_text="""
        Mapnik xml configuration file that defines data sources and styles. 
        All paths within xml must be relative to media/staticmap/
    """, blank=False, max_length=510)
    default_x1 = models.FloatField(
            help_text="Lower-left X coordinate of default map extent. Units and spatial reference system are defined in the mapnik xml.")
    default_y1 = models.FloatField(
            help_text="Lower-left Y coordinate of default map extent. Units and spatial reference system are defined in the mapnik xml.")
    default_x2 = models.FloatField(
            help_text="Upper-right X coordinate of default map extent. Units and spatial reference system are defined in the mapnik xml.")
    default_y2 = models.FloatField(
            help_text="Upper-right Y coordinate of default map extent. Units and spatial reference system are defined in the mapnik xml.")
    default_width = models.IntegerField(help_text="Default map image width in pixels")
    default_height = models.IntegerField(help_text="Default map image height in pixels")
