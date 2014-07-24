from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import *
import json

def get_json(request):
    data = {
        "state": {
            "activeLayers": []
        },
        "layers": [layer.toDict for layer in Layer.objects.filter(is_sublayer=False)],
        "themes": [theme.toDict for theme in Theme.objects.all()],
        "success": True
    }
    return HttpResponse(json.dumps(data))

def demo(request):
    context = RequestContext(request)
    return render_to_response('layer_manager/demo.html', context)
