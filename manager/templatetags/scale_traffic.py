from django import template

register = template.Library()


@register.filter
def scale_traffic(traffic):
    return round(traffic/4.5)
