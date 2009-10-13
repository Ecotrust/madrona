from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from lingcod.manipulators.manipulators import * 
from manipulators import *

from django.conf import settings
from django.utils import simplejson

import models

def simpleManipulators(request, template_name='common/simple-manipulators.html'):
    return render_to_response(template_name, RequestContext(request,{'api_key':settings.GOOGLE_API_KEY}))
  

