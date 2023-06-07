from django.urls import re_path
from madrona.manipulators import views
urlpatterns = [
    re_path(r'^test/$', views.testView),
    re_path(r'^list/([A-Za-z0-9_,]+)/([A-Za-z0-9_,]+)/$', views.mpaManipulatorList),
    re_path(r'^([A-Za-z0-9_,]+)/$', views.multi_generic_manipulator_view, name='manipulate'),
    re_path(r'^', views.multi_generic_manipulator_view, {'manipulators': None}, name='manipulate-blank'),
]
