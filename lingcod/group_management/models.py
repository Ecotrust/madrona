from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group

class GroupRequest(models.Model):
    """
    store user's requests for group membership
    """
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    date_requested = models.DateTimeField(auto_now_add=True, verbose_name="Date Requested")
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return "%s requests membership with %s" % (self.user.username, self.group.name)
