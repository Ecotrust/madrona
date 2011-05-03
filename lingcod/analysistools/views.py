# Create your views here.
from django.http import HttpResponse
from lingcod.features.views import get_object_for_viewing
from lingcod.analysistools.models import Analysis
from lingcod.common import default_mimetypes as mimetypes
from django.utils import simplejson

def progress(request, uid):
    instance = get_object_for_viewing(request, uid)
    if isinstance(instance, HttpResponse):
        return instance

    if issubclass(instance.__class__, Analysis):
        p = instance.progress
        progress = {
            'complete': p[0],
            'total': p[1],
            'html': instance.status_html
        }
        res = HttpResponse(simplejson.dumps(progress))
        res['Content-Type'] = mimetypes.JSON 
        return res

    return HttpResponse("%s is not an analysis!" % (instance), status=500)
