#!/usr/bin/env python

import mapnik
from georeference import render_to_wld

mapfile = 'habitat.xml'

m = mapnik.Map(20000,20000,'+proj=latlong +datum=WGS84')

mapnik.load_map(m, mapfile)

lyr = mapnik.Layer('world',"+proj=latlong +datum=WGS84")
lyr.datasource = mapnik.Shapefile(file='./data/BroadScaleHabsProj.shp')
m.zoom_to_box(lyr.envelope())
filepath = 'map'
raster = '%s.png' % filepath
world_file = '%s.pngw' % filepath
mapnik.render_to_file(m, raster, 'png')
render_to_wld(m, world_file)



