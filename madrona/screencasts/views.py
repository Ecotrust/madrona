from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render
from madrona.screencasts.models import Screencast, YoutubeScreencast

from django.conf import settings

def listTutorials(request, screencasts_template='tutorials.html'):
    return render(request, screencasts_template, {'MEDIA_URL':settings.MEDIA_URL, 'screencast_list':Screencast.objects.all()}) 

def showVideo(request, urlname, demo_template='demo_video.html'):
    try:
        screencast = Screencast.objects.get(urlname=urlname)
    except:
        return HttpResponse("Screencast " + urlname + " does not exist.", status=404)

    return render(request, demo_template, {'videoplayer':settings.VIDEO_PLAYER, 'screencast':screencast})


def showVideoByPk(request, pk, demo_template='demo_video.html'):
    try:
        screencast = Screencast.objects.get(pk=pk)
    except:
        return HttpResponse("Screencast does not exist.", status=404)

    if not settings.VIDEO_PLAYER:
        return HttpResponse("Server error - VIDEO_PLAYER is not defined.", status=500)

    import os
    player_path = settings.MEDIA_ROOT + "../" + settings.VIDEO_PLAYER
    if not os.path.exists(player_path):
        return HttpResponse("Server error - VIDEO_PLAYER does not exist <br/> should live at %s" % settings.VIDEO_PLAYER, status=500)

    return render(request, demo_template, {'videoplayer':settings.VIDEO_PLAYER, 'screencast':screencast}) 

def showYoutubeVideo(request, pk):
    try:
        screencast = YoutubeScreencast.objects.get(pk=pk)
    except:
        return HttpResponse("Screencast does not exist.", status=404)

    return render(request, 'youtube_video.html', {'screencast':screencast}) 
