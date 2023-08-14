from django.template import Library

register = Library()

@register.filter(name='abs')
def absolute(value):
    return abs(value)
