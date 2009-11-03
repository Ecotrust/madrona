import os
import tempfile
from kmlify import render_threshold_KMZ

dspath = os.path.join(os.path.dirname(__file__), '../../media/staticmap/data/socal_gshhs.shp')

geom_handlers = ['original', 'exterior', 'exterior_simplify', 'convex', 'simplify']

opts = { 
        'name_field': 'AREA',
        'area_threshold': 0.001, # In the original dataset units, only output 
                                 # polygons larger than this area
        'tolerance': 0.005 # Simplification tolerance in degrees
}

outdir = tempfile.mkdtemp()
print "Check %s for outputs..." % outdir
for gh in geom_handlers:
    opts['geometry_handler'] = gh
    render_threshold_KMZ(dspath, options=opts, outdir=outdir)
    print "   rendered test dataset to KML using area threshold strategy and a %s geometry handler" % gh
    

