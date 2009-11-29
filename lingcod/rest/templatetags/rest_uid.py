from django import template
from django.template import resolve_variable
register = template.Library()
from lingcod.rest.utils import rest_uid
from lingcod.common.utils import get_class

@register.tag(name="rest_uid")
def do_rest_uid(parser, token):
    """Returns a string that is a unique identifier for a given model for
    the REST Framework.
    """
    tokens = token.split_contents()
    if len(tokens) == 2:
        path = tokens[1]
    else:
        raise template.TemplateSyntaxError, "%r tag accepts no more than 1 argument." % token.contents.split()[0]
    model = get_class(path)
    result = rest_uid(model)
    return RestUidNode(result)

class RestUidNode(template.Node):
    def __init__(self, result):
        self.result = result
    
    def render(self, context):
        return self.result