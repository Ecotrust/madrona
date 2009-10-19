from lingcod.mpa import models
from manipulators import *

class Mpa(models.Mpa):
    class Options:
        manipulators = [ ClipToStudyRegionManipulator, EastWestManipulator ]
        #manipulators = [ ClipToShapeManipulator ]
        #manipulators = [ ClipToGraticuleManipulator ]

    class Meta(models.Mpa.Meta):
        pass
