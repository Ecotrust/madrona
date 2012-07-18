from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.utils import simplejson
from models import *

def getJson(request):
    json = {
        "state": {
            "activeLayers": []
        },
        "layers": [layer.toDict for layer in Layer.objects.filter(is_sublayer=False)],
        "themes": [theme.toDict for theme in Theme.objects.all()],
        "success": True
    }
    return HttpResponse(simplejson.dumps(json))

