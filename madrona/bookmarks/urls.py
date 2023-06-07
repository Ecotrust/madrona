from django.conf.urls import include
from django.urls import reverse, re_path
from madrona.bookmarks import views

urlpatterns = [
    re_path(r'^(?P<bookmark_id>\d+)/$', views.show_bookmark, name="bookmark"),
    re_path(r'^statejson/(?P<bookmark_id>\d+)$', views.bookmark_state_json, name="bookmark-state-json"),
    re_path(r'^tool/$', views.save_tool_bookmark, name="bookmark-tool"),
]
