from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.utils import simplejson
from models import *

def getJson(request):
    themes = {
        "state": {
	    "activeLayers": []
	},
	"layers": [theme.toDict for theme in Theme.objects.all()],
	"success": True
    }
    return HttpResponse(simplejson.dumps(themes))

