from django import template
register = template.Library()
from lingcod.rest.utils import rest_uid
from lingcod.rest.templatetags.rest_uid import do_rest_uid
from django.conf import settings
from django.template import Token

@register.tag(name="array_uid")
def do_array_uid(parser, token):
    """Returns a string that is a unique identifier for the array model
    """
    return do_rest_uid(parser, Token(token.token_type, "rest_uid %s" % (settings.ARRAY_CLASS, )))