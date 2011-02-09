from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.kmlapp.views',
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/user_features.kml$', 'create_kml', name='kmlapp-user-kml'),
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/user_features.kmz$', 'create_kml', {'kmz': True}, name='kmlapp-user-kmz'),

    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/user_features_links.kml$', 'create_kml', {'links': True}, name='kmlapp-userlinks-kml'),
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/user_features_links.kmz$', 'create_kml', {'links': True, 'kmz': True}, name='kmlapp-userlinks-kmz'),

    url(r'^(?P<session_key>\w+)/(?P<input_collection_uid>\w+)/collection.kml$', 'create_kml', name='kmlapp-collection-kml'),
    url(r'^(?P<session_key>\w+)/(?P<input_collection_uid>\w+)/collection.kmz$', 'create_kml', {'kmz': True}, name='kmlapp-collection-kmz'),

    url(r'^(?P<session_key>\w+)/(?P<input_collection_uid>\w+)/collection_links.kml$', 'create_kml', {'links': True}, name='kmlapp-collection-links-kml'),
    url(r'^(?P<session_key>\w+)/(?P<input_collection_uid>\w+)/collection_links.kmz$', 'create_kml', {'links': True, 'kmz': True}, name='kmlapp-collection-links-kmz'),
# TODO
    url(r'^(?P<session_key>\w+)/(?P<input_mpa_id>\d+)/mpa.kml$', 'create_kml', name='kmlapp-mpa-kml'),
    url(r'^(?P<session_key>\w+)/(?P<input_mpa_id>\d+)/mpa.kmz$', 'create_kml', {'kmz': True}, name='kmlapp-mpa-kmz'),

    url(r'^(?P<session_key>\w+)/(?P<input_sharegroup>\d+)/(?P<input_shareuser>\d+)/shared_by.kml$', 'create_kml', {'links': True}, name='kmlapp-sharedby-kml'),
    url(r'^(?P<session_key>\w+)/(?P<input_sharegroup>\d+)/(?P<input_shareuser>\d+)/shared_by.kmz$', 'create_kml', {'links': True, 'kmz': True}, name='kmlapp-sharedby-kmz'),

    url(r'^(?P<session_key>\w+)/public.kml$', 'shared_public', name='kmlapp-publicshared-kml'),
    url(r'^(?P<session_key>\w+)/public.kmz$', 'shared_public', {'kmz': True}, name='kmlapp-publicshared-kmz'),

    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/shared_links.kml$', 'create_shared_kml', name='kmlapp-sharedlinks-kml'),
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/shared_links.kmz$', 'create_shared_kml', {'kmz': True}, name='kmlapp-sharedlinks-kmz'),

)

