from django.http import HttpResponse
from lingcod.common.views import map
from lingcod.bookmarks.models import Bookmark

def lower_first(s):
    return s[0].lower() + s[1:]

def show_bookmark(request, bookmark_id):
    b = Bookmark.objects.get(pk=bookmark_id)
    camera_params = ["Latitude", "Longitude", "Altitude", "Heading", "Tilt", "Roll", "AltitudeMode"]
    get = request.GET.copy()
    for p in camera_params:
        get[p] = b.__dict__[lower_first(p)];
    request.GET = get;
    return map(request)
