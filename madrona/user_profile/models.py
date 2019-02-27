from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """ Extra information about registered users """

    def __unicode__(self):
        return u"UserProfile: %s" % (self.user.username)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(blank=True)
