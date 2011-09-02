from django.http import HttpResponse
from lingcod.common.views import map
from lingcod.bookmarks.models import Bookmark
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings
from lingcod.common.utils import get_logger
import datetime
import urlparse

log = get_logger()

def lower_first(s):
    return s[0].lower() + s[1:]

domain = "http://%s" % Site.objects.get_current().domain

def show_bookmark(request, bookmark_id):
    b = Bookmark.objects.get(pk=bookmark_id)
    get = request.GET.copy()
    camera_params = ["Latitude", "Longitude", "Altitude", "Heading", "Tilt", "Roll", "AltitudeMode", 'publicstate']
    for p in camera_params:
        get[p] = b.__dict__[lower_first(p)];
    request.GET = get;
    return map(request)

def save_tool_bookmark(request):
    u, created = User.objects.get_or_create(username=settings.BOOKMARK_ANON_USERNAME)
    p = request.POST
    try:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    except:
        ip = request.META['REMOTE_ADDR']

    # see if they've met the limit for this IP address
    if len(Bookmark.objects.filter(date_created__gt = datetime.datetime.now()-settings.BOOKMARK_ANON_LIMIT[1],
                                   ip=ip)) >= settings.BOOKMARK_ANON_LIMIT[0]:
        log.error(ip + " has exceeded the anonymous bookmark limit")
        return HttpResponse("Bookmark Limit Exceeded. Try again later.", status=404)

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
            publicstate = p['publicstate'])
    b.save()

    url = reverse('bookmark', args=[b.pk])
    absurl = urlparse.urljoin(domain, url)

    return HttpResponse(absurl, status=200)
