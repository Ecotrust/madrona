from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse
from django.conf import settings

try:
    use_openid = settings.OPENID_ENABLED
except:
    use_openid = False

urlpatterns = patterns('madrona.user_profile.views',
        url(r'^(?P<username>\w+)/$', 'profile_form', {'use_openid': use_openid}, name="user_profile-form"),
)
