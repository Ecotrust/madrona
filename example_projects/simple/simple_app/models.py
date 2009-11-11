from lingcod.mpa import models
from lingcod.array.models import MpaArray as BaseArray
from manipulators import *

class Mpa(models.Mpa):
    class Options:
        manipulators = [ ClipToStudyRegionManipulator, EastWestManipulator ]
        #manipulators = [ ClipToShapeManipulator ]
        #manipulators = [ ClipToGraticuleManipulator ]

    class Meta(models.Mpa.Meta):
        db_table = u'simple_mpa'
        pass

class MpaArray(BaseArray):
    pass