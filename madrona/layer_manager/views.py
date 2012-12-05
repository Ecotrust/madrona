from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import *

def get_json(request):
    json = {
        "state": {
            "activeLayers": []
        },
        "layers": [layer.toDict for layer in Layer.objects.filter(is_sublayer=False)],
        "themes": [theme.toDict for theme in Theme.objects.all()],
        "success": True
    }
    return HttpResponse(simplejson.dumps(json))

def demo(request):
    context = RequestContext(request)
    return render_to_response('layer_manager/demo.html', context)
