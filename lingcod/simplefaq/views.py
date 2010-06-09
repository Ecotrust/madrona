from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from lingcod.simplefaq.models import *


def faq(request):
    faq_groups = FaqGroup.objects.all()
    faqs_by_group = []
    #Build an faq list by group, then by faq.  order them by importance
    for group in faq_groups:
        faq_query = Faq.objects.filter(faq_group__faq_group_name=group.faq_group_name).order_by('importance')
        faqs_by_group.append({'group_obj':group,'group_faqs':faq_query})
    return render_to_response('faq.html', {'faqs_by_group':faqs_by_group}, context_instance=RequestContext(request)) 
