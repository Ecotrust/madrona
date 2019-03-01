from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from madrona.common import default_mimetypes as mimetypes
from madrona.news.models import Entry
from madrona.common.utils import valid_browser
from madrona.features import user_sharing_groups
from madrona.studyregion.models import StudyRegion
from madrona.layers.models import PublicLayerList, PrivateKml
from madrona.layers.views import has_privatekml
from madrona.features.views import has_features
import datetime

from django.conf import settings


def map(request, template_name='common/map_ext.html', extra_context={}):
    """
    Main application window
    Sets/Checks Cookies to determine if user needs to see the about or news panels
    """
    timeformat = "%d-%b-%Y %H:%M:%S"

    set_news_cookie = False
    set_viewed_cookie = False
    show_panel = None

    useragent = request.META['HTTP_USER_AGENT']
    enforce_supported = settings.ENFORCE_SUPPORTED_BROWSER
    if 'supported' in request.REQUEST and request.REQUEST['supported'] == 'false':
            enforce_supported = False
    if enforce_supported and not valid_browser(useragent):
        from madrona.common import uaparser
        bp = uaparser.browser_platform(useragent)
        context = {'useragent':useragent,
                'browser_platform': bp.__repr__(),
                'redirect_url': settings.LOGIN_REDIRECT_URL}
        context.update(extra_context)
        return render_to_response('common/supported_browsers.html', context)

    if "mm_already_viewed" in request.COOKIES:
        if "mm_last_checked_news" in request.COOKIES:
            try:
                last_checked = datetime.datetime.strptime(request.COOKIES['mm_last_checked_news'], timeformat)
                try:
                    latest_news = Entry.objects.latest('modified_on').modified_on
                    # if theres new news, show it and reset cookie
                    if last_checked < latest_news:
                        set_news_cookie = True
                        show_panel = "news"
                except:
                    # no news is good news??
                    pass

            except:
                # Datetime cookie is not valid... someone's been messing with the cookies!
                set_news_cookie = True
                show_panel = "news"
        else:
            # haven't checked the news yet OR cleared the cookie
            set_news_cookie = True
            try:
                latest_news = Entry.objects.latest('modified_on').modified_on
                show_panel = "news"
            except:
                pass
    else:
        # Haven't ever visited MM or cleared their cookies
        set_viewed_cookie = True
        show_panel = "about"

    # Check if the user is a member of any sharing groups (not including public shares)
    member_of_sharing_group = False
    user = request.user
    if user.is_authenticated and user_sharing_groups(user):
        member_of_sharing_group = True

    context = RequestContext(request,{
        'api_key':settings.GOOGLE_API_KEY,
        'session_key': request.session.session_key,
        'show_panel': show_panel,
        'member_of_sharing_group': member_of_sharing_group,
        'is_studyregion': StudyRegion.objects.count() > 0,
        'is_public_layers': PublicLayerList.objects.filter(active=True).count() > 0,
        'is_privatekml': has_privatekml(user),
        'has_features': has_features(user),
        'camera': parse_camera(request),
        'publicstate': get_publicstate(request),
        'bookmarks_as_feature': settings.BOOKMARK_FEATURE,
    })

    context.update(extra_context)
    response = render_to_response(template_name, context)

    if set_news_cookie:
        now = datetime.datetime.strftime(datetime.datetime.now(), timeformat)
        response.set_cookie("mm_last_checked_news", now)

    if set_viewed_cookie:
        max_age = 365 * 24 * 60 * 60  # one year
        expire_stamp = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie("mm_already_viewed","True", expires=expire_stamp)

    return response

def forbidden(request, *args, **kwargs):
    return HttpResponse('Access denied', status=403)

def parse_camera(request):
    camera_params = ["Latitude", "Longitude", "Altitude", "Heading", "Tilt", "Roll", "AltitudeMode"]
    camera = {}
    for p in camera_params:
        try:
            camera[p] = float(request.REQUEST[p])
        except KeyError:
            pass

    if len(camera.keys()) == 0:
        return None
    return camera

def get_publicstate(request):
    try:
        s = request.REQUEST['publicstate']
    except KeyError:
        s = None
    return s

def launch(request, template_name='common/launch.html', extra_context={}):
    """
    Launch screen / Home page for application
    """
    context = {}
    context.update(extra_context)
    return render_to_response(template_name, context)
