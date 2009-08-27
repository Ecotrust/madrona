from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from lingcod.manipulators.manipulators import * 
from manipulators import *

from django.conf import settings
from django.utils import simplejson

import models

def sampleManipulator(request, template_name='common/sample-manipulator.html'):
    return render_to_response(template_name, RequestContext(request,{'api_key':settings.GOOGLE_API_KEY}))
    
def mpaManipulatorList(request):
    """Handler for AJAX mpa manipulators request (from sample-manipulator.html)
    """
    manipulators = models.Mpa.Options.manipulators
    manip_text = [(manipulator.Options.name) for manipulator in manipulators]
    
    return HttpResponse( simplejson.dumps( manip_text ))
    

