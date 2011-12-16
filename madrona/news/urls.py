from django.conf.urls.defaults import *
from models import Entry, Tag

entry_dict = {
    'queryset': Entry.objects.filter(is_draft=False),
    'date_field': 'published_on',
}

tag_dict = {
    'queryset': Tag.objects.all(),
}

urlpatterns = patterns('django.views.generic',
    url(r'^/?$', 'date_based.archive_index', entry_dict, name="news-main"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[0-9A-Za-z-]+)/$', 'date_based.object_detail', dict(entry_dict, slug_field='slug', month_format='%m'),name="news-detail"),
    url(r'^about/$', 'simple.direct_to_template', {'template':'news/about.html'}, name='news-about'),
)


