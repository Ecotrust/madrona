from django import template

register = template.Library()

def percentage(decimal, precision=0):
    d = float(decimal)
    format_string = "." + str(precision) + "%"
    return format(d, format_string)

register.filter('percentage', percentage)
