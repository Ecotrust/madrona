from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """ Extra information about registered users """
    
    def __unicode__(self):
        return u"UserProfile: %s" % (self.user.username)
    
    user = models.OneToOneField(User)
    about = models.TextField(blank=True)
    fav_color = models.CharField(verbose_name="Favorite Color", blank=True, null=True, max_length=255)

class Foo(models.Model):
    """ Super Extra information about registered users """
    about = models.TextField(blank=True)
    fav_color = models.CharField(verbose_name="Favorite Color", blank=True, null=True, max_length=255)
