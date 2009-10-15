from django.contrib.gis.db import models
from manipulators import *
from lingcod.mpa.models import Mpa
from lingcod.manipulators.manipulators import *

class Mpa(Mpa):
    
    class Options:
        manipulators = [ ClipToStudyRegionManipulator, EastWestManipulator ]
        #manipulators = [ ClipToShapeManipulator ]
        #manipulators = [ ClipToGraticuleManipulator ]

