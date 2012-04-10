dropdb example -U postgres
createdb example -U postgres
rm -rf my_project 

python ../bin/create-madrona-project.py    \
  --project "My Project" \
  --app testapp \
  --domain "hestia.ecotrust.org:8053" \
  --connection "dbname='example' user='postgres' " \
  --studyregion "SRID=4326;POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))" \
  --aoi "My Areas"  \
  --aoi "My Other Areas"  \
  --poi "Points of interest"  \
  --loi "Pipelines"  \
  --superuser \
  --folder "Folder for Areas"  \
  --kml "http://ebm.nceas.ucsb.edu/GlobalMarine/kml/marine_model.kml" \
  --kml "http://www.geo.uzh.ch/...global/GlobalPermafrostZonationIndexMap.kmz" \
  --kml "http://services.google.com/earth/kmz/realtime_earthquakes_n.kmz" \
  --kml "http://mw2.google.com/mw-earth-vectordb/gallery_website/en/New_York_Times.kml" \
  --kml "http://mw2.google.com/mw-earth-vectordb/gallery_website/en/National_Geographic_Magazine.kml" \
  --kml "http://mw1.google.com/mw-earth-vectordb/outreach/kml3/nl_unep.kml" \
  --kml "http://www.gearthblog.com/kmfiles/gebweather.kmz" \
  --kml "http://earth.google.com/gallery/kmz/forest_cover_change_newsite_n.kmz" \
  --kml "http://mw2.google.com/mw-earth-vectordb/gallery_website/en/earthnc/1/earthnc_noaa_charts.kml" \
  --kml "http://mw1.google.com/mw-earth-vectordb/gallery_website/nl/ocean/Marine_Protected_Areas.kml" \
  --kml "http://mw1.google.com/mw-earth-vectordb/gallery_website/nl/ocean/Human_Impacts.kml" \
  --kml "http://mw1.google.com/mw-earth-vectordb/gallery_website/nl/ocean/Ocean_Atlas.kml" \
  --kml "http://services.google.com/earth/kmz/changing_sea_level_n.kmz" \
  --kml "http://services.google.com/earth/kmz/global_paleogeographic_n.kmz" \
  --kml "http://mw2.google.com/mw-earth-vectordb/gallery_website/kmls/smr-tour.kmz" \
  --kml "http://www.marinetraffic.com/ais/ge_marinetraffic.kml" \
  --kml "http://mw1.google.com/mw-ocean/sio/v7/doc.kml" \
  --kml "http://modata.ceoe.udel.edu/web_kmzs/World%20and%20Regional%20Sea%20Surface%20Temperature.kmz" \
  --kml "http://mw2.google.com/mw-earth-vectordb/gallery_website/en/Rumsey_Historical_Maps.kml" \
  --kml "http://services.google.com/earth/kmz/global_temperatures_n.kmz" \
  --kml "http://services.google.com/earth/kmz/world_population_animation_n.kmz" \
  --kml "http://services.google.com/earth/kmz/jpl_modis_n.kmz" \
  --kml "http://services.google.com/earth/kmz/night_lights_n.kmz" 
