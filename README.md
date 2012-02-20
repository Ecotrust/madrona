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

    cd /usr/local/apps
    mkdir newapp && cd newapp
    wget https://github.com/downloads/Ecotrust/madrona/create-madrona-env
    bash create-madrona-env
    source env/bin/activate

Start your madrona-based project

    create-madrona-project.py your_project
    cd your_project
    python manage.py prepsite
    python manage.py runserver

## Learn more

[Documentation](http://ecotrust.github.com/madrona/docs/)
