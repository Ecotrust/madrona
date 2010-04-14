from urlparse import *
from django.template import Library
from django.contrib.sites.models import Site
from django.conf import settings
from django import template

register = Library()

@register.tag(name="absolute_media_url")
def do_absolute_media_url(parser, token):
    """Provides MEDIA_URL, but adds the hostname if necessary
    """
    return AbsoluteMediaUrlNode(settings.MEDIA_URL)
        
class AbsoluteMediaUrlNode(template.Node):
    def __init__(self, media_url):
        self.media_url = media_url

    def render(self, context):
        o = urlparse(self.media_url)
        if o.hostname is None:
            domain = 'http://%s' % (Site.objects.get_current().domain, )
            return "%s" % urljoin(domain, self.media_url)
        else:
            return self.media_url