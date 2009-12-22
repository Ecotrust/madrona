import urlparse
from django.template import Library
from django.template.defaulttags import URLNode, url
from django.contrib.sites.models import Site
from django.template import Token
from django.template import Variable
import os

register = Library()

class RelativeURLNode(URLNode):
    
    request_path = None
    
    def render(self, context):
        req = Variable(self.request_path).resolve(context).rpartition('/')[0]
        path = super(RelativeURLNode, self).render(context)
        return os.path.relpath(path, req)

def relurl(parser, token, node_cls=RelativeURLNode):
    """Use like the url templatetag, but provide the request path as the first
    argument and this templatetag will return a relative url."""
    old_token = token
    contents = old_token.split_contents()
    request_path = contents.pop(1)
    new_token = Token(old_token.token_type, ' '.join(contents))
    node_instance = url(parser, new_token)
    node_instance.request_path = request_path
    node = node_cls(view_name=node_instance.view_name,
        args=node_instance.args,
        kwargs=node_instance.kwargs,
        asvar=node_instance.asvar)
    node.request_path = request_path
    return node
        
relurl = register.tag(relurl)