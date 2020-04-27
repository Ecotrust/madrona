from django.conf.urls import url, include
from madrona.manipulators import views
urlpatterns = [
    url(r'^test/$', views.testView),
    url(r'^list/([A-Za-z0-9_,]+)/([A-Za-z0-9_,]+)/$', views.mpaManipulatorList),
    url(r'^([A-Za-z0-9_,]+)/$', views.multi_generic_manipulator_view, name='manipulate'),
    url(r'^', views.multi_generic_manipulator_view, {'manipulators': None}, name='manipulate-blank'),
]
