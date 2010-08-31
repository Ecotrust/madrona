from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.conf import settings

try:
    use_openid = settings.OPENID_ENABLED
except:
    use_openid = False
print use_openid

urlpatterns = patterns('lingcod.user_profile.views',
        url(r'^(?P<username>\w+)/$', 'profile_form', {'use_openid': use_openid}, name="user_profile-form" ),
)
