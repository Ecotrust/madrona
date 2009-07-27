#!/bin/bash
DB="mm_simple_example"

createdb -T postgis $DB
python manage.py syncdb --noinput
./runpy add_merc.py