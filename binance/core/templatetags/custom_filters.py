from django import template

register = template.Library()


@register.filter
def last_url_path(value, num):
    return value.split('/')[-num - 1]
