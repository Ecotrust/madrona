from django.conf.urls import url, include
from django.urls import reverse
from django.conf import settings
from madrona.user_profile import views

try:
    use_openid = settings.OPENID_ENABLED
except:
    use_openid = False

urlpatterns = [
        url(r'^(?P<username>\w+)/$', views.profile_form, {'use_openid': use_openid}, name="user_profile-form"),
]
