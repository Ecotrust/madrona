from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from lingcod.data_manager.models import *

def return_active_general_file(request, data_layer_id):
    dl = DataLayer.objects.get(pk=data_layer_id)
    gf = dl.active_generalfile
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachement; filename=%s.xls' % ( 'estuary_spacing' )
    response.write(gf.file.file.read())
    return response
