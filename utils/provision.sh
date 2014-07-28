#!/bin/bash
## using 12.04

# sudo apt-get update

## PPA not necessary in 14.04
sudo apt-get install -y python-software-properties git
#sudo add-apt-repository ppa:mapnik/v2.2.0
#sudo apt-add-repository ppa:ubuntugis/ppa

#sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev python-dev build-essential libjpeg-dev python-pip \
                        libmapnik libmapnik-dev mapnik-utils python-mapnik \
                        libjpeg8-dev libpng3 libfreetype6-dev postgresql-9.1-postgis-2.0

## in 14.04 postgresql-9.3-postgis-2.1
## in 14.04 python-mapnik mapnik-input-plugin-* mapnik-utils libmapnik2.2 libmapnik2-dev \


sudo pip install --upgrade pip
sudo apt-get install -y python-gdal python-imaging
sudo pip install --allow-all-external --allow-unverified elementtree elementtree
# export CPLUS_INCLUDE_PATH=/usr/include/gdal
# export C_INCLUDE_PATH=/usr/include/gdal
# sudo pip install --allow-external --allow-insecure \
#     --find-links http://wheels2.astropy.org/ --use-wheel \
#     "Cython>=0.16" Numpy "GDAL>=1.10.0" \
#     PIL --allow-external PIL --allow-unverified PIL \
#     --allow-all-external --allow-unverified elementtree elementtree


# IF inside venv, requires virtualenv wrapper
# pip install virtualenvwrapper 
# add2virtualenv /usr/lib/pymodules/python2.7

cd /usr/local/src/madrona
sudo pip install -r requirements.txt
sudo pip install -r requirements-dev.txt
sudo python setup.py develop

sudo -u postgres psql -d template1 -c "CREATE EXTENSION postgis;"
sudo -u postgres psql -d template1 -f madrona/common/sql/cleangeometry.sql
sudo -u postgres dropdb test_project
sudo -u postgres psql -c "DROP ROLE IF EXISTS django"
sudo -u postgres psql -c "CREATE ROLE django WITH PASSWORD 'django' CREATEDB CREATEROLE LOGIN"
# createuser -sdP django
sudo -u postgres createdb -O django test_project