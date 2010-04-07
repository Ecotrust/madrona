from django import template
import locale
try:
    #this first command is for the aws servers
    locale.setlocale(locale.LC_ALL, 'en_US')
except:
    #this second command is probably what you'll need on your local machine
    locale.setlocale(locale.LC_ALL, '')
register = template.Library()
 

@register.filter()
def currency(value):
    return locale.currency(float(value), grouping=True)
