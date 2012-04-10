dropdb example -U postgres
createdb example -U postgres
rm -rf my-project 

python ../bin/create-madrona-project.py    \
  --project "My Project" \
  --app testapp \
  --domain "hestia.ecotrust.org:8050" \
  --connection "dbname='example' user='postgres' " \
  --studyregion "SRID=4326;POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))" \
  --aoi "My Areas"  \
  --aoi "My Other Areas"  \
  --folder "Folder for Areas"  \
  --kml "Global Marine|http://ebm.nceas.ucsb.edu/GlobalMarine/kml/marine_model.kml" \
  --superuser
