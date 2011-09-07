from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns('lingcod.bookmarks.views',
    url(r'^(?P<bookmark_id>\d+)/$', 'show_bookmark', name="bookmark"),
    url(r'^tool/$', 'save_tool_bookmark', name="bookmark-tool"),
)

