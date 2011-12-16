from django import template

register = template.Library()

def percentage(decimal, precision=0):
    format_string = "." + str(precision) + "%"
    return format(decimal, format_string)

register.filter('percentage', percentage)
