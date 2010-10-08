from django.conf.urls.defaults import *
from lingcod.rest import registered_models

urlpatterns = []
for model in registered_models:
    urlpatterns += patterns('',
        (r'%s/' % (str(model.__name__),), 'lingcod.common.views.forbidden'),
    )
    print "registering url for " + str(model)