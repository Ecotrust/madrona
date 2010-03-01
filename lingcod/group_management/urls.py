from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^request/$', 'lingcod.group_management.views.group_request',name="group_management-request" ),
    url(r'^request/sent/$', 'django.views.generic.simple.direct_to_template',{'template': 'group_management/group_request_sent.html'},"group_management-request-sent"),
)
