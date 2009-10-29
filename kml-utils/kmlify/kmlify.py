#!/usr/bin/python
from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.gdal import SpatialReference
import os
import sys
import zipfile

kml_header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
"""

kml_styles = """   <Style id="default">
    <LineStyle>
        <color>7dff0000</color>
        <width>1.5</width>
    </LineStyle>
    <PolyStyle>
        <color>7dff0000</color>
    </PolyStyle>
    <BalloonStyle>
      <text>
        <![CDATA[
%s
        ]]>
      </text>
    </BalloonStyle>
    </Style>
"""

kml_footer = "</Document></kml>"

placemark = """
<Placemark>
    <name>%s</name>
    <styleUrl>#default</styleUrl>
    %s
    %s
</Placemark>
"""

def handle_geom(geom, gh, tolerance=0.0001):
    """
    Given an OGR/geodjango geometry, do something to it and return as kml string
    """
    if gh=='convex':
        return geom.convex_hull.kml
    elif gh=='original':
        return geom.kml
    elif gh=='simplify':
        return geom.geos.simplify(tolerance=tolerance, preserve_topology=True).kml
    elif gh=='exterior':
        # just grab the exterior ring and coerce it into a kml polygon
        return "<Polygon><outerBoundaryIs>%s</outerBoundaryIs></Polygon>" % geom.exterior_ring.kml
    elif gh=='exterior_simplify':
        ring = geom.geos.exterior_ring.simplify(tolerance=tolerance, preserve_topology=True).kml
        return "<Polygon><outerBoundaryIs>%s</outerBoundaryIs></Polygon>" % ring

def sanitize(s):
    """
    Make sure certain chars are escaped properly for xml
    """
    return str(s).replace("&","&amp;").replace("<","&gt;").replace(">","&lt;")

def working_dir(outdir, layername, threshold, gh):
    """
    Set up a working directory to place files
    """
    wdir = os.path.join(outdir, '%s_%s_%s' % (layername,int(threshold),gh))
    if not os.path.exists(wdir):
        os.makedirs(wdir)
    return wdir

def load_layer(dspath, layername=None):
    """
    Loads a datasource and returns the OGR Layer  
    """
    ds = DataSource(dspath)
    if layername is None:
        layername = os.path.splitext(os.path.basename(dspath))[0]
    layer = ds[layername]

    allowed_geomtypes = ['Point','Line','Polygon']
    if layer.geom_type.name not in allowed_geomtypes:
        raise Exception("The geometry type of the input dataset is not supported")

    return layer

def balloon_content(fields):
    """
    Create an ExtendedData template for balloons
    """
    balloon_content = ''
    for field in fields:
        balloon_content += "\n <li>%s is $[%s]</li>" % (field, field)
    return balloon_content
    
def extended_data(layer, feature,name_field):
    """
    Create the extended data xml fragment and assign the name/label field
    """
    name = ''
    extended_data = "<ExtendedData>\n"
    for field in layer.fields:
        extended_data += '<Data name="%s"> <value>%s</value> </Data>\n' % (field, 
                sanitize(feature[field]))
        if field == name_field:
            name = sanitize(feature[field])
    extended_data += "</ExtendedData>"
    return name, extended_data

def zip_as_KMZ(wdir):
    """
    Create a .kmz file from the specified directory. 
    Must contain a doc.kml (should probably check for that)
    This should really use the zipfile module rather than a popen call but laziness prevails
    """
    os.popen('zip -r %s.kmz %s' % (wdir,wdir))
    return

wgs84 = SpatialReference(4326)

def render_threshold_KMZ(dspath, options={}, outdir=os.getcwd(), layername=None):
    """
    Create a single KMZ using the threshold-by-area strategy
    """
    layer = load_layer(dspath,layername)

    try:
        gh = options['geometry_handler']
    except:
        gh = 'original'

    try:
        threshold = options['threshold']
    except:
        threshold = 0

    try:
        tolerance = options['tolerance']
    except:
        tolerance = 0

    wdir = working_dir(outdir, layer.name, int(threshold), gh)
    fh = open(os.path.join(wdir,"doc.kml"), 'w')

    fh.write(kml_header)
    fh.write(kml_styles % balloon_content(layer.fields))

    for feature in layer:
        label, extdata = extended_data(layer, feature, options['name_field'])

        if threshold>0:
            area = feature.geom.area
        else:
            area = 0

        if area > threshold or threshold==0:
            geom = feature.geom.transform(wgs84,clone=True)
            kml_geom = handle_geom(geom, gh, tolerance=tolerance)
            fh.write(placemark % (label, extdata, kml_geom))
        
    fh.write(kml_footer)
    fh.close()
    zip_as_KMZ(wdir)
