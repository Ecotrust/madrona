"""$Id: skipHours.py 988 2008-03-12 18:22:48Z sa3ruby $"""

__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision: 988 $"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from base import validatorBase
from validators import text
from logging import *

#
# skipHours element
#
class skipHours(validatorBase):
    
  def __init__(self):
    self.hours = []
    validatorBase.__init__(self)

  def validate(self):
    if "hour" not in self.children:
      self.log(MissingElement({"parent":self.name, "element":"hour"}))
    if len(self.children) > 24:
      self.log(NotEnoughHoursInTheDay({}))

  def do_hour(self):
    return hour()

class hour(text):
  def validate(self):
    try:
      h = int(self.value)
      if h in self.parent.hours or (h in [0,24] and 24-h in self.parent.hours):
        self.log(DuplicateValue({"parent":self.parent.name, "element":self.name, "value":self.value}))
      if (h < 0) or (h > 23):
        raise ValueError
      else:
        self.parent.hours.append(h)
        self.log(ValidHour({"parent":self.parent.name, "element":self.name, "value":self.value}))
    except ValueError:
      if self.value == '24':
        self.log(UseZeroForMidnight({"parent":self.parent.name, "element":self.name, "value":self.value}))
      else:
        self.log(InvalidHour({"parent":self.parent.name, "element":self.name, "value":self.value}))
