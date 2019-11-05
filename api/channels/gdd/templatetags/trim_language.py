import re
from django import template

register = template.Library()

@register.filter
def trim_language(v):
  return re.sub(r'^(/[^/]*/)', '/', v)
