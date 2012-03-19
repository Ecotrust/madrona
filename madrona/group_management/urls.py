from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    url(r'^request/$', 'madrona.group_management.views.group_request', name="group_management-request"),
    url(r'^request/sent/$', 
        TemplateView.as_view(template_name='group_management/group_request_sent.html'),
        name="group_management-request-sent"),
)
