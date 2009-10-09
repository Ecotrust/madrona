#!/usr/bin/env python

from mapnik import Map
import os

def render_to_wld(mapnik_map, path, x_rotation=0.0, y_rotation=0.0):
    scale = mapnik_map.scale()
    extent= mapnik_map.envelope()
    upper_left_x_center = extent.minx+(scale/2)
    upper_left_y_center = extent.maxy+(scale/2)
    wld_string = '%f\n%s\n%s\n-%f\n%f\n%f\n' % (scale,y_rotation,x_rotation,scale,upper_left_x_center,upper_left_y_center)
    wld_file = open(path, 'w')
    wld_file.write(wld_string)
    print 'world file output written to %s:' % path
    print wld_string


