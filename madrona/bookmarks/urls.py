from django.conf.urls import url, include
from django.urls import reverse
from madrona.bookmarks import views

urlpatterns = [
    url(r'^(?P<bookmark_id>\d+)/$', views.show_bookmark, name="bookmark"),
    url(r'^statejson/(?P<bookmark_id>\d+)$', views.bookmark_state_json, name="bookmark-state-json"),
    url(r'^tool/$', views.save_tool_bookmark, name="bookmark-tool"),
]
