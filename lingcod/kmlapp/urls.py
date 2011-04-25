from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.kmlapp.views',
    url(r'^user_features/(?P<session_key>\w+)/(?P<input_username>\w+).kml$', 'create_kml', name='kmlapp-user-kml'),
    url(r'^user_features/(?P<session_key>\w+)/(?P<input_username>\w+).kmz$', 'create_kml', {'kmz': True}, name='kmlapp-user-kmz'),

    url(r'^user_features_links/(?P<session_key>\w+)/(?P<input_username>\w+).kml$', 'create_kml', {'links': True}, name='kmlapp-userlinks-kml'),
    url(r'^user_features_links/(?P<session_key>\w+)/(?P<input_username>\w+).kmz$', 'create_kml', {'links': True, 'kmz': True}, name='kmlapp-userlinks-kmz'),

    url(r'^feature/(?P<session_key>\w+)/(?P<input_uid>\w+).kml$', 'create_kml', name='kmlapp-feature-kml'),
    url(r'^feature/(?P<session_key>\w+)/(?P<input_uid>\w+).kmz$', 'create_kml', {'kmz': True}, name='kmlapp-feature-kmz'),

    url(r'^feature_links/(?P<session_key>\w+)/(?P<input_uid>\w+).kml$', 'create_kml', {'links': True}, name='kmlapp-feature-links-kml'),
    url(r'^feature_links/(?P<session_key>\w+)/(?P<input_uid>\w+).kmz$', 'create_kml', {'links': True, 'kmz': True}, name='kmlapp-feature-links-kmz'),

    url(r'^shared_by/(?P<session_key>\w+)/group-(?P<input_sharegroup>\d+)_sharedby-(?P<input_shareuser>\d+).kml$', 'create_kml', {'links': True}, name='kmlapp-sharedby-kml'),
    url(r'^shared_by/(?P<session_key>\w+)/group-(?P<input_sharegroup>\d+)_sharedby-(?P<input_shareuser>\d+).kmz$', 'create_kml', {'links': True, 'kmz': True}, name='kmlapp-sharedby-kmz'),

    url(r'^public/(?P<session_key>\w+)/public.kml$', 'shared_public', name='kmlapp-publicshared-kml'),
    url(r'^public/(?P<session_key>\w+)/public.kmz$', 'shared_public', {'kmz': True}, name='kmlapp-publicshared-kmz'),

    url(r'^shared_links/(?P<session_key>\w+)/sharedby-(?P<input_username>\w+).kml$', 'create_shared_kml', name='kmlapp-sharedlinks-kml'),
    url(r'^shared_links/(?P<session_key>\w+)/sharedby-(?P<input_username>\w+).kmz$', 'create_shared_kml', {'kmz': True}, name='kmlapp-sharedlinks-kmz'),

)

