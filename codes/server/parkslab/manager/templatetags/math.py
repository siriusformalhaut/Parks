from django import template

register = template.Library()

@register.filter(name='minus')
def _minus(value, args):
    return value - args

@register.filter(name='times')
def _times(value, args):
    return value * args
    