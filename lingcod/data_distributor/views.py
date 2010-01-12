from lingcod.data_distributor.models import *
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction

def load_potential_targets_view(request, module='lingcod'):
    if request.user.is_staff:
        load_potential_targets(module=module)
        return HttpResponseRedirect('/admin/data_distributor/potentialtarget/')
    else:
        return HttpResponseForbidden

@transaction.commit_on_success
def run_load_setup(request, load_setup_pk):
    """docstring for run_load_setup"""
    if request.user.is_staff:
        lsu = LoadSetup.objects.get(pk=load_setup_pk)
        target_model = lsu.target_model.the_model
        target_model.objects.all().delete()
        lsu.run_load_setup()
    else:
        return HttpResponseForbidden