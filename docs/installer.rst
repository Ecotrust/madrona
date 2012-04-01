``madrona.installer`` - Installer App
=====================================

This app contains several scripts (and eventually a full web-based bootstrapping system) all aimed at automating some common tasks and getting users started quickly.

Install Madrona and requirements into a virtualenv::

    cd /usr/local/sites
    mkdir newsite && cd newsite
    virtualenv env
    source env/bin/activate
    pip install madrona

Create a db::

    sudo su postgres
    createuser dbuser -s -P 
    exit
    createdb -U dbuser -h localhost -W newsite
    # For postgres 9.1 and postgis 2.0 (for older versions, see the postgis docs)
    psql -d newsite -h localhost -U dbuser -c "CREATE EXTENSION postgis;"

Start your madrona-based project::

    create-madrona-project.py -p myproject -a myapp -d myproject.example.com \
    -c "host='localhost' user='dbuser' password='secret' dbname='newsite'"

    cd myproject

    python manage.py runserver
