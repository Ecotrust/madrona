"""$Id: category.py 988 2008-03-12 18:22:48Z sa3ruby $"""

__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision: 988 $"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from base import validatorBase
from validators import *

#
# author element.
#
class category(validatorBase):
  def getExpectedAttrNames(self):
    return [(None,u'term'),(None,u'scheme'),(None,u'label')]

  def prevalidate(self):
    self.children.append(True) # force warnings about "mixed" content

    self.validate_required_attribute((None,'term'), nonblank)
    self.validate_optional_attribute((None,'scheme'), rfc3987_full)
    self.validate_optional_attribute((None,'label'), nonhtml)
