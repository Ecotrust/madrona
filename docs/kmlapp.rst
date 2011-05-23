.. _kmlapp:

`lingcod.kmlapp`: KML Representation of Features and Collections
================================================================

.. note::
    Why call it `kmlapp` instead of simply `kml`? That namespace conflicts with the python bindings for libkml. 

.. note::
    Certain aspects of KML require absolute URLs and thus require configuring 
    the site domain with the `Django Sites framework <http://docs.djangoproject.com/en/dev/ref/contrib/sites/>`_. 
    You can do this by setting the domain name of your server
    through the admin tool (e.g. http://localhost:8000/admin/sites/site/1/).


Customizing the KML Representation 
**********************************

The Feature's kml representation is determined by several properties on the feature instance, 
    * .kml
    * .kml_style 
      
Reasonble default kml and kml_style properties are provided for all Feature types but most likely you'll need to override them to customize the look, feel and behavior of your application.

The `.kml` property MUST  
    * Return a string containing a valid `KML Feature <http://code.google.com/apis/kml/documentation/kmlreference.html#feature>`_ element (most commonly a Placemark or Folder)
    * Encode/escape any strings containing html entities that not part of the KML document structure. For instance, the name attribute of the feature might contain an ampersand which, if left unescaped, might create invalid kml. Use the ``django.utils.html.escape`` function.
    * The element must have an ``id`` attribute populated with the value of ``instance.uid``.
    * If it references any style URLs, the corresponding `Style element(s) <http://code.google.com/apis/kml/documentation/kmlreference.html#style>`_ must be provided by the feature's .kml_style property

The `.kml_style` property MUST
    * Return a string containing one or more valid `Style element(s) <http://code.google.com/apis/kml/documentation/kmlreference.html#style>`_ which may be referenced by URL from the KML feature.
    * Attempt to be reusable by all similar features; If your kml document contains multiple features, only the *unique* .kml_style strings will appear in the document. Refrain from creating a seperate style for each and every feature and try to group them into classes. 


Below is an example of how one might use the kml properties to classify the kml represetation of features.::

    @register
    class Mpa(PolygonFeature):
        designation = models.CharField(max_length=42)
        ...

        @property
        def kml(self):
            if self.designation == 'Marine Conservation Area':
                color = "green"
            else:
                color = "blue"

            return """
            <Placemark id="%s">
                <name>%s</name>
                <styleUrl>#%s-default</styleUrl>
                <styleUrl>#%s-%s</styleUrl>
                <ExtendedData>
                    <Data name="name"><value>%s</value></Data>
                    <Data name="user"><value>%s</value></Data>
                    <Data name="modified"><value>%s</value></Data>
                </ExtendedData>
                %s 
            </Placemark>
            """ % (self.uid, 
                self.name, 
                self.model_uid(),
                self.model_uid(), color,
                self.name, self.user, self.date_modified, 
                self.geom_kml)

        @property
        def kml_style(self):
            return """
            <Style id="%s-default">
                <BalloonStyle>
                    <bgColor>ffeeeeee</bgColor>
                    <text> <![CDATA[
                        <font color="#1A3752"><strong>$[name]</strong></font><br />
                        <font size=1>Created by $[user] on $[modified]</font>
                    ]]> </text>
                </BalloonStyle>
                <LabelStyle>
                    <color>ffffffff</color>
                    <scale>0.8</scale>
                </LabelStyle>
            </Style>

            <Style id="%s-green">
                <PolyStyle>
                    <color>ff0000c0</color>
                </PolyStyle>
            </Style>

            <Style id="%s-blue">
                <PolyStyle>
                    <color>778B1A55</color>
                </PolyStyle>
            </Style>
            """ % (self.model_uid(), self.model_uid(), self.model_uid())

There is also the special case where the Feature may need to be represented by a full KML Document rather than a fragment containing KML Features. For example, the representation of a `User Uploaded KML` would be the contents of the unaltered file itself; we'd want use a network link to point to the full KML Document. To acheive this, we can specify an optional `kml_full` property which should return a complete, valid KML Document::

    @property
    def kml_full(self):
        try:
            f = self.kml_file.read()
            return f
        except:
            return """<kml xmlns="http://www.opengis.net/kml/2.2"><Document><!-- empty --></Document></kml>"""

By default, Feature Collections are represented by network links for performance reasons. (Reduced file size, faster loading.)

KML Templates
**********************
The layout of the KML document is configured using the django templating system. You can override some or all of these templates by placing your customized versions in a TEMPLATE_DIR that is loaded before the kmlapp/templates directory (See `Loading Templates <http://docs.djangoproject.com/en/dev/ref/templates/api/#loading-templates>`_ in the django docs).

  * `kmlapp/base.kml` configures the overall top-level structure of the KML document. 
  * `kmlapp/public.kml` is a minor extension of the base.kml for unauthenticated users.
  * `kmlapp/shared.kml` configures the structure of the shared features; organized by group and user. 
