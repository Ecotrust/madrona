from django.conf import settings
from django.template import Node, Library

register = Library()

@register.simple_tag
def appname():
    try:
        name = settings.APP_NAME
    except AttributeError:
        name = '... settings.APP_NAME ...'
    return str(name)

@register.simple_tag
def help_email():
    try:
        name = settings.HELP_EMAIL
    except AttributeError:
        name = 'help@marinemap.org'
    return str(name)
