from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns('lingcod.user_profile.views',
    url(r'^(?P<username>\w+)/$', 'profile_form',name="user_profile-form" ),
)
