from urllib import parse as urlparse
from django.template import Library
from django.template.defaulttags import url, URLNode
from django.contrib.sites.models import Site

register = Library()

class AbsoluteURLNode(URLNode):
    def __init__(self, view_name, args, kwargs, asvar):
        super(AbsoluteURLNode, self).__init__(view_name,
            args,
            kwargs,
            None)
        self.abs_asvar = asvar

    def render(self, context):
        path = super(AbsoluteURLNode, self).render(context)
        domain = "http://%s" % Site.objects.get_current().domain
        url = urlparse.urljoin(domain, path)

        if self.abs_asvar:
            context[self.abs_asvar] = url
            return ''
        else:
            return url

def absurl(parser, token):
    """Just like {% url 'urlname' %} but ads the domain of the current site."""
    node_instance = url(parser, token)
    return AbsoluteURLNode(view_name=node_instance.view_name,
        args=node_instance.args,
        kwargs=node_instance.kwargs,
        asvar=node_instance.asvar)

absurl = register.tag(absurl)
