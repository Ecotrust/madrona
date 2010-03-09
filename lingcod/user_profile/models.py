from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """ Extra information about registered users """
    
    def __unicode__(self):
        return u"UserProfile: %s" % (self.username)
    
    user = models.OneToOneField(User)
    about = models.TextField(blank=True)
