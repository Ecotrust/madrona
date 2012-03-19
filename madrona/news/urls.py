from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView
from django.views.generic.dates import ArchiveIndexView, DateDetailView
from models import Entry, Tag

entry_dict = {
    'queryset': Entry.objects.filter(is_draft=False),
    'date_field': 'published_on',
}

tag_dict = {
    'queryset': Tag.objects.all(),
}

urlpatterns = patterns('django.views.generic',
    url(r'^/?$', 
        ArchiveIndexView.as_view(**entry_dict), 
        name="news-main"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[0-9A-Za-z-]+)/$', 
        DateDetailView.as_view(slug_field='slug', month_format='%m', **entry_dict),
        name="news-detail"),
    url(r'^about/$', 
        TemplateView.as_view(template_name='news/about.html'), name='news-about'),
)
