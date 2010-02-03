from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes
from lingcod.news.models import Entry
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

    if "mm_already_viewed" in request.COOKIES:
        if "mm_last_checked_news" in request.COOKIES:
            try:
                last_checked = datetime.datetime.strptime(request.COOKIES['mm_last_checked_news'], timeformat)
                try:
                    latest_news = Entry.objects.latest('modified_on').modified_on
                except:
                    latest_news = datetime.datetime.now()

                # if theres new news, show it and reset cookie
                if last_checked < latest_news:
                    set_news_cookie = True
                    show_panel = "news"
            except:
                # Datetime cookie is not valid... someone's been messing with the cookies!
                set_news_cookie = True
                show_panel = "news"
        else:
            # haven't checked the news yet OR cleared the cookie
            set_news_cookie = True
            show_panel = "news"
    else:
        # Haven't ever visited MM or cleared their cookies
        set_viewed_cookie = True
        show_panel = "about"
            
    response = render_to_response(template_name, RequestContext(request,{
        'api_key':settings.GOOGLE_API_KEY, 
        'WAVE_ID': settings.WAVE_ID,
        'session_key': request.session.session_key,
        'show_panel': show_panel,
        }))
    
    if set_news_cookie:
        now = datetime.datetime.strftime(datetime.datetime.now(), timeformat)
        response.set_cookie("mm_last_checked_news", now)

    if set_viewed_cookie:
        max_age = 365*24*60*60  #one year
        expire_stamp = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie("mm_already_viewed","True", expires=expire_stamp)

    return response
