# Madrona

## Overview
Madrona is a framework for building
web-based decision support tools for open and participatory spatial 
planning. Madrona offers a simple, flexible and powerful
means of gathering expertise from resource managers, scientists, stakeholders and 
public in a process of collaborative decision making.

Madrona is a python module providing a set of reusable apps for the django web framework. 
Using madrona, one can extend the framework for any
sort of collaborative spatial planning process or decision support tool. 

## Examples

* Oregon MarineMap
* Washingtion Marine Planner
* Bioregional Discovery Tool
* USFWS Watershed Prioritization Tool
* Oregon/Washington Forest Management Scenario Planner

## Developer Quick Start

Install Madrona and requirements into a virtualenv

    cd /usr/local/sites
    mkdir newsite && cd newsite
    wget https://github.com/downloads/Ecotrust/ecotrust.github.com/create-madrona-env
    bash create-madrona-env
    source env/bin/activate

Create a db

    sudo su postgres
    createuser dbuser -s -P 
    exit
    createdb -U dbuser -h localhost -W newsite
    # For postgres 9.1 (for older versions, see the postgis docs)
    psql -d newsite -h localhost -U dbuser -c "CREATE EXTENSION postgis;"

Start your madrona-based project

    create-madrona-project.py -p myproject -a myapp -d myproject.example.com \
      -c "host='localhost' user='dbuser' password='secret' dbname='newsite'"

    cd myproject
    python manage.py runserver

## Learn more

[Documentation](http://ecotrust.github.com/madrona/docs/)
