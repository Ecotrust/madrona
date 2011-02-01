from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import default_mimetypes as mimetypes
from lingcod.news.models import Entry
from lingcod.common.utils import valid_browser, user_sharing_groups
import datetime

from django.conf import settings


def map(request, template_name='common/map.html'):
    """
    Main application window
    Sets/Checks Cookies to determine if user needs to see the about or news panels
    """
    timeformat = "%d-%b-%Y %H:%M:%S"

    set_news_cookie = False
    set_viewed_cookie = False
    show_panel = None

    useragent = request.META['HTTP_USER_AGENT']
    enforce_supported = True
    if 'supported' in request.REQUEST:
        if request.REQUEST['supported'] == 'false':
            enforce_supported = False
    if not valid_browser(useragent) and enforce_supported:
        from lingcod.common import uaparser
        bp = uaparser.browser_platform(useragent)
        return render_to_response('common/supported_browsers.html', {'useragent':useragent, 'browser_platform': bp.__repr__()})

    if "mm_already_viewed" in request.COOKIES:
        if "mm_last_checked_news" in request.COOKIES:
            try:
                last_checked = datetime.datetime.strptime(request.COOKIES['mm_last_checked_news'], timeformat)
                try:
                    latest_news = Entry.objects.latest('modified_on').modified_on
                    print latest_news
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
    # 
    # # Check if user has a single active UserLayerList
    # from lingcod.layers.models import UserLayerList
    # user = request.user
    # user_layers = False
    # if user.is_authenticated():
    #     try:
    #         UserLayerList.objects.get(user=user.id, active=True)
    #         user_layers = True
    #     except:
    #         pass
            
    # Check if the user is a member of any sharing groups (not including public shares)
    member_of_sharing_group = False
    user = request.user
    if user.is_authenticated() and len(user_sharing_groups(user)) > 0:
        member_of_sharing_group = True
    
    response = render_to_response(template_name, RequestContext(request,{
        'api_key':settings.GOOGLE_API_KEY, 
        'session_key': request.session.session_key,
        'show_panel': show_panel,
        'member_of_sharing_group': member_of_sharing_group,
        #'user_layers': user_layers,
        }))
    
    if set_news_cookie:
        now = datetime.datetime.strftime(datetime.datetime.now(), timeformat)
        response.set_cookie("mm_last_checked_news", now)

    if set_viewed_cookie:
        max_age = 365*24*60*60  #one year
        expire_stamp = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie("mm_already_viewed","True", expires=expire_stamp)

    return response

def forbidden(request, *args, **kwargs):
    return HttpResponse('Access denied', status=403)
