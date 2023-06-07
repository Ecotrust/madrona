from django.conf.urls import include
from django.urls import reverse, re_path
from django.conf import settings
from madrona.user_profile import views

try:
    use_openid = settings.OPENID_ENABLED
except:
    use_openid = False

urlpatterns = [
        re_path(r'^(?P<username>\w+)/$', views.profile_form, {'use_openid': use_openid}, name="user_profile-form"),
]
