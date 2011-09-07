from django.contrib.gis.db import models
from lingcod.features import register
from lingcod.features.models import Feature
from django.utils.html import escape
from django.conf import settings

class Bookmark(Feature):
    description = models.TextField(default="", null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    heading = models.FloatField(default=0)
    tilt = models.FloatField(default=0)
    roll = models.FloatField(default=0)
    altitudeMode = models.FloatField(default=1)
    ip = models.IPAddressField(default="0.0.0.0", null=True, blank=True)
    publicstate = models.TextField(default="{}")
    
    @property
    def kml(self):
        camera = "<Camera>\n"
        camera_params = ["latitude", "longitude", "altitude", "heading", "tilt", "roll", "altitudeMode"]
        for p in camera_params:
            val = self.__dict__[p]
            if val is not None:
                camera += "                <%s>%s</%s>\n" % (p, val, p)
        camera += "            </Camera>\n"
          
        return """
        <Placemark id="%s">
            <visibility>1</visibility>
            <name>%s</name>
            <styleUrl>#%s-default</styleUrl>
            <ExtendedData>
                <Data name="descr"><value>%s</value></Data>
            </ExtendedData>
            %s
        </Placemark>
        """ % (self.uid, escape(self.name), self.model_uid(), escape(self.description), camera) 

    @property
    def kml_style(self):
        return """
        <Style id="%s-default"> 
            <!-- invisible -->
            <BalloonStyle>
                <bgColor>ffeeeeee</bgColor>
                <text> <![CDATA[ 
                    <h3>$[name]</h3>
                    <p>$[descr]</p>
                ]]> </text>
            </BalloonStyle>
            <IconStyle>
                <scale>0.0</scale>
            </IconStyle>
            <LabelStyle>
                <scale>0.0</scale>
            </LabelStyle>
        </Style>
        """ % (self.model_uid())


    class Options:
        manipulators = []
        optional_manipulators = [ ]
        verbose_name = 'Bookmark'
        form = 'lingcod.bookmarks.forms.BookmarkForm'
        icon_url = 'bookmarks/images/bookmark.png'
        form_template = 'bookmarks/form.html'
        show_template = 'bookmarks/show.html'

if settings.BOOKMARK_FEATURE:
    Bookmark = register(Bookmark)
