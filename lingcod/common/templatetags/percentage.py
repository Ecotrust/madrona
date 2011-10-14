from django import template

register = template.Library()

def percentage(value):
    return '{0:.0%}'.format(value)

register.filter('percentage', percentage)
