from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from lingcod.screencasts.models import Screencast

from django.conf import settings

def listTutorials(request, screencasts_template='tutorials.html'):
    return render_to_response(screencasts_template, context_instance=RequestContext(request, {'MEDIA_URL':settings.MEDIA_URL, 'screencast_list':Screencast.objects.all()})) 


def showVideo(request, urlname, demo_template='demo_video.html'):
    try:
        screencast = Screencast.objects.get(urlname=urlname)
    except:
        return HttpResponse( "Screencast " + urlname + " does not exist.", status=404 )
    
    return render_to_response(demo_template, {'videoplayer':settings.VIDEO_PLAYER, 'screencast':screencast}, context_instance=RequestContext(request)) 

