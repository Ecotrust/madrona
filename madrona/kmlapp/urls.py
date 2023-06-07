from django.urls import path, re_path, include
from madrona.kmlapp import views
urlpatterns = [
    re_path(r'^user_features/(?P<session_key>\w+)/(?P<input_username>\w+).kml$',
        views.create_kml, name='kmlapp-user-kml'),
    re_path(r'^user_features/(?P<session_key>\w+)/(?P<input_username>\w+).kmz$',
        views.create_kml, {'kmz': True}, name='kmlapp-user-kmz'),

    re_path(r'^user_features_links/(?P<session_key>\w+)/(?P<input_username>\w+).kml$',
        views.create_kml, {'links': True}, name='kmlapp-userlinks-kml'),
    re_path(r'^user_features_links/(?P<session_key>\w+)/(?P<input_username>\w+).kmz$',
        views.create_kml, {'links': True, 'kmz': True}, name='kmlapp-userlinks-kmz'),

    re_path(r'^feature/(?P<session_key>\w+)/(?P<input_uid>\w+).kml$',
        views.create_kml, name='kmlapp-feature-kml'),
    re_path(r'^feature/(?P<session_key>\w+)/(?P<input_uid>\w+).kmz$',
        views.create_kml, {'kmz': True}, name='kmlapp-feature-kmz'),

    re_path(r'^feature_links/(?P<session_key>\w+)/(?P<input_uid>\w+).kml$',
        views.create_kml, {'links': True}, name='kmlapp-feature-links-kml'),
    re_path(r'^feature_links/(?P<session_key>\w+)/(?P<input_uid>\w+).kmz$',
        views.create_kml, {'links': True, 'kmz': True}, name='kmlapp-feature-links-kmz'),

    re_path(r'^shared_by/(?P<session_key>\w+)/group-(?P<input_sharegroup>\d+)_sharedby-(?P<input_shareuser>\d+).kml$',
        views.create_kml, {'links': True}, name='kmlapp-sharedby-kml'),
    re_path(r'^shared_by/(?P<session_key>\w+)/group-(?P<input_sharegroup>\d+)_sharedby-(?P<input_shareuser>\d+).kmz$', views.create_kml, {'links': True, 'kmz': True}, name='kmlapp-sharedby-kmz'),

    re_path(r'^public/(?P<session_key>\w+)/public.kml$',
        views.shared_public, name='kmlapp-publicshared-kml'),
    re_path(r'^public/(?P<session_key>\w+)/public.kmz$',
        views.shared_public, {'kmz': True}, name='kmlapp-publicshared-kmz'),

    re_path(r'^shared_links/(?P<session_key>\w+)/sharedby-(?P<input_username>\w+).kml$',
        views.create_shared_kml, name='kmlapp-sharedlinks-kml'),
    path(r'shared_links/<str:session_key>/sharedby-<str:input_username>.kmz',
        views.create_shared_kml, {'kmz': True}, name='kmlapp-sharedlinks-kmz'),
]
