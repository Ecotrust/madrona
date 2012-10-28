# -*- coding: utf8 -*-
from django.core.management import setup_environ
import os
import sys
sys.path.append(os.path.dirname(os.path.join('..','nplcc',__file__)))

import settings
setup_environ(settings)

#==================================#
import json
from madrona.layer_manager.models import Theme, Layer

# go to http://demo.flightstats-ops.com/maps/
# put debugger in line 5 of http://demo.flightstats-ops.com/maps/maps.js
# copy the results of JSON.stringify(tilesinfo)
# replace all \" with '
tilesets_json = """
{"mqosm":{"group":"OpenStreetMap","name":"MapQuest Open Street Map","url":"http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.jpg","subdomains":"1234","attribution":"Data, imagery and map information provided by <a href='http://open.mapquest.co.uk' target='_blank'>MapQuest</a>, <a href='http://www.openstreetmap.org/' target='_blank'>OpenStreetMap</a> and contributors, <a href='http://creativecommons.org/licenses/by-sa/2.0/' target='_blank'>CC-BY-SA</a>","minZoom":0,"maxZoom":18},
"mqaerial":{"group":"OpenStreetMap","name":"MapQuest Open Aerial","url":"http://oatile{s}.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.jpg","subdomains":"1234","attribution":"Tiles courtesy of MapQuest. Portions Courtesy NASA/JPL-Caltech and U.S. Depart. of Agriculture, Farm Service Agency","minZoom":0,"maxZoom":18},
"osm":{"group":"OpenStreetMap","name":"Open Street Map Normal","url":"http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png","subdomains":"abc","attribution":"Data, imagery and map information provided by <a href='http://www.openstreetmap.org/' target='_blank'>OpenStreetMap</a> and contributors, <a href='http://creativecommons.org/licenses/by-sa/2.0/' target='_blank'>CC-BY-SA</a>","minZoom":0,"maxZoom":18},
"topousaosm":{"group":"OpenStreetMap","name":"Topo USA OSM","url":"http://tile1.toposm.com/us/color-relief/{z}/{x}/{y}.jpg","subdomains":"","attribution":"Data, imagery and map information provided by <a href='http://www.openstreetmap.org/' target='_blank'>OpenStreetMap</a> and contributors, <a href='http://creativecommons.org/licenses/by-sa/2.0/' target='_blank'>CC-BY-SA</a>","minZoom":3,"maxZoom":15},
"cloudmadepaledawn":{"group":"CloudMade","name":"Pale Dawn","url":"http://{s}.tile.cloudmade.com/8fe4ccbb4940415d9475cc21bf41ea53/998/256/{z}/{x}/{y}.png","subdomains":"abc","attribution":"2011 CloudMade","minZoom":0,"maxZoom":18},
"midnightcommander":{"group":"CloudMade","name":"Midnight Commander","url":"http://{s}.tile.cloudmade.com/8fe4ccbb4940415d9475cc21bf41ea53/999/256/{z}/{x}/{y}.png","subdomains":"abc","attribution":"2011 CloudMade","minZoom":0,"maxZoom":18},
"cloudmadegreen":{"group":"CloudMade","name":"Green Terrain","url":"http://{s}.tile.cloudmade.com/8fe4ccbb4940415d9475cc21bf41ea53/996/256/{z}/{x}/{y}.png","subdomains":"abc","attribution":"2011 CloudMade","minZoom":0,"maxZoom":18},
"cloudmadeweb":{"group":"CloudMade","name":"CloudMade Web","url":"http://{s}.tile.cloudmade.com/8fe4ccbb4940415d9475cc21bf41ea53/1/256/{z}/{x}/{y}.png","subdomains":"abc","attribution":"2011 CloudMade","minZoom":0,"maxZoom":18},
"cloudmadefine":{"group":"CloudMade","name":"CloudMade Fine Line","url":"http://{s}.tile.cloudmade.com/8fe4ccbb4940415d9475cc21bf41ea53/2/256/{z}/{x}/{y}.png","subdomains":"abc","attribution":"2011 CloudMade","minZoom":0,"maxZoom":18},
"cloudmadenonames":{"group":"CloudMade","name":"No Names","url":"http://{s}.tile.cloudmade.com/8fe4ccbb4940415d9475cc21bf41ea53/3/256/{z}/{x}/{y}.png","subdomains":"abc","attribution":"2011 CloudMade","minZoom":0,"maxZoom":18},
"cloudmaderoad":{"group":"CloudMade","name":"CloudMade Road","url":"http://{s}.tile.cloudmade.com/8fe4ccbb4940415d9475cc21bf41ea53/4/256/{z}/{x}/{y}.png","subdomains":"abc","attribution":"2011 CloudMade","minZoom":0,"maxZoom":18},
"cloudmademanilla":{"group":"CloudMade","name":"Manilla","url":"http://{s}.tile.cloudmade.com/8fe4ccbb4940415d9475cc21bf41ea53/7/256/{z}/{x}/{y}.png","subdomains":"abc","attribution":"2011 CloudMade","minZoom":0,"maxZoom":18},
"cloudmadered":{"group":"CloudMade","name":"CloudMade Red","url":"http://{s}.tile.cloudmade.com/8fe4ccbb4940415d9475cc21bf41ea53/8/256/{z}/{x}/{y}.png","subdomains":"abc","attribution":"2011 CloudMade","minZoom":0,"maxZoom":18},
"cloudmadehighway":{"group":"CloudMade","name":"CloudMade Highway","url":"http://{s}.tile.cloudmade.com/8fe4ccbb4940415d9475cc21bf41ea53/9/256/{z}/{x}/{y}.png","subdomains":"abc","attribution":"2011 CloudMade","minZoom":0,"maxZoom":18},
"mapboxterrain":{"group":"MapBox","name":"Mapbox Terrain","url":"http://{s}.tiles.mapbox.com/v3/examples.map-4l7djmvo/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":17},
"mapboxstreets":{"group":"MapBox","name":"Mapbox Streets","url":"http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-streets/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":17},
"mapboxsimple":{"group":"MapBox","name":"Mapbox Simple","url":"http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-simple/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":17},
"mapboxgeographyclass":{"group":"MapBox","name":"Geography Class","url":"http://{s}.tiles.mapbox.com/v3/mapbox.geography-class/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"mapboxpirate":{"group":"MapBox","name":"Pirate Map","url":"http://{s}.tiles.mapbox.com/v3/aj.Sketchy2/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"mapboxcanopy":{"group":"MapBox","name":"Canopy Height","url":"http://{s}.tiles.mapbox.com/v3/villeda.simard-forests/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"mapboxearthquake":{"group":"MapBox","name":"Earthquake Risk","url":"http://{s}.tiles.mapbox.com/v3/bclc-apec.map-rslgvy56/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"mapboxshadowplay":{"group":"MapBox","name":"Shadow Play","url":"http://{s}.tiles.mapbox.com/v3/tmcw.shadowplay/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"mapboxpopulationfire":{"group":"MapBox","name":"Population Fire","url":"http://{s}.tiles.mapbox.com/v3/aj.population-fire/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"mapboxwarden":{"group":"MapBox","name":"Mapbox Warden","url":"http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-warden/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":17},
"mapboxzenburn":{"group":"MapBox","name":"Mapbox Zenburn","url":"http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-zenburn/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":17},
"mapboxnightvision":{"group":"MapBox","name":"Mapbox Night Vision","url":"http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-nightvision/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":17},
"mapboxlight":{"group":"MapBox","name":"Mapbox Light","url":"http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-light/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":17},
"mapboxchester":{"group":"MapBox","name":"Mapbox Chester","url":"http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-chester/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":17},
"mapboxgraphite":{"group":"MapBox","name":"Mapbox Graphite","url":"http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-graphite/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":17},
"mapboxlacquer":{"group":"MapBox","name":"Mapbox Lacquer","url":"http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-lacquer/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":17},
"mapboxcontrolroom":{"group":"MapBox","name":"Control Room","url":"http://{s}.tiles.mapbox.com/v3/mapbox.control-room/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"mapboxprint":{"group":"MapBox","name":"World Print","url":"http://{s}.tiles.mapbox.com/v3/mapbox.world-print/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":9},
"mapboxworldlight":{"group":"MapBox","name":"World Light","url":"http://{s}.tiles.mapbox.com/v3/mapbox.world-light/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":11},
"mapboxworlddark":{"group":"MapBox","name":"World Dark","url":"http://{s}.tiles.mapbox.com/v3/mapbox.world-dark/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":1,"maxZoom":11},
"mapboxworldblue":{"group":"MapBox","name":"World Blue","url":"http://{s}.tiles.mapbox.com/v3/mapbox.world-blue/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"mapboxworldglass":{"group":"MapBox","name":"World Glass","url":"http://{s}.tiles.mapbox.com/v3/mapbox.world-glass/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":11},
"mapboxworldglassoceans":{"group":"MapBox","name":"World Glass Oceans","url":"http://{s}.tiles.mapbox.com/v3/mapbox.world-glass-oceans/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"naturalearth1":{"group":"NaturalEarth","name":"Natural Earth 1","url":"http://{s}.tiles.mapbox.com/v3/mapbox.natural-earth-1/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":6},
"naturalearth2":{"group":"NaturalEarth","name":"Natural Earth 2","url":"http://{s}.tiles.mapbox.com/v3/mapbox.natural-earth-2/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":6},
"naturalearthhypsometric":{"group":"NaturalEarth","name":"Hypsometric","url":"http://{s}.tiles.mapbox.com/v3/mapbox.natural-earth-hypso/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":6},
"naturalearthhypsobathy":{"group":"NaturalEarth","name":"Hypsometric Bathymetry","url":"http://{s}.tiles.mapbox.com/v3/mapbox.natural-earth-hypso-bathy/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":6},
"bmjul":{"group":"BlueMarble","name":"July","url":"http://{s}.tiles.mapbox.com/v3/mapbox.blue-marble-topo-jul/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"bmjulb":{"group":"BlueMarble","name":"July Bathymetry","url":"http://{s}.tiles.mapbox.com/v3/mapbox.blue-marble-topo-bathy-jul/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"bmjan":{"group":"BlueMarble","name":"January","url":"http://{s}.tiles.mapbox.com/v3/mapbox.blue-marble-topo-jan/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"bmjanb":{"group":"BlueMarble","name":"January Bathymetry","url":"http://{s}.tiles.mapbox.com/v3/mapbox.blue-marble-topo-bathy-jan/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"bmbw":{"group":"BlueMarble","name":"Gray","url":"http://{s}.tiles.mapbox.com/v3/mapbox.blue-marble-topo-jul-bw/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"bmbwb":{"group":"BlueMarble","name":"Gray Bathymetry","url":"http://{s}.tiles.mapbox.com/v3/mapbox.blue-marble-topo-bathy-jul-bw/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":0,"maxZoom":8},
"nasabmmm":{"group":"BlueMarble","name":"Modest Maps","url":"http://s3.amazonaws.com/com.modestmaps.bluemarble/{z}-r{y}-c{x}.jpg","subdomains":"","attribution":"NASA","minZoom":0,"maxZoom":9},
"bm8bit":{"group":"BlueMarble","name":"Blue Marble 8-bit","url":"http://{s}.tiles.mapbox.com/v3/colemanm.blue-marble-8bit/{z}/{x}/{y}.png","subdomains":"abcd","attribution":"Mapbox","minZoom":2,"maxZoom":5},
"terrain":{"group":"Stamen","name":"Terrain","url":"http://{s}.tile.stamen.com/terrain/{z}/{x}/{y}.jpg","subdomains":"abcd","attribution":"Michal Migurski http://mike.teczno.com/notes/osm-us-terrain-layer/foreground.html","minZoom":4,"maxZoom":18},
"terrainbg":{"group":"Stamen","name":"Terrain Background","url":"http://{s}.tile.stamen.com/terrain-background/{z}/{x}/{y}.jpg","subdomains":"abcd","attribution":"Michal Migurski http://mike.teczno.com/notes/osm-us-terrain-layer/foreground.html","minZoom":4,"maxZoom":18},
"watercolor":{"group":"Stamen","name":"Watercolor","url":"http://{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg","subdomains":"abcd","attribution":"<a href='http://stamen.com'>Stamen Design</a> <a href='http://creativecommons.org/licenses/by/3.0'>CC-BY-SA</a>","minZoom":0,"maxZoom":17},
"toner":{"group":"Stamen","name":"Toner","url":"http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.jpg","subdomains":"abcd","attribution":"<a href='http://stamen.com'>Stamen Design</a> <a href='http://creativecommons.org/licenses/by/3.0'>CC-BY-SA</a>","minZoom":0,"maxZoom":20},
"acetate":{"group":"GeoIQ","name":"Acetate Street","url":"http://{s}.acetate.geoiq.com/tiles/acetate/{z}/{x}/{y}.png","subdomains":["a1","a2","a3"],"attribution":"2011 GeoIQ &#038; Stamen, Data from OSM and Natural Earth","minZoom":2,"maxZoom":20},
"acetateterrain":{"group":"GeoIQ","name":"Acetate Terrain","url":"http://{s}.acetate.geoiq.com/tiles/terrain/{z}/{x}/{y}.png","subdomains":["a1","a2","a3"],"attribution":"2011 GeoIQ &#038; Stamen, Data from OSM and Natural Earth","minZoom":0,"maxZoom":20},
"acetatehillshade":{"group":"GeoIQ","name":"Acetate Hillshading","url":"http://{s}.acetate.geoiq.com/tiles/acetate-hillshading/{z}/{x}/{y}.png","subdomains":["a1","a2","a3"],"attribution":"2011 GeoIQ &#038; Stamen, Data from OSM and Natural Earth","minZoom":0,"maxZoom":17},
"worldbank":{"group":"GeoIQ","name":"World Bank","url":"http://acetate.geoiq.com/tiles/worldbank/{z}/{x}/{y}.png","subdomains":"","attribution":"World Bank","minZoom":0,"maxZoom":17},
"worldbankterrain":{"group":"GeoIQ","name":"World Bank Terrain","url":"http://acetate.geoiq.com/tiles/worldbank-hillshading/{z}/{x}/{y}.png","subdomains":"","attribution":"World Bank","minZoom":0,"maxZoom":17},
"googlenormal":{"group":"Google","name":"Google Street","url":"http://mt{s}.google.com/vt/v=w2.106&hl=en&x={x}&y={y}&z={z}&s=","subdomains":"0123","attribution":"Google 2012","minZoom":0,"maxZoom":22},
"googleterrain":{"group":"Google","name":"Google Terrain","url":"http://{s}.google.com/vt/v=w2p.106&hl=en&x={x}&y={y}&z={z}&s=","subdomains":["mt0","mt1","mt2","mt3"],"attribution":"Google 2012","minZoom":0,"maxZoom":15},
"googlesatellite":{"group":"Google","name":"Google Satellite","url":"http://khm{s}.googleapis.com/kh/v=118&src=app&x={x}&y={y}&z={z}&s=G&token=56901","subdomains":"0123","attribution":"2012 Google","minZoom":0,"maxZoom":21},
"googlephysical":{"group":"Google","name":"Google Physical","url":"http://mt{s}.googleapis.com/vt/lyrs=t@129,r@189000000&hl=en&src=api&x={x}&y={y}&z={z}&s=Galileo","subdomains":"0123","attribution":"Google 2012","minZoom":0,"maxZoom":22},
"nokiaroad":{"group":"Nokia","name":"Nokia Street","url":"http://{s}.maptile.maps.svc.ovi.com/maptiler/v2/maptile/newest/normal.day/{z}/{x}/{y}/256/png8","subdomains":"bcde","attribution":"Nokia","minZoom":0,"maxZoom":20},
"nokiasat":{"group":"Nokia","name":"Nokia Satellite","url":"http://{s}.maptile.maps.svc.ovi.com/maptiler/v2/maptile/newest/satellite.day/{z}/{x}/{y}/256/png8","subdomains":"bcde","attribution":"Nokia","minZoom":0,"maxZoom":20},
"nokiahybrid":{"group":"Nokia","name":"Nokia Hybrid","url":"http://{s}.maptile.maps.svc.ovi.com/maptiler/v2/maptile/newest/hybrid.day/{z}/{x}/{y}/256/png8","subdomains":"bcde","attribution":"Nokia","minZoom":0,"maxZoom":20},
"nokiaterrain":{"group":"Nokia","name":"Nokia Terrain","url":"http://{s}.maptile.maps.svc.ovi.com/maptiler/v2/maptile/newest/terrain.day/{z}/{x}/{y}/256/png8","subdomains":"bcde","attribution":"Nokia","minZoom":0,"maxZoom":20},
"bingroad":{"group":"Bing","name":"Bing Street","typeBing":"Road","minZoom":0,"maxZoom":18},
"bingaerial":{"group":"Bing","name":"Bing Aerial","typeBing":"Aerial","minZoom":0,"maxZoom":18},
"binghybrid":{"group":"Bing","name":"Bing Hybrid","typeBing":"AerialWithLabels","minZoom":0,"maxZoom":18},
"esristreet":{"group":"ESRI","name":"ESRI Street","url":"http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}.jpg","subdomains":"","attribution":"ESRI","minZoom":0,"maxZoom":19},
"esrinatgeo":{"group":"ESRI","name":"National Geographic","url":"http://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}.jpg","subdomains":"","attribution":"ESRI","minZoom":0,"maxZoom":16},
"esrirelief":{"group":"ESRI","name":"ESRI Shaded Relief","url":"http://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}.jpg","subdomains":"","attribution":"ESRI","minZoom":0,"maxZoom":19},
"esrisatellite":{"group":"ESRI","name":"ESRI Satellite","url":"http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.jpg","subdomains":"","attribution":"ESRI","minZoom":0,"maxZoom":19},
"esritopo":{"group":"ESRI","name":"ESRI Topo","url":"http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.jpg","subdomains":"","attribution":"ESRI","minZoom":0,"maxZoom":19},
"esriterrain":{"group":"ESRI","name":"ESRI Terrain","url":"http://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}.jpg","subdomains":"","attribution":"ESRI","minZoom":0,"maxZoom":19},
"esrilight":{"group":"ESRI","name":"ESRI Light","url":"http://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}.jpg","subdomains":"","attribution":"ESRI","minZoom":0,"maxZoom":19},
"esriocean":{"group":"ESRI","name":"ESRI Ocean","url":"http://server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}.jpg","subdomains":"","attribution":"ESRI","minZoom":0,"maxZoom":19},
"openmapsurfer":{"group":"misc","name":"Open Map Surfer","url":"http://129.206.74.245:8001/tms_r.ashx?x={x}&y={y}&z={z}","subdomains":"","attribution":"Open Map Surfer","minZoom":0,"maxZoom":18},
"avichart":{"group":"misc","name":"Aviation Charts","url":"http://wms.chartbundle.com/tms/1.0.0/sec/{z}/{x}/{y}.png","subdomains":"","attribution":"Chartbundle","minZoom":0,"maxZoom":13},
"argyle":{"group":"misc","name":"Argyle","url":"http://temp{s}.argyl.es/preview-key/{z}/{x}/{y}.jpg","subdomains":"123","attribution":"Nathan Vander Wilt","minZoom":0,"maxZoom":19},
"apple":{"group":"misc","name":"Apple iPhoto","url":"http://gsp2.apple.com/tile?api=1&style=slideshow&layers=default&lang=en_US&z={z}&x={x}&y={y}&v=9","subdomains":"","attribution":"Apple","minZoom":3,"maxZoom":14},
"opnvkarte":{"group":"misc","name":"Öpnvkarte transport","url":"http://tile.xn--pnvkarte-m4a.de/tilegen/{z}/{x}/{y}.png","subdomains":"","attribution":"Öpnvkarte","minZoom":0,"maxZoom":18},
"toolserver":{"group":"misc","name":"Tool Server","url":"http://{s}.www.toolserver.org/tiles/bw-noicons/{z}/{x}/{y}.png","subdomains":"abc","attribution":"Tool Server","minZoom":0,"maxZoom":12},
"opencycle":{"group":"misc","name":"Open Cycle Map","url":"http://{s}.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png","subdomains":"abc","attribution":"Open Cycle Map","minZoom":0,"maxZoom":16},
"openlandscape":{"group":"misc","name":"Open Cycle Map Landscape","url":"http://tile3.opencyclemap.org/landscape/{z}/{x}/{y}.png","subdomains":"","attribution":"Open Cycle Map","minZoom":0,"maxZoom":18},
"opentransport":{"group":"misc","name":"Open Cycle Map Transport","url":"http://tile2.opencyclemap.org/transport/{z}/{x}/{y}.png","subdomains":"","attribution":"Open Cycle Map","minZoom":0,"maxZoom":18}}
"""

tiles = json.loads(tilesets_json)
Theme.objects.all().delete()
Layer.objects.all().delete()

for k,v in tiles.items():
    try:    
        if not v['url']:
            continue

        url = v['url'].replace("{","${")
        theme, created = Theme.objects.get_or_create(name=v['group'],display_name=v['group'])

        if v['subdomains'] != '':
            subdomains = ','.join(list(v['subdomains']))
        else:
            subdomains = None
        layer = Layer.objects.create(name=v['name'], url=url, subdomains=subdomains, 
                layer_type="XYZ", opacity="1.0", source=v['attribution'])
        layer.themes.add(theme)
        layer.save()
    except KeyError:
        pass
