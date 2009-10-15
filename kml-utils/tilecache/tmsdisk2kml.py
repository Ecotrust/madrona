#/usr/bin/env python
"""
Reads a TMS disk cache and generates superoverlays
Author: perry@marinemap.org
"""

import os
import glob
import TileCache.Service
from TileCache.Layer import Tile
#from TileCache.Services.KML import KML

# CONFIGURATION ======================#
tmsdir = "/tmp/tilecache"
tmsurl = "file:///tmp/tilecache" 
layername = "habitat"
extension = "png"
cfg = 'tilecache.cfg'
minLod = 64
overwrite = True

def main():
    s = TileCache.Service.load(cfg)
    lyr = s.layers[layername] 

    # Traverse the TMS directory and look for tiles
    for root, dirs, files in os.walk(os.path.join(tmsdir,layername)):
        for t in glob.glob(os.path.join(root,"*.%s" % extension)):
            tileinfo = t.split("/")[-8:]
            tileinfo[-1] = tileinfo[-1].replace(".%s" % extension, '')
            z = int(tileinfo[1])
            x = int(tileinfo[2]+tileinfo[3]+tileinfo[4])
            y = int(tileinfo[5]+tileinfo[6]+tileinfo[7])

            tile = Tile(lyr, x, y, z)
            doc = generate_kml_doc(tile, base_path=tmsurl, include_wrapper=True)
            filename = t.replace(extension, 'kml')
            if not os.path.exists(filename) or overwrite:
                print "Generating KML for zoom level %s tile %s,%s" % (z,x,y)
                fh = open(filename, 'w')
                fh.write(doc)
                fh.close()

    cell = lyr.getCell(lyr.bbox, exact=False)
    tile = Tile(lyr, cell[0], cell[1], cell[2])
    doc = generate_kml_doc(tile, base_path=tmsurl, include_wrapper=True)
    fh = open(os.path.join(tmsdir,layername,"doc.kml"),'w')
    fh.write(doc)
    fh.close()



def generate_kml_doc(tile, base_path="", include_wrapper = True):    
    """ Modified from TileCache.Cache.Disk """
    tiles = [
        Tile(tile.layer, tile.x << 1, tile.y << 1, tile.z + 1),
        Tile(tile.layer, (tile.x << 1) + 1, tile.y << 1, tile.z + 1),
        Tile(tile.layer, (tile.x << 1) + 1, (tile.y << 1) + 1, tile.z + 1),
        Tile(tile.layer, tile.x << 1 , (tile.y << 1) + 1, tile.z + 1)
    ]
    

    network_links = []
    
    for single_tile in tiles:
        if single_tile.z >= len(tile.layer.resolutions):
            continue

        dims = (  "%02d" % single_tile.z,
                "%03d" % int(single_tile.x / 1000000),
                "%03d" % (int(single_tile.x / 1000) % 1000),
                "%03d" % (int(single_tile.x) % 1000),
                "%03d" % int(single_tile.y / 1000000),
                "%03d" % (int(single_tile.y / 1000) % 1000),
                "%03d" % (int(single_tile.y) % 1000)
            )
        b = single_tile.bounds()
        network_links.append("""<NetworkLink>
    <name>tile</name>
    <Region>
    <Lod>
        <minLodPixels>%s</minLodPixels><maxLodPixels>-1</maxLodPixels>
    </Lod>
    <LatLonAltBox>
        <north>%s</north><south>%s</south>
        <east>%s</east><west>%s</west>
    </LatLonAltBox>
    </Region>
    <Link>
    <href>%s/%s/%s/%s/%s/%s/%s/%s/%s.kml</href>
    <viewRefreshMode>onRegion</viewRefreshMode>
    </Link>
</NetworkLink>""" % (minLod, b[3], b[1], b[2], b[0], base_path, single_tile.layer.name, 
                     dims[0], dims[1], dims[2], dims[3], dims[4], dims[5], dims[6]))

    dims = (  "%02d" % tile.z,
            "%03d" % int(tile.x / 1000000),
            "%03d" % (int(tile.x / 1000) % 1000),
            "%03d" % (int(tile.x) % 1000),
            "%03d" % int(tile.y / 1000000),
            "%03d" % (int(tile.y / 1000) % 1000),
            "%03d.%s" % (int(tile.y) % 1000, tile.layer.extension)
        )
    
    b = tile.bounds()
    kml = []
    if include_wrapper: 
        kml.append( """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.1">""")
    if tile.z == len(tile.layer.resolutions) - 1:
        max_lod_pixels = -1
    else:
        max_lod_pixels = 512
    kml.append("""
<Document>
<Region>
    <Lod>
    <minLodPixels>%s</minLodPixels><maxLodPixels>%d</maxLodPixels>
    </Lod>
    <LatLonAltBox>
    <north>%s</north><south>%s</south>
    <east>%s</east><west>%s</west>
    </LatLonAltBox>
</Region>
<GroundOverlay>
    <drawOrder>%s</drawOrder>
    <Icon>
    <href>%s/%s/%s/%s/%s/%s/%s/%s/%s</href>
    </Icon>
    <LatLonBox>
    <north>%s</north><south>%s</south>
    <east>%s</east><west>%s</west>
    </LatLonBox>
</GroundOverlay>
%s
""" % (minLod, max_lod_pixels, b[3], b[1], b[2], b[0], tile.z, base_path, tile.layer.name, 
       dims[0], dims[1], dims[2], dims[3], dims[4], dims[5], dims[6],
       b[3], b[1], b[2], b[0], "\n".join(network_links)))
    if include_wrapper:
        kml.append("""</Document></kml>""" )
    kml = "\n".join(kml)       

    return kml


if __name__ == "__main__":
    main()
