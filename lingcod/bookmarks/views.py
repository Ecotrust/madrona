from django.http import HttpResponse
from lingcod.common.views import map
from lingcod.bookmarks.models import Bookmark
from django.contrib.auth.models import User

def lower_first(s):
    return s[0].lower() + s[1:]

camera_params = ["Latitude", "Longitude", "Altitude", "Heading", "Tilt", "Roll", "AltitudeMode", 'publicstate']

def show_bookmark(request, bookmark_id):
    b = Bookmark.objects.get(pk=bookmark_id)
    get = request.GET.copy()
    for p in camera_params:
        get[p] = b.__dict__[lower_first(p)];
    request.GET = get;
    return map(request)

def save_tool_bookmark(request):
    u, created = User.objects.get_or_create(username="anonymous_bookmark_user")
    p = request.POST
    try:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    except:
        ip = request.META['REMOTE_ADDR']

    b = Bookmark(
            user = u,
            name = "",
            ip = ip,
            description = "",
            latitude = p['Latitude'],
            longitude = p['Longitude'],
            altitude = p['Altitude'],
            heading = p['Heading'],
            tilt = p['Tilt'],
            roll = p['Roll'],
            altitudeMode = p['AltitudeMode'],
            publicstate = p['publicstate']
    )
    b.save()

    return HttpResponse("works", status=200)
