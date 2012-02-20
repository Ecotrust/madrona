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

* Install Madrona and requirements

    git clone https://perrygeo@github.com/Ecotrust/madrona.git
    pip install -r madrona/madrona_requirements.txt
    cd madrona
    python setup.py develop

* Start your madrona-based project

    cd ~/src
    create-madrona-project.py your_project
    cd your_project
    python manage.py prepsite
    python manage.py runserver

## Learn more

[http://ecotrust.github.com/madrona/docs/](Documentation)
