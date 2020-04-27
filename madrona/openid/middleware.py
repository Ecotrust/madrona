# -*- coding: utf-8 -*-
# Copyright 2007, 2008,2009 by Benoît Chesneau <benoitc@e-engura.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from madrona.openid.utils.mimeparse import best_match
from django.http import HttpResponseRedirect
from django.urls import reverse

from madrona.openid.models import UserAssociation
from madrona.openid.views import xrdf
from madrona.common.utils import get_logger

__all__ = ["OpenIDMiddleware"]
log = get_logger()

class OpenIDMiddleware(object):
    """
    Populate request.openid. This comes either from cookie or from
    session, depending on the presence of OPENID_USE_SESSIONS. MP- HUH? I dont see that setting used anywhere
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        request.openid = request.session.get('openid', None)
        request.openids = request.session.get('openids', [])

        # The code below seems benign and perfectly understandable (just grabs the openids and attaches a list to the request object)
        # But for some unknown reason, this filter interacts with sessions in such a way that
        # load_sessions fails to work on requests from the GE plugin
        #
        # Not sure what the implications are for excluding it but we shall see
        #
        #rels = UserAssociation.objects.filter(user__id=request.user.id)
        rels = []
        request.associated_openids = [rel.openid_url for rel in rels]

    def process_response(self, request, response):
        if response.status_code != 200 or (hasattr(response, 'content') and len(response.content) < 200):
            return response
        path = request.get_full_path()
        if path == "/" and 'HTTP_ACCEPT' in request.META and \
                best_match(['text/html', 'application/xrds+xml'],
                    request.META['HTTP_ACCEPT']) == 'application/xrds+xml':
            response = xrdf(request)
        return response
