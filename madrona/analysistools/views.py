# Create your views here.
from django.http import HttpResponse
from madrona.features.views import get_object_for_viewing
from madrona.analysistools.models import Analysis
from madrona.common import default_mimetypes as mimetypes
from django.utils import simplejson
from django.shortcuts import render_to_response

from django.views.decorators.cache import never_cache
# set headers to disable all client-side caching
@never_cache
def progress(request, uid):
    instance = get_object_for_viewing(request, uid)
    if isinstance(instance, HttpResponse):
        return instance

    if issubclass(instance.__class__, Analysis):
        p = instance.progress
        progress = {
            'uid': instance.uid,
            'complete': p[0],
            'total': p[1],
            'html': instance.status_html,
            'error': 0
        }
        if 'error' in instance.status_html.lower():
            progress['error'] = 1
        res = HttpResponse(simplejson.dumps(progress))
        res['Content-Type'] = mimetypes.JSON 
        return res

    return HttpResponse("%s is not an analysis!" % (instance), status=500)

def progress_html(request, uid):
    instance = get_object_for_viewing(request, uid)
    if isinstance(instance, HttpResponse):
        return instance

    if issubclass(instance.__class__, Analysis):
        p = instance.progress
        progress = {
            'complete': p[0],
            'total': p[1],
            'done': p[1] == p[0],
            'uid': instance.uid,
            'name': instance.name,
            'html': instance.status_html
        }
        return render_to_response('analysis/progress.html', {'progress': progress})

    return HttpResponse("%s is not an analysis!" % (instance), status=500)
