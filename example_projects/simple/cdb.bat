createdb -U postgres -T template_postgis mm_simple_example
python manage.py syncdb --noinput
python add_merc.py