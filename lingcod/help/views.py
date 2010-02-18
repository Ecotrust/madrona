from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings
from lingcod.common import mimetypes
from lingcod.screencasts.models import Screencast
from lingcod.simplefaq.models import *

def get_faqs():
    faq_groups = FaqGroup.objects.all().order_by('importance')
    faqs_by_group = []
    #Build an faq list by group, then by faq.  order them by importance
    for group in faq_groups:
        faq_query = Faq.objects.filter(faq_group__faq_group_name=group.faq_group_name).order_by('importance')
        faqs_by_group.append({'group_obj':group,'group_faqs':faq_query})
    return faqs_by_group

def get_vids():
    return Screencast.objects.filter(selected_for_help=True)

def help(request):
    vids = get_vids()
    faqs = get_faqs()
    return render_to_response('help.html', {'faqs_by_group':faqs, 'screencast_list':vids, 'MEDIA_URL':settings.MEDIA_URL }) 

