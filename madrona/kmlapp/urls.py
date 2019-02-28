from django.conf.urls import url, include
from madrona.kmlapp import views
urlpatterns = [
    url(r'^user_features/(?P<session_key>\w+)/(?P<input_username>\w+).kml$',
        views.create_kml, name='kmlapp-user-kml'),
    url(r'^user_features/(?P<session_key>\w+)/(?P<input_username>\w+).kmz$',
        views.create_kml, {'kmz': True}, name='kmlapp-user-kmz'),

    url(r'^user_features_links/(?P<session_key>\w+)/(?P<input_username>\w+).kml$',
        views.create_kml, {'links': True}, name='kmlapp-userlinks-kml'),
    url(r'^user_features_links/(?P<session_key>\w+)/(?P<input_username>\w+).kmz$',
        views.create_kml, {'links': True, 'kmz': True}, name='kmlapp-userlinks-kmz'),

    url(r'^feature/(?P<session_key>\w+)/(?P<input_uid>\w+).kml$',
        views.create_kml, name='kmlapp-feature-kml'),
    url(r'^feature/(?P<session_key>\w+)/(?P<input_uid>\w+).kmz$',
        views.create_kml, {'kmz': True}, name='kmlapp-feature-kmz'),

    url(r'^feature_links/(?P<session_key>\w+)/(?P<input_uid>\w+).kml$',
        views.create_kml, {'links': True}, name='kmlapp-feature-links-kml'),
    url(r'^feature_links/(?P<session_key>\w+)/(?P<input_uid>\w+).kmz$',
        views.create_kml, {'links': True, 'kmz': True}, name='kmlapp-feature-links-kmz'),

    url(r'^shared_by/(?P<session_key>\w+)/group-(?P<input_sharegroup>\d+)_sharedby-(?P<input_shareuser>\d+).kml$',
        views.create_kml, {'links': True}, name='kmlapp-sharedby-kml'),
    url(r'^shared_by/(?P<session_key>\w+)/group-(?P<input_sharegroup>\d+)_sharedby-(?P<input_shareuser>\d+).kmz$',
        views.create_kml, {'links': True, 'kmz': True}, name='kmlapp-sharedby-kmz'),

    url(r'^public/(?P<session_key>\w+)/public.kml$',
        views.shared_public, name='kmlapp-publicshared-kml'),
    url(r'^public/(?P<session_key>\w+)/public.kmz$',
        views.shared_public, {'kmz': True}, name='kmlapp-publicshared-kmz'),

    url(r'^shared_links/(?P<session_key>\w+)/sharedby-(?P<input_username>\w+).kml$',
        views.create_shared_kml, name='kmlapp-sharedlinks-kml'),
    url(r'^shared_links/(?P<session_key>\w+)/sharedby-(?P<input_username>\w+).kmz$',
        views.create_shared_kml, {'kmz': True}, name='kmlapp-sharedlinks-kmz'),
]
